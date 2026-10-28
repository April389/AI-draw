"""
Pydantic数据模型
定义请求/响应的数据结构以及图的核心数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class DiagramType(str, Enum):
    """支持的图表类型"""
    FLOWCHART = "flowchart"        # 流程图
    ARCHITECTURE = "architecture"  # 架构图
    SEQUENCE = "sequence"          # 时序图
    MINDMAP = "mindmap"            # 思维导图
    STATE = "state"                # 状态图
    CLASS = "class"                # 类图
    GENERIC = "generic"            # 通用图


# ==================== 图的核心数据模型（LLM输出格式） ====================

class Node(BaseModel):
    """图节点"""
    id: str = Field(..., description="节点唯一标识")
    label: str = Field(..., description="节点显示文本")
    type: str = Field(default="rectangle", description="节点形状: rectangle/ellipse/diamond/cylinder/parallelogram")
    x: Optional[float] = Field(default=None, description="X坐标（可选，不指定则自动布局）")
    y: Optional[float] = Field(default=None, description="Y坐标")
    width: Optional[float] = Field(default=None, description="宽度")
    height: Optional[float] = Field(default=None, description="高度")
    color: Optional[str] = Field(default=None, description="填充颜色")
    stroke_color: Optional[str] = Field(default=None, description="边框颜色")


class Edge(BaseModel):
    """图边/连线"""
    id: str = Field(..., description="边唯一标识")
    source: str = Field(..., description="起始节点ID")
    target: str = Field(..., description="目标节点ID")
    label: Optional[str] = Field(default=None, description="连线标签")
    style: str = Field(default="solid", description="连线样式: solid/dashed/dotted")
    arrow: str = Field(default="both", description="箭头方向: none/start/end/both")


class DiagramData(BaseModel):
    """LLM输出的完整图数据"""
    diagram_type: DiagramType = Field(..., description="图表类型")
    title: Optional[str] = Field(default=None, description="图表标题")
    nodes: List[Node] = Field(..., description="节点列表")
    edges: List[Edge] = Field(default_factory=list, description="边列表")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="附加元数据")


# ==================== API请求/响应模型 ====================

class GenerateRequest(BaseModel):
    """生成图表请求"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="用户自然语言描述")
    diagram_type: Optional[DiagramType] = Field(default=None, description="指定图表类型（可选，自动推断）")
    stream: Optional[bool] = Field(default=False, description="是否流式输出")


class GenerateResponse(BaseModel):
    """生成图表响应"""
    success: bool = Field(..., description="是否成功")
    diagram: Optional[DiagramData] = Field(default=None, description="生成的图数据")
    excalidraw_elements: Optional[List[Dict[str, Any]]] = Field(default=None, description="Excalidraw兼容元素列表")
    error: Optional[str] = Field(default=None, description="错误信息")


class ValidateRequest(BaseModel):
    """验证图数据请求"""
    diagram: DiagramData


class ValidateResponse(BaseModel):
    """验证响应"""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
