# 🚀 FastAPI File Upload & Q&A Service

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg)](https://www.python.org/)

一个功能强大的 FastAPI 文件上传服务，支持上传 Markdown (.md)、PDF (.pdf) 和文本 (.txt) 文件，并内置**智能问答**能力。

## ✨ 核心特性

### 📤 文件上传
- ✅ 支持 `.md`、`.pdf`、`.txt` 文件上传
- ✅ 自动保存到 `./uploads` 目录
- ✅ PDF 文件使用 `pypdf` 提取文本
- ✅ Markdown 和 TXT 文件直接读取

### 🧠 智能问答 (RAG)
- ✅ 自动文本分块（500字符/块，100字符重叠）
- ✅ 使用 BAAI/bge-small-zh-v1.5 中文嵌入模型
- ✅ 自定义内存向量存储（基于 NumPy）
- ✅ 余弦相似度语义搜索
- ✅ LLM 集成支持

### 🛡️ 生产就绪
- ✅ RESTful API 设计
- ✅ 健康检查端点
- ✅ 完整的错误处理
- ✅ 环境变量配置

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/Absoluking/claude-code.git
cd claude-code
```

### 2. 创建虚拟环境

```bash
python -m venv venv
```

**激活虚拟环境**:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量（可选）

创建 `.env` 文件：

```env
ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1
ANTHROPIC_AUTH_TOKEN=test-token-123
ANTHROPIC_MODEL=glm-4.7-flash
```

## 🚀 运行服务

```bash
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://0.0.0.0:8000` 启动。

## 📖 API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API 接口说明

### 1. 健康检查

```
GET /health
```

检查服务状态和向量存储状态。

**响应示例**:
```json
{
  "status": "healthy",
  "collections": 1,
  "documents_in_store": 3,
  "llm_available": true,
  "llm_model": "glm-4.7-flash",
  "llm_base_url": "http://127.0.0.1:8000/v1"
}
```

### 2. 上传文件

```
POST /upload
Content-Type: multipart/form-data
```

上传文件并自动提取文本内容，创建向量索引。

**参数**:
- `file` (required) - 上传的文件

**支持的文件类型**: `.md`, `.pdf`, `.txt`

**响应示例**:
```json
{
  "filename": "document.pdf",
  "filepath": "uploads/document.pdf",
  "file_size": 12345,
  "content": "这是提取的 PDF 文本内容...",
  "chunks_count": 25
}
```

### 3. 智能问答

```
POST /ask
```

基于上传的文件内容进行语义搜索并生成答案。

**参数**:
- `question` (required) - 用户问题

**响应示例**:
```json
{
  "question": "文档中提到的主要内容是什么？",
  "answer": "根据文档内容，主要提到了以下内容：...",
  "model": "glm-4.7-flash"
}
```

**工作流程**:
1. **文本分块**: 将上传文件内容分块
2. **向量化**: 使用 BGE 模型生成向量
3. **语义检索**: 查找最相关的 3 个文本块
4. **提示词构建**: 组合上下文和问题
5. **LLM 生成**: 调用 LLM 生成答案

## 🔧 LLM 配置

本项目使用 OpenAI 兼容的 API 接口调用本地 LLM 服务。

### 环境变量

```bash
# LLM 服务地址（必需）
ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1

# 认证令牌（必需）
ANTHROPIC_AUTH_TOKEN=your-auth-token-here

# 模型名称（可选，默认：glm-4.7-flash）
ANTHROPIC_MODEL=glm-4.7-flash
```

### 配置示例

**Windows (CMD)**:
```cmd
set ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1
set ANTHROPIC_AUTH_TOKEN=test-token-123
set ANTHROPIC_MODEL=glm-4.7-flash
python main.py
```

**Windows (PowerShell)**:
```powershell
$env:ANTHROPIC_BASE_URL="http://127.0.0.1:8000/v1"
$env:ANTHROPIC_AUTH_TOKEN="test-token-123"
$env:ANTHROPIC_MODEL="glm-4.7-flash"
python main.py
```

**Linux/Mac**:
```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1
export ANTHROPIC_AUTH_TOKEN=test-token-123
export ANTHROPIC_MODEL=glm-4.7-flash
python main.py
```

### 配置文件 (.env)

创建 `.env` 文件：

```env
ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1
ANTHROPIC_AUTH_TOKEN=test-token-123
ANTHROPIC_MODEL=glm-4.7-flash
```

## 🧪 测试示例

### 上传文件测试

```bash
# 上传 TXT 文件
curl -X POST "http://localhost:8000/upload" -F "file=@test.txt"

# 上传 Markdown 文件
curl -X POST "http://localhost:8000/upload" -F "file=@README.md"

# 上传 PDF 文件
curl -X POST "http://localhost:8000/upload" -F "file=@example.pdf"
```

### 智能问答测试

```bash
# 检查健康状态
curl http://localhost:8000/health

# 提问（使用 POST + form data）
curl -X POST "http://localhost:8000/ask" -F "question=FastAPI 的特点是什么？"

# 提问（使用 GET）
curl "http://localhost:8000/ask?question=向量数据库有什么应用？"
```

## 📁 项目结构

```
.
├── main.py                 # 主应用文件
├── requirements.txt        # Python 依赖
├── README.md              # 项目文档
├── .env                   # 环境变量配置（可选）
├── .gitignore            # Git 忽略文件
└── uploads/              # 文件上传目录
    ├── example.md
    ├── document.pdf
    └── data.txt
```

## 🔍 向量数据库技术细节

本项目使用自定义的内存向量存储实现，无需额外的向量数据库依赖。

### 技术栈
- **嵌入模型**: BAAI/bge-small-zh-v1.5（512维，中文优化）
- **相似度计算**: 余弦相似度（基于 NumPy）
- **存储方式**: 内存存储（重启后清空）

### 文本分块策略
- 块大小：500字符
- 重叠：100字符
- 自动过滤空白块

### 支持的文件类型
- `.txt` - 纯文本文件
- `.md` - Markdown 文件
- `.pdf` - PDF 文档（支持中文和英文）

### 应用场景
- 检索增强生成 (RAG)
- 语义搜索
- 文档相似性检测
- 智能问答系统

## ⚠️ 注意事项

- 📂 上传的文件默认保存在 `./uploads` 目录
- 🧠 向量数据存储在内存中，重启服务后会清空
- 📄 PDF 文本提取可能无法处理所有特殊格式的 PDF
- 🔒 建议在生产环境中添加文件大小限制和安全验证
- 🌐 首次运行会自动下载嵌入模型（约95MB），请确保网络通畅
- 📦 如果网络受限，可以手动下载模型并指定路径

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- 项目地址: https://github.com/Absoluking/claude-code
- 问题反馈: [GitHub Issues](https://github.com/Absoluking/claude-code/issues)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
