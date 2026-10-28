"""
JSON Schema校验模块
负责校验LLM输出是否符合预定义的JSON Schema
"""
import json
import re
from typing import Any, Dict, List, Tuple
import jsonschema
from jsonschema import validate, ValidationError


# 精简版的运行时Schema（用于校验）
RUNTIME_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["diagram_type", "nodes"],
    "properties": {
        "diagram_type": {
            "type": "string",
            "enum": ["flowchart", "architecture", "sequence", "mindmap", "state", "class", "generic"]
        },
        "title": {"type": "string"},
        "nodes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["rectangle", "ellipse", "diamond", "cylinder", 
                                 "parallelogram", "cloud", "hexagon"]
                    },
                    "x": {"type": ["number", "null"]},
                    "y": {"type": ["number", "null"]},
                    "width": {"type": ["number", "null"]},
                    "height": {"type": ["number", "null"]},
                    "color": {"type": ["string", "null"]},
                    "stroke_color": {"type": ["string", "null"]}
                }
            }
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "source", "target"],
                "properties": {
                    "id": {"type": "string"},
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "label": {"type": ["string", "null"]},
                    "style": {"type": "string", "enum": ["solid", "dashed", "dotted"]},
                    "arrow": {"type": "string", "enum": ["none", "start", "end", "both"]}
                }
            }
        },
        "metadata": {"type": ["object", "null"]}
    }
}


def extract_json_from_text(text: str) -> str:
    """
    从LLM输出中提取JSON字符串
    
    LLM可能在JSON前后添加Markdown代码块标记或解释文字，
    此函数尝试从中提取纯JSON部分。
    """
    text = text.strip()
    
    # 尝试匹配Markdown代码块
    code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
    if code_block_match:
        return code_block_match.group(1)
    
    # 找到第一个 { 和最后一个 }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1]
    
    return text


def parse_llm_response(raw_text: str) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    解析LLM原始输出并校验
    
    Args:
        raw_text: LLM返回的原始文本
    
    Returns:
        (是否成功, 解析后的数据, 错误信息列表)
    """
    errors: List[str] = []
    
    # 1. 提取JSON
    json_str = extract_json_from_text(raw_text)
    
    # 2. 解析JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        errors.append(f"JSON解析失败: {str(e)}")
        # 尝试修复常见问题
        fixed = _try_fix_json(json_str)
        if fixed:
            try:
                data = json.loads(fixed)
            except json.JSONDecodeError:
                return False, {}, errors
        else:
            return False, {}, errors
    
    # 3. JSON Schema校验
    try:
        validate(instance=data, schema=RUNTIME_SCHEMA)
    except ValidationError as e:
        errors.append(f"Schema校验失败: {e.message} at {list(e.path)}")
        return False, data, errors
    
    # 4. 业务逻辑校验
    business_errors = _validate_business_logic(data)
    errors.extend(business_errors)
    
    if errors:
        return len(business_errors) == 0, data, errors
    
    return True, data, errors


def _try_fix_json(text: str) -> str:
    """尝试修复常见的JSON格式问题"""
    try:
        # 去除注释
        fixed = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        # 去除尾部逗号
        fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
        json.loads(fixed)  # 验证是否有效
        return fixed
    except json.JSONDecodeError:
        return ""


def _validate_business_logic(data: Dict[str, Any]) -> List[str]:
    """
    业务逻辑校验
    
    检查:
    - edge的source/target是否指向存在的node
    - node id是否唯一
    - edge id是否唯一
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    # 检查节点ID唯一性
    node_ids = [n.get("id") for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("存在重复的节点ID")
    
    # 检查边ID唯一性
    edge_ids = [e.get("id") for e in edges]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("存在重复的边ID")
    
    # 检查边引用有效性
    node_id_set = set(node_ids)
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and source not in node_id_set:
            errors.append(f"边 {edge.get('id')} 的 source='{source}' 不存在于节点列表")
        if target and target not in node_id_set:
            errors.append(f"边 {edge.get('id')} 的 target='{target}' 不存在于节点列表")
    
    return errors


def full_validate(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    完整校验，返回(valid, errors, warnings)
    
    用于 /api/validate 端点
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # Schema校验
    try:
        validate(instance=data, schema=RUNTIME_SCHEMA)
    except ValidationError as e:
        errors.append(f"Schema校验失败: {e.message}")
        return False, errors, warnings
    
    # 业务校验
    biz_errors = _validate_business_logic(data)
    errors.extend(biz_errors)
    
    # 额外警告
    node_ids = [n.get("id") for n in data.get("nodes", [])]
    if len(node_ids) < 2:
        warnings.append("建议至少包含2个节点以形成有意义的图表")
    
    # 检查是否有孤立节点（没有任何边连接）
    if data.get("edges"):
        connected_ids = set()
        for e in data["edges"]:
            connected_ids.add(e.get("source"))
            connected_ids.add(e.get("target"))
        isolated = [nid for nid in node_ids if nid not in connected_ids]
        if isolated:
            warnings.append(f"以下节点未被任何边连接: {isolated}")
    
    return len(errors) == 0, errors, warnings
