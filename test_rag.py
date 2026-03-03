"""
RAG 流程测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def setup_rag():
    """设置 RAG 环境：上传测试文件"""
    print("=" * 70)
    print("设置 RAG 环境：上传测试文件")
    print("=" * 70)

    # 创建测试文档内容
    test_content = """
向量数据库（Vector Database）是一种用于存储和检索向量嵌入（embeddings）的数据库系统。
它主要用于语义搜索、推荐系统和相似性搜索等场景。

RAG（Retrieval-Augmented Generation）是一种结合了信息检索和生成式 AI 的技术。
通过从知识库中检索相关信息，然后将其提供给大语言模型，从而生成更准确、更上下文相关的回答。

ChromaDB 是一个流行的开源向量数据库，支持 Python 和 JavaScript。
它提供了简单易用的 API，可以轻松集成到各种应用中。

嵌入模型将文本转换为向量表示，使计算机能够理解文本的语义。
常用的中文嵌入模型包括 BAAI/bge-small-zh-v1.5 和 BAAI/bge-m3 等。
    """.strip()

    # 上传文件
    files = {"file": ("rag_test.txt", test_content)}
    response = requests.post(f"{BASE_URL}/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 文件上传成功")
        print(f"   文件名: {data['filename']}")
        print(f"   文本块数: {data['chunks_count']}")
        print(f"   内容预览: {data['content'][:100]}...")
        return True
    else:
        print(f"❌ 文件上传失败: {response.status_code}")
        print(f"   错误: {response.text}")
        return False

def test_rag_flow():
    """测试完整的 RAG 流程"""
    print("\n" + "=" * 70)
    print("测试完整的 RAG 流程")
    print("=" * 70)

    # 问题列表
    questions = [
        "什么是向量数据库？",
        "RAG 技术的工作原理是什么？",
        "ChromaDB 有什么特点？",
        "常用的中文嵌入模型有哪些？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- 问题 {i}: {question} ---")

        payload = {"question": question}
        print(f"发送请求到 {BASE_URL}/ask...")

        response = requests.post(f"{BASE_URL}/ask", json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"状态: ✅ 成功")
            print(f"模型: {data.get('model', 'N/A')}")
            print(f"检索到的上下文块数: {data.get('results_count', 0)}")
            print(f"\n答案:")
            print("-" * 60)
            # 限制显示长度
            answer = data.get('answer', '')
            print(answer[:300] + "..." if len(answer) > 300 else answer)
            print("-" * 60)
        else:
            print(f"状态: ❌ 失败 ({response.status_code})")
            try:
                error_data = response.json()
                print(f"错误: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"错误: {response.text}")

def test_health():
    """测试服务健康状态"""
    print("\n" + "=" * 70)
    print("服务健康检查")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/health")
    data = response.json()

    print(f"服务状态: {data.get('status', 'Unknown')}")
    print(f"集合名称: {data.get('collections', 'Unknown')}")
    print(f"文档数量: {data.get('documents_in_store', 0)}")
    print(f"嵌入模型: {data.get('embedding_model', 'Unknown')}")
    print(f"向量维度: {data.get('embedding_dimension', 'Unknown')}")
    print(f"LLM 可用: {'是' if data.get('llm_available') else '否'}")
    if data.get('llm_available'):
        print(f"LLM 模型: {data.get('llm_model', 'Unknown')}")
        print(f"LLM 地址: {data.get('llm_base_url', 'Unknown')}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RAG 流程测试套件")
    print("=" * 70)

    try:
        # 1. 测试健康检查
        test_health()

        # 2. 设置环境
        if setup_rag():
            # 3. 测试 RAG 流程
            test_rag_flow()

        print("\n" + "=" * 70)
        print("✅ RAG 流程测试完成！")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print("请确保 main.py 正在运行: python main.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
