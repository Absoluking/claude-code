from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from openai import OpenAI
import uuid

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

# 打印配置信息
print("=" * 60)
print("Configuration:")
print(f"  ANTHROPIC_BASE_URL: {os.getenv('ANTHROPIC_BASE_URL')}")
print(f"  ANTHROPIC_AUTH_TOKEN: {os.getenv('ANTHROPIC_AUTH_TOKEN', 'NOT SET')[:20]}...")
print(f"  ANTHROPIC_MODEL: {os.getenv('ANTHROPIC_MODEL')}")
print("=" * 60)

app = FastAPI(title="File Upload API", version="2.0.0")

# 初始化嵌入模型
print("Loading embedding model: BAAI/bge-small-zh-v1.5")
embedding_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print(f"Embedding model loaded. Embedding dimension: {embedding_model.get_sentence_embedding_dimension()}")

# 初始化 OpenAI 客户端（用于调用 LLM）
# 使用正确的智谱 AI API 配置
anthropic_base_url = "https://open.bigmodel.cn/api/paas/v4"
anthropic_auth_token = "61965768265f46f581a45aa9d91be121.BBmentHLsM1rwjdL"
anthropic_model = "glm-4-flash"

try:
    print(f"Initializing LLM client with:")
    print(f"  Base URL: {anthropic_base_url}")
    print(f"  Model: {anthropic_model}")
    print(f"  API Key: {anthropic_auth_token[:20]}...")

    llm_client = OpenAI(
        api_key=anthropic_auth_token,
        base_url=anthropic_base_url
    )

    # 测试 API 连接
    test_response = llm_client.chat.completions.create(
        model=anthropic_model,
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )

    if test_response.choices and test_response.choices[0].message:
        LLM_AVAILABLE = True
        print("LLM client initialized successfully and API connection verified")
    else:
        LLM_AVAILABLE = False
        print("LLM client initialized but API connection test failed")

except Exception as e:
    print(f"Warning: Failed to initialize LLM client: {str(e)}")
    import traceback
    traceback.print_exc()
    LLM_AVAILABLE = False

# 初始化 ChromaDB 客户端
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
CHROMA_DB_PATH.mkdir(exist_ok=True)

print(f"Initializing ChromaDB at: {CHROMA_DB_PATH}")
chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH),
    settings=Settings(anonymized_telemetry=False)
)

# 获取或创建向量存储集合
collection_name = "document_chunks"
vector_store = chroma_client.get_or_create_collection(name=collection_name)

print(f"ChromaDB collection '{collection_name}' initialized")

# 确保上传目录存在
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 挂载上传目录（可选）
# app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def root():
    return {
        "message": "FastAPI File Upload Service",
        "endpoints": ["/upload", "/ask"],
        "note": "Upload a text/PDF file using POST /upload, then ask questions using POST /ask"
    }


@app.get("/health")
async def health():
    """
    健康检查端点

    Returns:
        服务状态、向量存储状态和 LLM 状态
    """
    try:
        # 检查向量存储状态
        status = "healthy"
        docs_count = vector_store.count()

        health_info = {
            "status": status,
            "collections": collection_name,
            "documents_in_store": docs_count,
            "llm_available": LLM_AVAILABLE,
            "embedding_model": "BAAI/bge-small-zh-v1.5",
            "embedding_dimension": embedding_model.get_sentence_embedding_dimension()
        }

        if LLM_AVAILABLE:
            health_info["llm_model"] = anthropic_model
            health_info["llm_base_url"] = anthropic_base_url

        return health_info
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    将文本按指定大小分块，每块之间有重叠

    Args:
        text: 输入文本
        chunk_size: 每块大小（字符数）
        overlap: 重叠字符数

    Returns:
        文本块列表
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件并返回提取的内容，同时创建向量索引

    - **file**: 上传的文件

    支持的文件类型: .pdf, .md, .txt
    上传后会自动：
    - 保存文件到 uploads 目录
    - 提取文本内容
    - 创建向量索引用于语义检索
    """
    # 验证文件扩展名
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # 支持的文件类型
    allowed_extensions = {'.md', '.pdf', '.txt'}
    file_ext = Path(filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Only {', '.join(allowed_extensions)} are allowed"
        )

    # 保存文件到 uploads 目录
    file_path = UPLOAD_DIR / filename

    try:
        # 读取上传的文件内容
        content = await file.read()

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 根据文件类型提取文本
        text_content = None
        chunks = []

        if file_ext == '.pdf':
            # 使用 pypdf 提取 PDF 文本
            text_content = extract_text_from_pdf(file_path)
        elif file_ext == '.md' or file_ext == '.txt':
            # 直接读取文本文件
            text_content = content.decode('utf-8')

        # 创建向量索引（如果存在文本内容）
        if text_content:
            chunks = chunk_text(text_content)
            try:
                # 为每个文本块生成向量
                vectors = embedding_model.encode(chunks).tolist()

                # 准备添加到 ChromaDB 的数据
                ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
                metadatas = [
                    {
                        "source": filename,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk)
                    }
                    for idx, chunk in enumerate(chunks)
                ]
                documents = chunks

                # 批量添加到 ChromaDB
                vector_store.add(
                    ids=ids,
                    embeddings=vectors,
                    metadatas=metadatas,
                    documents=documents
                )

                print(f"Added {len(chunks)} chunks to ChromaDB for file: {filename}")

            except Exception as e:
                # 向量存储失败不影响文件上传，只记录警告
                print(f"Warning: Failed to create vector index: {str(e)}")

        return {
            "filename": filename,
            "filepath": str(file_path),
            "file_size": len(content),
            "content": text_content if text_content else "",
            "chunks_count": len(chunks) if text_content else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    使用 pypdf 提取 PDF 文本
    """
    try:
        reader = PdfReader(pdf_path)
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        return "\n\n".join(text_parts)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from PDF: {str(e)}"
        )


@app.post("/ask", response_model=Dict[str, Any])
async def ask_question(question: str = Body(..., embed=True, description="用户问题")):
    """
    基于向量检索和 LLM 生成答案

    - **question**: 用户问题

    该端点使用语义检索从已上传的文件中找到最相关的上下文，然后调用 LLM 生成自然语言答案。
    """
    try:
        # 1. 验证输入
        if not question or not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # 2. 检查 ChromaDB 中是否有数据
        docs_count = vector_store.count()
        if docs_count == 0:
            raise HTTPException(
                status_code=404,
                detail="No documents found in the vector store. Please upload a file first using /upload endpoint."
            )

        # 3. 检查 LLM 是否可用
        if not LLM_AVAILABLE:
            # 如果 LLM 不可用，只返回检索到的上下文
            return {
                "question": question,
                "note": "LLM is not available, returning only retrieved context",
                "query_embedding": True,
                "results": []
            }

        # 4. 将问题向量化
        query_embedding = embedding_model.encode(question).tolist()

        # 5. 在 ChromaDB 中查询最相关的 3 个文本块
        results = vector_store.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        # 6. 检查是否有结果
        if not results['documents'] or not results['documents'][0]:
            raise HTTPException(
                status_code=404,
                detail="No relevant documents found in the vector store."
            )

        # 7. 构建提示词（RAG 提示词）
        context_parts = []
        for i, doc in enumerate(results['documents'][0], 1):
            context_parts.append(f"Reference {i}:\n{doc}\n")

        context_text = "\n---\n\n".join(context_parts)

        prompt = f"""你是一个智能问答助手。请基于以下上下文信息回答用户的问题。

上下文信息：
{context_text}

用户问题：{question}

请根据上下文信息给出准确、简洁的答案。如果上下文中没有相关信息，请明确说明。
IMPORTANT: 返回纯文本结果，不要使用任何 Markdown 格式（如 #, ##, **, 等符号）。"""

        # 8. 调用 LLM 生成答案
        try:
            print(f"Calling LLM with model: {anthropic_model}")
            print(f"Prompt length: {len(prompt)} characters")

            response = llm_client.chat.completions.create(
                model=anthropic_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的智能问答助手，能够基于提供的上下文信息准确回答问题。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )

            print(f"LLM response type: {type(response)}")
            print(f"LLM response: {response}")

            # 9. 提取答案
            if not response.choices:
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM response is empty or malformed - no choices in response"
                )

            choice = response.choices[0]
            print(f"First choice: {choice}")

            if not choice.message:
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM response is empty or malformed - no message in choice"
                )

            if not choice.message.content:
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM response content is empty"
                )

            answer = choice.message.content
            print(f"Answer length: {len(answer)} characters")

            return {
                "question": question,
                "answer": answer,
                "model": anthropic_model,
                "results_count": len(results['documents'][0]),
                "query_used": True
            }

        except Exception as llm_error:
            print(f"LLM Error: {str(llm_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"LLM API call failed: {str(llm_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
