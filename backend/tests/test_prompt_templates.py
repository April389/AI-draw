"""
测试 Prompt 模板模块
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from prompt_templates import (
    build_user_prompt,
    get_system_prompt,
    SYSTEM_PROMPT_BASE,
    DIAGRAM_JSON_SCHEMA
)


class TestBuildUserPrompt:
    """测试用户Prompt构建"""
    
    def test_basic_prompt(self):
        """测试基本Prompt构建"""
        result = build_user_prompt("创建一个用户注册流程")
        assert "用户注册流程" in result
        assert "JSON Schema" in result
    
    def test_prompt_with_type(self):
        """测试指定图表类型"""
        result = build_user_prompt("测试", diagram_type="flowchart")
        assert "流程图" in result
    
    def test_prompt_with_architecture_type(self):
        """测试架构图类型"""
        result = build_user_prompt("测试", diagram_type="architecture")
        assert "架构图" in result
    
    def test_prompt_with_none_type(self):
        """测试不指定类型"""
        result = build_user_prompt("简单描述")
        # 不包含类型提示
        assert "【" not in result or "】" not in result
    
    def test_prompt_empty_input(self):
        """空输入也应生成有效Prompt"""
        result = build_user_prompt("")
        assert result is not None
        assert isinstance(result, str)


class TestGetSystemPrompt:
    """测试系统Prompt"""
    
    def test_system_prompt_not_empty(self):
        """系统Prompt非空"""
        prompt = get_system_prompt()
        assert prompt is not None
        assert len(prompt) > 100
    
    def test_system_prompt_contains_schema(self):
        """系统Prompt包含Schema定义"""
        prompt = get_system_prompt()
        assert "diagram_type" in prompt
        assert "nodes" in prompt
    
    def test_system_prompt_contains_guidelines(self):
        """系统Prompt包含设计指引"""
        prompt = get_system_prompt()
        assert "流程图" in prompt
        assert "架构图" in prompt


class TestSchemaDefinition:
    """测试JSON Schema定义"""
    
    def test_schema_is_valid_json(self):
        """Schema字符串是合法的JSON"""
        import json
        parsed = json.loads(DIAGRAM_JSON_SCHEMA)
        assert parsed["type"] == "object"
        assert "properties" in parsed
    
    def test_schema_has_required_fields(self):
        """Schema包含必需字段定义"""
        import json
        parsed = json.loads(DIAGRAM_JSON_SCHEMA)
        assert "diagram_type" in parsed["properties"]
        assert "nodes" in parsed["properties"]
        assert "edges" in parsed["properties"]
    
    def test_schema_node_types(self):
        """Schema支持多种节点类型"""
        import json
        parsed = json.loads(DIAGRAM_JSON_SCHEMA)
        node_props = parsed["properties"]["nodes"]["items"]["properties"]
        node_types = node_props["type"]["enum"]
        assert "rectangle" in node_types
        assert "ellipse" in node_types
        assert "diamond" in node_types
