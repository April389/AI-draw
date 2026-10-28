"""
Prompt工程模块
定义结构化的System Prompt和各类图表的生成指引
通过Prompt约束LLM输出符合JSON Schema的结构化数据
"""
from typing import Optional, Dict


# ==================== 图数据的JSON Schema定义 ====================
# 用于在Prompt中告知LLM输出格式要求

DIAGRAM_JSON_SCHEMA = r'''{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["diagram_type", "nodes"],
  "properties": {
    "diagram_type": {
      "type": "string",
      "enum": ["flowchart", "architecture", "sequence", "mindmap", "state", "class", "generic"],
      "description": "图表类型"
    },
    "title": {
      "type": "string",
      "description": "图表标题，简短描述"
    },
    "nodes": {
      "type": "array",
      "minItems": 1,
      "description": "节点列表",
      "items": {
        "type": "object",
        "required": ["id", "label"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-zA-Z0-9_]+$", "description": "唯一标识"},
          "label": {"type": "string", "description": "显示文本"},
          "type": {
            "type": "string",
            "enum": ["rectangle", "ellipse", "diamond", "cylinder", "parallelogram", "cloud", "hexagon"],
            "default": "rectangle",
            "description": "节点形状"
          },
          "x": {"type": "number", "description": "X坐标(可选)"},
          "y": {"type": "number", "description": "Y坐标(可选)"},
          "width": {"type": "number", "description": "宽度(可选)"},
          "height": {"type": "number", "description": "高度(可选)"},
          "color": {"type": "string", "description": "填充颜色如#FFD6A5"},
          "stroke_color": {"type": "string", "description": "边框颜色如#000000"}
        }
      }
    },
    "edges": {
      "type": "array",
      "description": "连线列表",
      "items": {
        "type": "object",
        "required": ["id", "source", "target"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-zA-Z0-9_]+$"},
          "source": {"type": "string", "description": "起始节点ID"},
          "target": {"type": "string", "description": "目标节点ID"},
          "label": {"type": "string", "description": "连线上的标签(可选)"},
          "style": {
            "type": "string",
            "enum": ["solid", "dashed", "dotted"],
            "default": "solid"
          },
          "arrow": {
            "type": "string",
            "enum": ["none", "start", "end", "both"],
            "default": "end"
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "附加元数据（可选）"
    }
  }
}'''


# ==================== System Prompt ====================

SYSTEM_PROMPT_BASE = f"""你是一个专业的图表设计助手。你的任务是将用户的自然语言描述转换为结构化的图表数据。

## 输出要求
你必须且只能输出符合以下JSON Schema的JSON对象，不要输出任何其他文字、Markdown代码块标记或解释：

{DIAGRAM_JSON_SCHEMA}

## 各图表类型的设计指引

### 流程图 (flowchart)
- 使用rectangle表示普通步骤
- 开始/结束使用ellipse（圆角）
- 判断/决策使用diamond（菱形）
- 输入/输出使用parallelogram
- 连线表示步骤间的顺序或分支关系

### 架构图 (architecture)
- 用rectangle表示组件、服务、模块
- 不同层级的组件使用不同颜色区分（如前端/后端/数据库）
- 用cylinder表示数据库
- 用cloud表示外部服务/网络
- 连线表示依赖或调用关系

### 时序图 (sequence)
- 节点表示参与者/对象
- 使用x坐标排列参与者（从左到右）
- edges的label表示消息/方法调用

### 思维导图 (mindmap)
- 所有节点组成层级结构
- 根节点在中心
- 子节点通过edges连接到父节点

### 状态图 (state)
- 状态用rectangle或ellipse表示
- 转换箭头用edges表示
- 初始状态用ellipse标记

### 类图 (class)
- 每个节点表示一个类
- edges表示类之间的关系（继承、组合、依赖）

## 通用规则
1. 节点ID必须是唯一的英文标识符，如node1, process_A
2. label要简洁明了，控制在15字以内
3. 合理选择节点形状以增强可读性
4. 颜色使用十六进制格式如#FFD6A5、#95C2F6
5. 如果用户没有指定图表类型，根据描述自动推断最合适的类型
6. 至少生成1个节点，复杂描述可生成5-15个节点
7. 确保所有edge的source和target都指向已存在的节点ID"""


def build_user_prompt(
    user_input: str,
    diagram_type: Optional[str] = None
) -> str:
    """
    构建发送给LLM的用户Prompt
    
    Args:
        user_input: 用户的自然语言描述
        diagram_type: 指定的图表类型（可选）
    
    Returns:
        完整的用户Prompt
    """
    prompt_parts = [f"请根据以下描述生成图表：\n\n{user_input}"]
    
    if diagram_type:
        type_hint = {
            "flowchart": "流程图",
            "architecture": "架构图", 
            "sequence": "时序图",
            "mindmap": "思维导图",
            "state": "状态图",
            "class": "类图",
            "generic": "通用图"
        }.get(diagram_type, diagram_type)
        prompt_parts.append(f"\n请生成【{type_hint}】类型的图表。")
    
    prompt_parts.append("""

现在请直接输出符合JSON Schema的JSON对象：""")
    
    return "\n".join(prompt_parts)


def get_system_prompt() -> str:
    """获取系统Prompt"""
    return SYSTEM_PROMPT_BASE
