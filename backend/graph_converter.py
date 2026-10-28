"""
图数据转换器
将内部图数据模型转换为Excalidraw可识别的元素格式
Excalidraw元素格式参考: https://docs.excalidraw.com/docs/codebase/files/element
"""
import uuid
import math
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict


# ==================== 节点形状到Excalidraw元素类型的映射 ====================
NODE_TYPE_MAP = {
    "rectangle": "rectangle",
    "ellipse": "ellipse",
    "diamond": "diamond",
    "parallelogram": "rectangle",  # Excalidraw无平行四边形，用rectangle近似
    "cylinder": "rectangle",       # Excalidraw无圆柱体，用rectangle近似
    "cloud": "rectangle",          # Excalidraw无云形状
    "hexagon": "rectangle",
}

# 默认节点尺寸（如果LLM未指定）
DEFAULT_NODE_SIZES = {
    "rectangle": (140, 60),
    "ellipse": (120, 60),
    "diamond": (100, 100),
    "parallelogram": (140, 60),
    "cylinder": (100, 80),
    "cloud": (160, 80),
    "hexagon": (120, 80),
}


def _gen_excalidraw_id() -> str:
    """生成Excalidraw兼容的元素ID"""
    return uuid.uuid4().hex[:22]


def _auto_layout(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    简单的自动布局算法
    按图的层级结构从左到右排列节点
    
    采用拓扑排序+层级分配的方式
    """
    # 构建邻接表
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    node_map = {n["id"]: n for n in nodes}
    
    for edge in edges:
        src, tgt = edge["source"], edge["target"]
        adj[src].append(tgt)
        in_degree[tgt] += 1
    
    # 找到所有根节点（无入边）
    roots = [nid for nid in node_map if in_degree[nid] == 0]
    
    # BFS分层
    layers = defaultdict(list)
    visited = set()
    queue = [(root, 0) for root in roots]
    
    while queue:
        node_id, layer = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        layers[layer].append(node_id)
        
        for neighbor in adj[node_id]:
            if neighbor not in visited:
                queue.append((neighbor, layer + 1))
    
    # 处理孤立节点
    for nid in node_map:
        if nid not in visited:
            layers[max(layers.keys(), default=-1) + 1].append(nid)
    
    # 计算坐标
    HORIZONTAL_GAP = 280
    VERTICAL_GAP = 150
    START_X = 100
    START_Y = 100
    
    for layer, node_ids in layers.items():
        total_height = len(node_ids) * VERTICAL_GAP
        start_y = START_Y + max(0, (800 - total_height) / 2)
        
        for idx, nid in enumerate(node_ids):
            node = node_map[nid]
            if node.get("x") is None:
                node["x"] = START_X + layer * HORIZONTAL_GAP
            if node.get("y") is None:
                node["y"] = start_y + idx * VERTICAL_GAP
    
    return nodes


def _node_to_excalidraw(node: Dict[str, Any]) -> Dict[str, Any]:
    """将内部节点转换为Excalidraw元素"""
    node_type = node.get("type", "rectangle")
    exc_type = NODE_TYPE_MAP.get(node_type, "rectangle")
    
    width = node.get("width") or DEFAULT_NODE_SIZES.get(node_type, (140, 60))[0]
    height = node.get("height") or DEFAULT_NODE_SIZES.get(node_type, (140, 60))[1]
    
    element = {
        "id": _gen_excalidraw_id(),
        "type": exc_type,
        "x": node.get("x", 100),
        "y": node.get("y", 100),
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": node.get("stroke_color", "#1e1e1e"),
        "backgroundColor": node.get("color", "#ffffff"),
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 3} if exc_type == "rectangle" else None,
        "seed": hash(node.get("id", "")) % 2147483647,
        "version": 1,
        "versionNonce": uuid.uuid4().int % 2147483647,
        "isDeleted": False,
        "boundElements": [],
        "updated": 0,
        "link": None,
        "locked": False,
    }
    
    # 如果有label，创建一个文本元素
    label_text = node.get("label")
    elements = [element]
    
    if label_text:
        text_element = {
            "id": _gen_excalidraw_id(),
            "type": "text",
            "x": node.get("x", 100) + 10,
            "y": node.get("y", 100) + height / 2 - 15,
            "width": len(label_text) * 14 + 20,
            "height": 30,
            "angle": 0,
            "strokeColor": node.get("stroke_color", "#1e1e1e"),
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": hash(f"text_{node.get('id', '')}") % 2147483647,
            "version": 1,
            "versionNonce": uuid.uuid4().int % 2147483647,
            "isDeleted": False,
            "boundElements": None,
            "updated": 0,
            "link": None,
            "locked": False,
            "text": label_text,
            "fontSize": 20,
            "fontFamily": 5,  # Comic Sans
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": 25,
            "containerId": None,
            "originalText": label_text,
            "lineHeight": 1.25,
        }
        elements.append(text_element)
    
    return elements


def _edge_to_excalidraw(
    edge: Dict[str, Any], 
    node_id_to_excalidraw: Dict[str, str],
    nodes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """将内部边转换为Excalidraw箭头元素"""
    # 找到source和target对应的Excalidraw元素ID
    source_node_id = edge["source"]
    target_node_id = edge["target"]
    
    # 计算连接点位置
    source_node = next((n for n in nodes if n["id"] == source_node_id), None)
    target_node = next((n for n in nodes if n["id"] == target_node_id), None)
    
    # 计算节点边界点
    def get_edge_point(
        from_node: Optional[Dict[str, Any]], 
        to_node: Optional[Dict[str, Any]]
    ) -> Tuple[float, float]:
        if not from_node or not to_node:
            return 0, 0
        
        fw = from_node.get("width") or DEFAULT_NODE_SIZES.get(
            from_node.get("type", "rectangle"), (140, 60)
        )[0]
        fh = from_node.get("height") or DEFAULT_NODE_SIZES.get(
            from_node.get("type", "rectangle"), (140, 60)
        )[1]
        
        fx = from_node.get("x", 100)
        fy = from_node.get("y", 100)
        tw = to_node.get("width") or DEFAULT_NODE_SIZES.get(
            to_node.get("type", "rectangle"), (140, 60)
        )[0]
        th = to_node.get("height") or DEFAULT_NODE_SIZES.get(
            to_node.get("type", "rectangle"), (140, 60)
        )[1]
        tx = to_node.get("x", 100)
        ty = to_node.get("y", 100)
        
        # 计算方向向量
        dx = tx + tw/2 - (fx + fw/2)
        dy = ty + th/2 - (fy + fh/2)
        
        # 归一化
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return fx + fw/2, fy + fh/2
        
        dx /= length
        dy /= length
        
        # 从中心到边界的距离
        hw = fw / 2
        hh = fh / 2
        
        # 找到碰撞点
        scale = min(
            abs(hw / dx) if dx != 0 else float('inf'),
            abs(hh / dy) if dy != 0 else float('inf')
        )
        
        return fx + fw/2 + dx * scale, fy + fh/2 + dy * scale
    
    x1, y1 = get_edge_point(source_node, target_node)
    x2, y2 = get_edge_point(target_node, source_node)
    
    # 箭头设置
    arrow_setting = edge.get("arrow", "end")
    start_arrow = "arrow" if arrow_setting in ("start", "both") else None
    end_arrow = "arrow" if arrow_setting in ("end", "both") else None
    
    # 连线样式
    stroke_style = edge.get("style", "solid")
    if stroke_style == "dashed":
        excali_stroke_style = 2
    elif stroke_style == "dotted":
        excali_stroke_style = 3
    else:
        excali_stroke_style = 1
    
    arrow_element = {
        "id": _gen_excalidraw_id(),
        "type": "arrow",
        "x": 0,
        "y": 0,
        "width": abs(x2 - x1) or 1,
        "height": abs(y2 - y1) or 1,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": excali_stroke_style,
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": hash(edge.get("id", "")) % 2147483647,
        "version": 1,
        "versionNonce": uuid.uuid4().int % 2147483647,
        "isDeleted": False,
        "boundElements": None,
        "updated": 0,
        "link": None,
        "locked": False,
        "points": [
            [0, 0],
            [x2 - x1, y2 - y1]
        ],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": start_arrow,
        "endArrowhead": end_arrow,
    }
    
    return arrow_element


def convert_to_excalidraw(diagram_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将内部图数据转换为Excalidraw元素列表
    
    Args:
        diagram_data: 内部图数据格式
    
    Returns:
        Excalidraw元素列表
    """
    nodes = diagram_data.get("nodes", [])
    edges = diagram_data.get("edges", [])
    
    # 自动布局（对未指定坐标的节点）
    nodes = _auto_layout(nodes, edges)
    
    # 转换节点
    excalidraw_elements: List[Dict[str, Any]] = []
    node_id_to_first_excalidraw: Dict[str, str] = {}
    
    for node in nodes:
        elements = _node_to_excalidraw(node)
        if elements:
            node_id_to_first_excalidraw[node["id"]] = elements[0]["id"]
            excalidraw_elements.extend(elements)
    
    # 转换边
    for edge in edges:
        arrow_element = _edge_to_excalidraw(
            edge, 
            node_id_to_first_excalidraw,
            nodes
        )
        excalidraw_elements.append(arrow_element)
        
        # 如果边有label，添加文本元素
        edge_label = edge.get("label")
        if edge_label:
            source_node = next((n for n in nodes if n["id"] == edge["source"]), None)
            target_node = next((n for n in nodes if n["id"] == edge["target"]), None)
            
            if source_node and target_node:
                sx = source_node.get("x", 100) + (source_node.get("width", 140) or 140) / 2
                sy = source_node.get("y", 100) + (source_node.get("height", 60) or 60) / 2
                tx = target_node.get("x", 100) + (target_node.get("width", 140) or 140) / 2
                ty = target_node.get("y", 100) + (target_node.get("height", 60) or 60) / 2
                
                mid_x = (sx + tx) / 2
                mid_y = (sy + ty) / 2
                
                label_text_element = {
                    "id": _gen_excalidraw_id(),
                    "type": "text",
                    "x": mid_x - len(edge_label) * 7,
                    "y": mid_y - 15,
                    "width": len(edge_label) * 14 + 10,
                    "height": 25,
                    "angle": 0,
                    "strokeColor": "#1e1e1e",
                    "backgroundColor": "transparent",
                    "fillStyle": "solid",
                    "strokeWidth": 1,
                    "strokeStyle": "solid",
                    "roughness": 0,
                    "opacity": 100,
                    "groupIds": [],
                    "frameId": None,
                    "roundness": None,
                    "seed": hash(f"edge_label_{edge.get('id', '')}") % 2147483647,
                    "version": 1,
                    "versionNonce": uuid.uuid4().int % 2147483647,
                    "isDeleted": False,
                    "boundElements": None,
                    "updated": 0,
                    "link": None,
                    "locked": False,
                    "text": edge_label,
                    "fontSize": 16,
                    "fontFamily": 5,
                    "textAlign": "center",
                    "verticalAlign": "middle",
                    "baseline": 20,
                    "containerId": None,
                    "originalText": edge_label,
                    "lineHeight": 1.25,
                }
                excalidraw_elements.append(label_text_element)
    
    return excalidraw_elements
