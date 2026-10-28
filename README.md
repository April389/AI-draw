# AI 智能绘图系统

> 基于大语言模型的智能矢量图表生成系统，支持通过自然语言生成流程图、架构图、时序图、思维导图等多种矢量图表，降低非技术用户的图表制作门槛。

## 核心特性

- **自然语言生成图表**：用一句话描述需求，AI 自动生成专业图表
- **多图表类型支持**：流程图、架构图、时序图、思维导图、状态图、类图、通用图
- **Prompt 工程 + JSON Schema 校验**：通过精细的 Prompt 约束 LLM 输出严格遵循 JSON Schema，确保输出可解析、可验证
- **可交互矢量画布**：基于 SVG 的原生画布，支持节点拖拽、缩放、平移、选中、删除
- **多格式导出**：支持 PNG、SVG、JSON 三种格式导出
- **流式渲染**：前端通过 SVG 实时渲染，加载流畅
- **详尽的测试覆盖**：后端 67 个单元测试，前端 Vitest 测试套件

## 技术架构

### 后端（Python + FastAPI）
- **FastAPI**：高性能异步 Web 框架
- **Pydantic v2**：数据模型与 Schema 验证
- **OpenAI SDK**：兼容 OpenAI API 格式的大模型调用（支持 DeepSeek、Qwen、GPT 等）
- **jsonschema**：LLM 输出的 JSON Schema 严格校验
- **Prompt 工程**：通过 System Prompt 约束输出格式 + 各图表类型设计指引

### 前端（Vue 3 + TypeScript + Vite）
- **Vue 3 Composition API**：响应式组件开发
- **Pinia**：状态管理
- **原生 SVG 画布**：自研矢量绘图引擎（无 Excalidraw React 依赖，更轻量）
- **Vitest**：前端单元测试
- **Axios**：HTTP 请求

## 项目结构

```
.
├── backend/                    # 后端 FastAPI 服务
│   ├── app.py                  # FastAPI 主应用与路由
│   ├── config.py               # 配置管理
│   ├── schemas.py              # Pydantic 数据模型
│   ├── prompt_templates.py     # Prompt 工程：System Prompt & 用户 Prompt
│   ├── schema_validator.py     # JSON Schema 校验器
│   ├── llm_client.py           # LLM 客户端封装（含 Mock 模式）
│   ├── graph_converter.py      # 图数据 → Excalidraw/SVG 元素转换器
│   ├── requirements.txt        # Python 依赖
│   └── tests/                  # 后端测试套件（67个测试）
├── frontend/                   # 前端 Vue 3 应用
│   ├── src/
│   │   ├── components/         # 组件
│   │   │   ├── PromptInput.vue # Prompt 输入面板
│   │   │   ├── DiagramCanvas.vue # 矢量画布
│   │   │   └── Toolbar.vue     # 工具栏
│   │   ├── stores/             # Pinia Store
│   │   ├── api/                # API 封装
│   │   ├── types/              # TypeScript 类型定义
│   │   ├── utils/export.ts     # 导出工具（PNG/SVG/JSON）
│   │   └── App.vue             # 根组件
│   ├── tests/                  # 前端测试
│   ├── package.json
│   └── vite.config.ts
└── .gitignore
```

## 快速开始

### 1. 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置 LLM API（可选，默认使用 Mock 模式）
# 复制 .env.example 为 .env 并填入你的 API Key
# cp .env.example .env

# 启动服务
python app.py
# 或 uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 使用系统。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | 根据自然语言生成图表 |
| POST | `/api/validate` | 校验图数据结构 |
| POST | `/api/convert` | 转换为 Excalidraw 元素 |
| GET | `/api/diagram-types` | 列出支持的图表类型 |
| GET | `/health` | 健康检查 |

### 生成请求示例

```json
POST /api/generate
{
  "prompt": "创建一个用户登录流程图，包含输入账号密码、验证、成功/失败分支",
  "diagram_type": "flowchart"
}
```

## 运行测试

### 后端测试

```bash
cd backend
pytest tests/ -v
```

测试覆盖：
- Prompt 模板构建与设计指引
- JSON Schema 提取与校验
- LLM 客户端（Mock 模式）
- 图数据转换器（自动布局、形状映射）
- FastAPI 端点（生成、校验、转换、健康检查）

### 前端测试

```bash
cd frontend
npm test
```

## LLM 配置

系统默认使用 **Mock 模式**（无需 API Key 即可运行，返回预设图数据用于演示）。

接入真实 LLM（兼容 OpenAI API 格式，如 DeepSeek / Qwen / GPT）：

1. 编辑 `backend/.env`（基于 `.env.example`）：
```env
LLM_API_KEY=sk-你的密钥
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

2. 重启后端服务

## 许可证

MIT License
