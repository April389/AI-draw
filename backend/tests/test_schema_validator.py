"""
测试 JSON Schema 校验模块
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import pytest
from schema_validator import (
    extract_json_from_text,
    parse_llm_response,
    full_validate,
    RUNTIME_SCHEMA
)
import jsonschema


class TestExtractJsonFromText:
    """测试JSON提取"""
    
    def test_extract_from_markdown_code_block(self, llm_json_response):
        """从Markdown代码块中提取JSON"""
        result = extract_json_from_text(llm_json_response)
        # 应该能解析为JSON
        parsed = json.loads(result)
        assert "diagram_type" in parsed
        assert "nodes" in parsed
    
    def test_extract_from_raw_json(self, llm_raw_json_response):
        """从纯JSON字符串提取"""
        result = extract_json_from_text(llm_raw_json_response)
        parsed = json.loads(result)
        assert parsed["diagram_type"] == "flowchart"
    
    def test_extract_with_prefix_text(self):
        """前面有解释文字的情况"""
        text = "好的，我来生成这个图表：\n\n{\"diagram_type\": \"generic\", \"nodes\": [{\"id\": \"a\", \"label\": \"A\"}]}"
        result = extract_json_from_text(text)
        parsed = json.loads(result)
        assert parsed["diagram_type"] == "generic"
    
    def test_extract_with_suffix_text(self):
        """后面有解释文字的情况"""
        text = "{\"diagram_type\": \"generic\", \"nodes\": [{\"id\": \"a\", \"label\": \"A\"}]} \n\n以上是生成的图表"
        result = extract_json_from_text(text)
        parsed = json.loads(result)
        assert "nodes" in parsed
    
    def test_extract_pure_json(self):
        """纯JSON输入"""
        pure = '{"a": 1, "b": [1,2,3]}'
        result = extract_json_from_text(pure)
        parsed = json.loads(result)
        assert parsed["a"] == 1


class TestParseLlmResponse:
    """测试LLM响应解析"""
    
    def test_parse_valid_response(self, llm_json_response):
        """解析有效的代码块包裹的响应"""
        success, data, errors = parse_llm_response(llm_json_response)
        assert success is True
        assert len(errors) == 0
        assert data["diagram_type"] == "flowchart"
        assert len(data["nodes"]) == 2
    
    def test_parse_raw_json(self, llm_raw_json_response):
        """解析纯JSON响应"""
        success, data, errors = parse_llm_response(llm_raw_json_response)
        assert success is True
        assert data["diagram_type"] == "flowchart"
    
    def test_parse_invalid_json(self):
        """解析无效JSON"""
        success, data, errors = parse_llm_response("这不是JSON")
        assert success is False
        assert len(errors) > 0
    
    def test_parse_schema_missing_nodes(self, invalid_data_no_nodes):
        """缺少必需字段"""
        raw = json.dumps(invalid_data_no_nodes)
        success, data, errors = parse_llm_response(raw)
        assert success is False
        # 应该有Schema校验错误
        assert any("nodes" in e.lower() or "schema" in e.lower() for e in errors)
    
    def test_parse_bad_edge_reference(self, invalid_data_bad_edge):
        """边引用不存在的节点"""
        raw = json.dumps(invalid_data_bad_edge)
        success, data, errors = parse_llm_response(raw)
        # Schema校验通过但业务逻辑校验失败
        assert success is False
        assert any("不存在" in e for e in errors)
    
    def test_parse_duplicate_node_ids(self):
        """重复的节点ID"""
        data = {
            "diagram_type": "flowchart",
            "nodes": [
                {"id": "dup", "label": "A"},
                {"id": "dup", "label": "B"}
            ]
        }
        success, result, errors = parse_llm_response(json.dumps(data))
        assert success is False
        assert any("重复" in e for e in errors)


class TestFullValidate:
    """测试完整校验"""
    
    def test_validate_good_flowchart(self, valid_flowchart_data):
        """校验良好的流程图"""
        valid, errors, warnings = full_validate(valid_flowchart_data)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_good_architecture(self, valid_architecture_data):
        """校验良好的架构图"""
        valid, errors, warnings = full_validate(valid_architecture_data)
        assert valid is True
    
    def test_validate_warns_single_node(self):
        """单个节点时应有警告"""
        data = {
            "diagram_type": "generic",
            "nodes": [{"id": "only", "label": "唯一"}]
        }
        valid, errors, warnings = full_validate(data)
        assert valid is True  # 单个节点合法
        assert any("至少" in w for w in warnings)  # 但有警告
    
    def test_validate_warns_orphan_node(self):
        """有孤立节点时应有警告"""
        data = {
            "diagram_type": "flowchart",
            "nodes": [
                {"id": "a", "label": "A"},
                {"id": "b", "label": "B"},
                {"id": "c", "label": "孤立"}
            ],
            "edges": [
                {"id": "e1", "source": "a", "target": "b"}
            ]
        }
        valid, errors, warnings = full_validate(data)
        assert valid is True
        assert any("孤立" in w or "未被" in w for w in warnings)
    
    def test_validate_errors_on_bad_type(self):
        """错误的图表类型"""
        data = {
            "diagram_type": "invalid_type",
            "nodes": [{"id": "a", "label": "A"}]
        }
        valid, errors, warnings = full_validate(data)
        assert valid is False
        assert len(errors) > 0


class TestRuntimeSchema:
    """测试运行时Schema"""
    
    def test_runtime_schema_is_valid(self):
        """运行时Schema本身合法"""
        jsonschema.Draft7Validator.check_schema(RUNTIME_SCHEMA)
    
    def test_runtime_schema_validates_good_data(self, valid_flowchart_data):
        """运行时Schema能正确校验好数据"""
        jsonschema.validate(instance=valid_flowchart_data, schema=RUNTIME_SCHEMA)
    
    def test_runtime_schema_rejects_bad_data(self):
        """运行时Schema拒绝坏数据"""
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"diagram_type": "flowchart"}, schema=RUNTIME_SCHEMA)
