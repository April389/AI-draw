"""
pytest配置文件
定义共享fixtures和测试选项
"""
import sys
import os
import json
import pytest

# 确保backend目录在导入路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


# ==================== 测试数据fixtures ====================

@pytest.fixture
def valid_flowchart_data():
    """有效的流程图测试数据"""
    return {
        "diagram_type": "flowchart",
        "title": "测试流程图",
        "nodes": [
            {"id": "start", "label": "开始", "type": "ellipse"},
            {"id": "process", "label": "处理", "type": "rectangle"},
            {"id": "decision", "label": "判断", "type": "diamond"},
            {"id": "end", "label": "结束", "type": "ellipse"}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "process", "arrow": "end"},
            {"id": "e2", "source": "process", "target": "decision", "arrow": "end"},
            {"id": "e3", "source": "decision", "target": "end", "arrow": "end"}
        ]
    }


@pytest.fixture
def valid_architecture_data():
    """有效的架构图测试数据"""
    return {
        "diagram_type": "architecture",
        "title": "测试架构",
        "nodes": [
            {"id": "frontend", "label": "前端", "type": "rectangle", "color": "#95C2F6"},
            {"id": "backend", "label": "后端", "type": "rectangle", "color": "#A8E6CF"},
            {"id": "db", "label": "数据库", "type": "cylinder", "color": "#FFD6A5"}
        ],
        "edges": [
            {"id": "e1", "source": "frontend", "target": "backend"},
            {"id": "e2", "source": "backend", "target": "db"}
        ]
    }


@pytest.fixture
def valid_sequence_data():
    """有效的时序图测试数据"""
    return {
        "diagram_type": "sequence",
        "title": "用户登录时序",
        "nodes": [
            {"id": "user", "label": "用户", "type": "rectangle", "x": 100},
            {"id": "client", "label": "客户端", "type": "rectangle", "x": 300},
            {"id": "server", "label": "服务端", "type": "rectangle", "x": 500}
        ],
        "edges": [
            {"id": "e1", "source": "user", "target": "client", "label": "输入密码"},
            {"id": "e2", "source": "client", "target": "server", "label": "POST /login", "arrow": "end"}
        ]
    }


@pytest.fixture
def invalid_data_no_nodes():
    """无效数据：缺少nodes"""
    return {
        "diagram_type": "flowchart",
        "edges": []
    }


@pytest.fixture
def invalid_data_bad_edge():
    """无效数据：边引用不存在的节点"""
    return {
        "diagram_type": "flowchart",
        "nodes": [
            {"id": "node1", "label": "节点1"}
        ],
        "edges": [
            {"id": "e1", "source": "node1", "target": "nonexistent"}
        ]
    }


@pytest.fixture
def llm_json_response():
    """模拟LLM返回的JSON字符串（Markdown代码块包裹）"""
    return """```json
{
    "diagram_type": "flowchart",
    "title": "代码块中的JSON",
    "nodes": [
        {"id": "a", "label": "节点A", "type": "rectangle"},
        {"id": "b", "label": "节点B", "type": "ellipse"}
    ],
    "edges": [
        {"id": "e1", "source": "a", "target": "b"}
    ]
}
```"""


@pytest.fixture
def llm_raw_json_response():
    """模拟LLM直接返回的JSON字符串（无包裹）"""
    return '{"diagram_type": "flowchart", "nodes": [{"id": "x", "label": "X"}], "edges": []}'
