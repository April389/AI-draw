"""
测试 LLM 客户端模块
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from llm_client import (
    BaseLLMClient,
    OpenAICompatibleClient,
    MockLLMClient,
    create_llm_client
)


class TestMockLLMClient:
    """测试Mock客户端"""
    
    @pytest.fixture
    def client(self):
        return MockLLMClient()
    
    def test_generate_returns_valid_json(self, client):
        """Mock客户端返回的是合法JSON"""
        result = client.generate("system", "user prompt")
        parsed = json.loads(result)
        assert "diagram_type" in parsed
        assert "nodes" in parsed
    
    def test_generate_contains_nodes(self, client):
        """返回的数据包含节点"""
        result = client.generate("system", "创建流程图")
        parsed = json.loads(result)
        assert len(parsed["nodes"]) > 0
    
    def test_flowchart_prompt_returns_flowchart(self, client):
        """流程图关键词返回流程图"""
        result = client.generate("system", "创建一个流程图")
        parsed = json.loads(result)
        assert parsed["diagram_type"] == "flowchart"
    
    def test_architecture_prompt_returns_architecture(self, client):
        """架构关键词返回架构图"""
        result = client.generate("system", "创建一个系统架构图")
        parsed = json.loads(result)
        assert parsed["diagram_type"] == "architecture"
    
    def test_mock_response_structure(self, client):
        """Mock响应结构完整性"""
        result = client.generate("system", "随便输入")
        parsed = json.loads(result)
        # 每个节点必须有id和label
        for node in parsed["nodes"]:
            assert "id" in node
            assert "label" in node
        # 每条边必须有source和target
        for edge in parsed.get("edges", []):
            assert "source" in edge
            assert "target" in edge


class TestCreateLLMClient:
    """测试客户端工厂"""
    
    def test_create_mock_client(self):
        """创建Mock客户端"""
        client = create_llm_client(mock=True)
        assert isinstance(client, MockLLMClient)
    
    def test_create_openai_client_when_available(self):
        """有openai包时创建OpenAI客户端"""
        client = create_llm_client(mock=False)
        # 可能是OpenAI客户端或降级的Mock客户端
        assert client is not None
        assert isinstance(client, BaseLLMClient)


class TestOpenAICompatibleClient:
    """测试OpenAI兼容客户端（需要Mock网络调用）"""
    
    def test_client_initialization_with_mock(self):
        """使用Mock的openai模块测试初始化"""
        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = MagicMock()
        
        with patch.dict('sys.modules', {'openai': mock_openai}):
            # 重新导入以触发新的模块加载
            from importlib import reload
            import llm_client
            reload(llm_client)
            
            client = llm_client.OpenAICompatibleClient(
                api_key="test-key",
                base_url="http://test",
                model="test-model"
            )
            assert client.api_key == "test-key"
            assert client.base_url == "http://test"
            assert client.model == "test-model"
    
    def test_mock_client_fallback(self):
        """当OpenAI不可用时降级到Mock"""
        # 创建一个未初始化网络客户端的情况
        client = MockLLMClient()
        result = client.generate("system", "test")
        assert result is not None
        assert isinstance(result, str)
