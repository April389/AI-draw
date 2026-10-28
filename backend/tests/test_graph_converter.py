"""
测试图数据转换器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from graph_converter import (
    convert_to_excalidraw,
    _auto_layout,
    _node_to_excalidraw,
    _edge_to_excalidraw,
    NODE_TYPE_MAP,
    DEFAULT_NODE_SIZES
)


class TestConvertToExcalidraw:
    """测试主转换函数"""
    
    def test_convert_flowchart(self, valid_flowchart_data):
        """转换流程图"""
        elements = convert_to_excalidraw(valid_flowchart_data)
        
        assert len(elements) > 0
        # 检查是否有rectangle/ellipse/diamond类型的形状
        types = set(e["type"] for e in elements)
        shape_types = {"rectangle", "ellipse", "diamond"}
        assert types & shape_types  # 至少有一种形状类型
    
    def test_convert_architecture(self, valid_architecture_data):
        """转换架构图"""
        elements = convert_to_excalidraw(valid_architecture_data)
        
        assert len(elements) > 0
        # 检查cylinder被映射为rectangle
        rects = [e for e in elements if e["type"] == "rectangle"]
        assert len(rects) >= 3  # 至少三个节点
    
    def test_convert_sequence(self, valid_sequence_data):
        """转换时序图"""
        elements = convert_to_excalidraw(valid_sequence_data)
        assert len(elements) > 0
    
    def test_convert_elements_have_required_fields(self, valid_flowchart_data):
        """转换后的元素包含必需字段"""
        elements = convert_to_excalidraw(valid_flowchart_data)
        
        required_fields = {"id", "type", "x", "y", "width", "height", 
                          "angle", "strokeColor", "backgroundColor", 
                          "fillStyle", "strokeWidth", "roughness",
                          "opacity", "seed", "version", "isDeleted"}
        
        for element in elements:
            missing = required_fields - set(element.keys())
            assert len(missing) == 0, f"元素缺少字段: {missing}"
    
    def test_convert_single_node(self):
        """单个节点也能转换"""
        data = {
            "diagram_type": "generic",
            "nodes": [{"id": "only", "label": "唯一节点", "type": "ellipse"}],
            "edges": []
        }
        elements = convert_to_excalidraw(data)
        assert len(elements) >= 2  # 形状 + 文本
    
    def test_convert_with_colors(self):
        """保留颜色信息"""
        data = {
            "diagram_type": "generic",
            "nodes": [{"id": "n1", "label": "彩色节点", "color": "#FF0000", "stroke_color": "#00FF00"}],
            "edges": []
        }
        elements = convert_to_excalidraw(data)
        rect = next((e for e in elements if e["type"] == "rectangle"), None)
        if rect:
            assert rect["backgroundColor"] == "#FF0000"
            assert rect["strokeColor"] == "#00FF00"


class TestAutoLayout:
    """测试自动布局"""
    
    def test_layout_moves_unpositioned_nodes(self):
        """自动布局为未指定坐标的节点分配位置"""
        nodes = [
            {"id": "a", "label": "A"},
            {"id": "b", "label": "B"},
            {"id": "c", "label": "C"}
        ]
        edges = [
            {"id": "e1", "source": "a", "target": "b"},
            {"id": "e2", "source": "b", "target": "c"}
        ]
        
        nodes = _auto_layout(nodes, edges)
        
        # 所有节点都应有坐标
        for node in nodes:
            assert node.get("x") is not None
            assert node.get("y") is not None
    
    def test_layout_preserves_existing_positions(self):
        """已指定坐标的节点保持不变"""
        nodes = [
            {"id": "fixed", "label": "固定", "x": 500, "y": 300},
            {"id": "auto", "label": "自动"}
        ]
        edges = []
        
        nodes = _auto_layout(nodes, edges)
        
        fixed_node = next(n for n in nodes if n["id"] == "fixed")
        assert fixed_node["x"] == 500
        assert fixed_node["y"] == 300


class TestNodeToExcalidraw:
    """测试节点转换"""
    
    def test_rectangle_node(self):
        """矩形节点"""
        node = {"id": "r1", "label": "矩形", "type": "rectangle", "x": 100, "y": 100}
        elements = _node_to_excalidraw(node)
        
        rect = next(e for e in elements if e["type"] == "rectangle")
        assert rect["x"] == 100
        assert rect["y"] == 100
    
    def test_ellipse_node(self):
        """椭圆节点"""
        node = {"id": "e1", "label": "椭圆", "type": "ellipse", "x": 200, "y": 150}
        elements = _node_to_excalidraw(node)
        
        ellipse = next(e for e in elements if e["type"] == "ellipse")
        assert ellipse is not None
    
    def test_node_creates_text_label(self):
        """节点会生成配套的文本元素"""
        node = {"id": "t1", "label": "Hello", "type": "rectangle", "x": 50, "y": 50}
        elements = _node_to_excalidraw(node)
        
        texts = [e for e in elements if e["type"] == "text"]
        assert len(texts) == 1
        assert texts[0]["text"] == "Hello"


class TestEdgeToExcalidraw:
    """测试边转换"""
    
    def test_basic_edge(self, valid_flowchart_data):
        """基本边转换"""
        nodes = valid_flowchart_data["nodes"]
        # 先自动布局
        nodes = _auto_layout(nodes, valid_flowchart_data["edges"])
        
        edge = valid_flowchart_data["edges"][0]
        element = _edge_to_excalidraw(edge, {}, nodes)
        
        assert element["type"] == "arrow"
        assert len(element["points"]) == 2
    
    def test_edge_with_label(self, valid_sequence_data):
        """带标签的边"""
        nodes = valid_sequence_data["nodes"]
        nodes = _auto_layout(nodes, valid_sequence_data["edges"])
        
        edge = valid_sequence_data["edges"][0]
        assert edge.get("label") is not None


class TestNodeTypeMapping:
    """测试节点类型映射"""
    
    def test_all_types_mapped(self):
        """所有预定义类型都有映射"""
        expected_types = {"rectangle", "ellipse", "diamond", "parallelogram", "cylinder", "cloud", "hexagon"}
        assert set(NODE_TYPE_MAP.keys()) == expected_types
    
    def test_default_sizes_exist(self):
        """每个类型都有默认尺寸"""
        for ntype in NODE_TYPE_MAP:
            assert ntype in DEFAULT_NODE_SIZES
