"""
FastAPI主应用
提供图表生成、验证、转换等API端点
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from config import get_settings
from schemas import (
    GenerateRequest,
    GenerateResponse,
    ValidateRequest,
    ValidateResponse,
    HealthResponse,
    DiagramData,
    DiagramType
)
from prompt_templates import build_user_prompt, get_system_prompt
from schema_validator import parse_llm_response, full_validate
from llm_client import create_llm_client, BaseLLMClient
from graph_converter import convert_to_excalidraw

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# 初始化FastAPI
app = FastAPI(
    title="智能绘图系统 API",
    description="基于大语言模型的智能矢量图表生成服务，支持流程图、架构图、时序图等",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm_client() -> BaseLLMClient:
    """
    获取LLM客户端依赖
    
    首次调用时创建并缓存实例
    """
    if not hasattr(app.state, "llm_client"):
        app.state.llm_client = create_llm_client(mock=False)
    return app.state.llm_client


# ==================== API端点 ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_diagram(
    request: GenerateRequest,
    llm_client: BaseLLMClient = Depends(get_llm_client)
):
    """
    根据自然语言描述生成图表
    
    流程:
    1. 构建Prompt
    2. 调用LLM
    3. 解析并校验JSON输出
    4. 转换为Excalidraw格式
    5. 返回结果
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] 收到生成请求: prompt='{request.prompt[:50]}...', type={request.diagram_type}")
    
    try:
        # 1. 构建Prompt
        system_prompt = get_system_prompt()
        user_prompt = build_user_prompt(
            request.prompt,
            request.diagram_type.value if request.diagram_type else None
        )
        
        # 2. 调用LLM
        logger.info(f"[{request_id}] 调用LLM模型: {settings.llm_model}")
        raw_response = llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        logger.info(f"[{request_id}] LLM返回原始长度: {len(raw_response)}")
        
        # 3. 解析并校验
        success, data, errors = parse_llm_response(raw_response)
        
        if not success:
            # 即使校验失败，也尝试转换和返回部分结果
            logger.warning(f"[{request_id}] 数据校验存在问题: {errors}")
            if not data:
                return GenerateResponse(
                    success=False,
                    error=f"生成失败: {'; '.join(errors)}"
                )
        
        # 4. 转换为Excalidraw格式
        try:
            excalidraw_elements = convert_to_excalidraw(data)
        except Exception as e:
            logger.error(f"[{request_id}] 转换Excalidraw格式失败: {e}")
            excalidraw_elements = []
        
        # 5. 构造返回
        diagram_data = DiagramData(**data)
        
        logger.info(f"[{request_id}] 成功生成 {diagram_data.diagram_type.value}，"
                    f"节点数={len(diagram_data.nodes)}, 边数={len(diagram_data.edges)}")
        
        return GenerateResponse(
            success=True,
            diagram=diagram_data,
            excalidraw_elements=excalidraw_elements
        )
        
    except Exception as e:
        logger.exception(f"[{request_id}] 生成过程出错: {e}")
        return GenerateResponse(
            success=False,
            error=f"生成失败: {str(e)}"
        )


@app.post("/api/validate", response_model=ValidateResponse)
async def validate_diagram(request: ValidateRequest):
    """
    校验图数据结构是否正确
    
    检查:
    - JSON Schema符合性
    - 节点ID唯一性
    - 边引用有效性
    - 孤立节点等警告
    """
    valid, errors, warnings = full_validate(request.diagram.model_dump())
    return ValidateResponse(
        valid=valid,
        errors=errors,
        warnings=warnings
    )


@app.post("/api/convert")
async def convert_to_excalidraw_api(request: DiagramData):
    """
    将内部图格式转换为Excalidraw元素格式
    
    前端可上传图数据，后端返回可直接加载到Excalidraw的元素列表
    """
    try:
        elements = convert_to_excalidraw(request.model_dump())
        return {
            "success": True,
            "elements": elements,
            "count": len(elements)
        }
    except Exception as e:
        logger.exception("转换失败")
        raise HTTPException(
            status_code=400,
            detail=f"转换失败: {str(e)}"
        )


@app.get("/api/diagram-types")
async def list_diagram_types():
    """列出支持的图表类型"""
    return {
        "types": [
            {"value": "flowchart", "label": "流程图", "description": "步骤、决策、分支的有序流程"},
            {"value": "architecture", "label": "架构图", "description": "系统组件及其关系"},
            {"value": "sequence", "label": "时序图", "description": "对象间的消息交互时序"},
            {"value": "mindmap", "label": "思维导图", "description": "层级化的概念结构"},
            {"value": "state", "label": "状态图", "description": "对象的状态转换"},
            {"value": "class", "label": "类图", "description": "面向对象的类结构"},
            {"value": "generic", "label": "通用图", "description": "不受类型限制的自由图表"}
        ]
    }


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info(f"智能绘图系统 API v{app.version} 启动中...")
    logger.info(f"LLM模型: {settings.resolved_model} (提供商: {settings.provider_description})")
    logger.info(f"API端点: {settings.resolved_base_url}")
    # 预热LLM客户端
    try:
        client = get_llm_client()
        logger.info(f"LLM客户端已初始化: {type(client).__name__}")
    except Exception as e:
        logger.warning(f"LLM客户端初始化异常: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("智能绘图系统 API 已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
