# FastAPI File Upload Service

一个简单的 FastAPI 文件上传服务，支持上传 Markdown (.md)、PDF (.pdf) 和文本 (.txt) 文件。

## 功能特性

- ✅ 支持上传 .md、.pdf、.txt 文件
- ✅ 自动保存上传的文件到 ./uploads 目录
- ✅ PDF 文件使用 pypdf 提取文本内容
- ✅ Markdown 和 TXT 文件直接读取文本内容
- ✅ RESTful API 设计

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
  "content": "文件内容..."
}
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

## 项目结构

```
fastapi-file-upload/
├── main.py           # 主应用文件
├── requirements.txt  # 依赖列表
├── README.md         # 项目说明
└── uploads/          # 上传文件保存目录
```

## 注意事项

- 上传的文件默认保存在 `./uploads` 目录
- PDF 文本提取可能无法处理所有特殊格式的 PDF
- 建议在生产环境中添加文件大小限制和安全验证
