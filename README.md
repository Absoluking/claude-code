# FastAPI File Upload Service

一个功能强大的 FastAPI 文件上传服务，支持上传 Markdown (.md)、PDF (.pdf) 和文本 (.txt) 文件，并内置**语义检索能力**。

## 功能特性

### 基础功能
- ✅ 支持上传 .md、.pdf、.txt 文件
- ✅ 自动保存上传的文件到 ./uploads 目录
- ✅ PDF 文件使用 pypdf 提取文本内容
- ✅ Markdown 和 TXT 文件直接读取文本内容
- ✅ RESTful API 设计

### 🔍 向量数据库集成
- ✅ 自动文本分块（500字符/块，100字符重叠）
- ✅ 使用 BAAI/bge-small-zh-v1.5 中文嵌入模型
- ✅ 自定义内存向量存储，基于 NumPy 实现
- ✅ 余弦相似度语义搜索
- ✅ 支持 RAG（检索增强生成）应用场景

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 接口说明

### 上传文件

**接口**: `POST /upload`

**参数**:
- `file`: 上传的文件 (支持 .md, .pdf, .txt)

**响应**:
```json
{
  "filename": "example.md",
  "filepath": "./uploads/example.md",
  "file_size": 1024,
  "content": "文件内容...",
  "chunks_count": 2
}
```

### LLM 智能问答

**接口**: `POST /ask`

**参数**: `question` (query parameter)

**响应**:
```json
{
  "question": "你的问题",
  "answer": "根据提供的上下文信息，这里是准确的答案...",
  "model": "glm-4.7-flash"
}
```

**工作流程**:
1. 向量检索：从上传的文件中检索最相关的 3 个文本块
2. 提示词构建：将检索结果和用户问题组合成 RAG 提示词
3. LLM 生成：调用 LLM 根据上下文生成自然语言答案

### 健康检查

**接口**: `GET /health`

**响应**:
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

## LLM 配置

本项目使用 OpenAI 兼容的 API 接口调用本地 LLM 服务。通过环境变量配置：

### 环境变量

```bash
# LLM 服务地址（必需）
ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1

# 认证令牌（必需）
ANTHROPIC_AUTH_TOKEN=your-auth-token-here

# 模型名称（必需，默认：glm-4.7-flash）
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

创建 `.env` 文件（可选）：
```env
ANTHROPIC_BASE_URL=http://127.0.0.1:8000/v1
ANTHROPIC_AUTH_TOKEN=test-token-123
ANTHROPIC_MODEL=glm-4.7-flash
```

然后在代码中加载：
```python
from dotenv import load_dotenv
load_dotenv()
```

## 测试上传

可以使用 curl 或其他 HTTP 客户端测试：

```bash
# 上传 TXT 文件
curl -X POST "http://localhost:8000/upload" -F "file=@test.txt"

# 上传 Markdown 文件
curl -X POST "http://localhost:8000/upload" -F "file=@README.md"

# 上传 PDF 文件
curl -X POST "http://localhost:8000/upload" -F "file=@example.pdf"
```

## 测试语义搜索

上传文件后，可以使用语义搜索功能提问：

```bash
# 检查健康状态
curl http://localhost:8000/health

# 提问（使用 GET 或 POST + query parameter）
curl -X POST -G "http://localhost:8000/ask" --data-urlencode "question=FastAPI 的特点是什么？"
curl -X POST "http://localhost:8000/ask?question=向量数据库有什么应用？"
```

## 项目结构

```
fastapi-file-upload/
├── main.py           # 主应用文件（包含向量存储实现）
├── requirements.txt  # 依赖列表
├── README.md         # 项目说明
├── test_server.py    # 自动化测试脚本
└── uploads/          # 上传文件保存目录
```

## 向量数据库说明

本项目使用自定义的内存向量存储实现，无需额外的向量数据库依赖：

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
- 问答系统

## 注意事项

- 上传的文件默认保存在 `./uploads` 目录
- 向量数据存储在内存中，重启服务后会清空
- PDF 文本提取可能无法处理所有特殊格式的 PDF
- 建议在生产环境中添加文件大小限制和安全验证
- 首次运行会自动下载嵌入模型（约95MB），请确保网络通畅
