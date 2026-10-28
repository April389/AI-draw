"""
测试 FastAPI 应用端点
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_llm_response():
    """Mock的LLM JSON响应"""
    return '''{
        "diagram_type": "flowchart",
        "title": "测试流程图",
        "nodes": [
            {"id": "start", "label": "开始", "type": "ellipse", "x": 400, "y": 50},
            {"id": "process", "label": "处理", "type": "rectangle", "x": 380, "y": 150},
            {"id": "end", "label": "结束", "type": "ellipse", "x": 400, "y": 250}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "process"},
            {"id": "e2", "source": "process", "target": "end"}
        ]
    }'''


@pytest.fixture
def client_with_mock(mock_llm_response):
    """带有Mock LLM客户端的TestClient"""
    # 为每次测试重新导入app以使用Mock
    with patch('app.get_llm_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.generate.return_value = mock_llm_response
        mock_get_client.return_value = mock_client
        
        # 延迟导入，确保使用最新的app模块
        from importlib import import_module, reload
        import app as app_module
        reload(app_module)
        
        # 注入Mock的LLM客户端到app.state
        app_module.app.state.llm_client = mock_client
        
        with TestClient(app_module.app) as client:
            yield client


@pytest.fixture
def client_with_real_mock():
    """使用实际MockLLMClient的TestClient"""
    from importlib import import_module, reload
    import app as app_module
    reload(app_module)
    
    from llm_client import MockLLMClient
    app_module.app.state.llm_client = MockLLMClient()
    
    with TestClient(app_module.app) as client:
        yield client


class TestHealthEndpoint:
    """测试健康检查端点"""
    
    def test_health_returns_ok(self, client_with_real_mock):
        """健康检查返回200和ok"""
        response = client_with_real_mock.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestGenerateEndpoint:
    """测试生成端点"""
    
    def test_generate_success(self, client_with_mock):
        """正常生成"""
        response = client_with_mock.post(
            "/api/generate",
            json={"prompt": "创建一个流程图"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["diagram"]["diagram_type"] == "flowchart"
        assert len(data["diagram"]["nodes"]) >= 3
        assert data["excalidraw_elements"] is not None
        assert len(data["excalidraw_elements"]) > 0
    
    def test_generate_with_diagram_type(self, client_with_mock):
        """指定图表类型"""
        response = client_with_mock.post(
            "/api/generate",
            json={"prompt": "创建图表", "diagram_type": "architecture"}
        )
        assert response.status_code == 200
    
    def test_generate_empty_prompt_rejected(self, client_with_mock):
        """空Prompt被拒绝"""
        response = client_with_mock.post(
            "/api/generate",
            json={"prompt": ""}
        )
        assert response.status_code == 422  # Pydantic校验失败
    
    def test_generate_too_long_prompt_rejected(self, client_with_mock):
        """过长Prompt被拒绝"""
        response = client_with_mock.post(
            "/api/generate",
            json={"prompt": "x" * 3000}
        )
        assert response.status_code == 422
    
    def test_generate_handles_llm_failure(self, client_with_mock):
        """LLM调用失败的处理"""
        client_with_mock.app.state.llm_client.generate.side_effect = Exception("API Error")
        
        response = client_with_mock.post(
            "/api/generate",
            json={"prompt": "测试"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "失败" in data.get("error", "")


class TestValidateEndpoint:
    """测试校验端点"""
    
    def test_validate_valid_data(self, client_with_real_mock, valid_flowchart_data):
        """校验有效数据"""
        response = client_with_real_mock.post(
            "/api/validate",
            json={"diagram": valid_flowchart_data}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0
    
    def test_validate_invalid_edge_ref(self, client_with_real_mock, invalid_data_bad_edge):
        """校验边引用错误"""
        response = client_with_real_mock.post(
            "/api/validate",
            json={"diagram": invalid_data_bad_edge}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
    
    def test_validate_missing_nodes(self, client_with_real_mock, invalid_data_no_nodes):
        """校验缺少节点"""
        response = client_with_real_mock.post(
            "/api/validate",
            json={"diagram": invalid_data_no_nodes}
        )
        # Pydantic可能在请求层拦截，也可能返回200但valid=False
        assert response.status_code in [200, 422]


class TestConvertEndpoint:
    """测试转换端点"""
    
    def test_convert_success(self, client_with_real_mock, valid_flowchart_data):
        """成功转换"""
        response = client_with_real_mock.post(
            "/api/convert",
            json=valid_flowchart_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "elements" in data
        assert data["count"] > 0
    
    def test_convert_architecture(self, client_with_real_mock, valid_architecture_data):
        """转换架构图"""
        response = client_with_real_mock.post(
            "/api/convert",
            json=valid_architecture_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestDiagramTypesEndpoint:
    """测试图表类型列表端点"""
    
    def test_list_types(self, client_with_real_mock):
        """列出所有支持的图表类型"""
        response = client_with_real_mock.get("/api/diagram-types")
        assert response.status_code == 200
        data = response.json()
        types = data["types"]
        
        assert len(types) == 7
        
        type_values = [t["value"] for t in types]
        assert "flowchart" in type_values
        assert "architecture" in type_values
        assert "sequence" in type_values
        assert "mindmap" in type_values
        assert "state" in type_values
        assert "class" in type_values
        assert "generic" in type_values


class TestCors:
    """测试CORS配置"""
    
    def test_cors_headers_present(self, client_with_real_mock):
        """响应包含CORS头"""
        response = client_with_real_mock.get(
            "/health",
            headers={"Origin": "http://example.com"}
        )
        assert response.headers.get("access-control-allow-origin") is not None
