"""
测试 LLM 集成的脚本

使用前请确保：
1. 后端服务正在运行（python main.py）
2. LLM 服务已启动并可访问（ANTHROPIC_BASE_URL）
3. 环境变量已正确配置
"""

import requests
import json
import time

# 配置
API_BASE = "http://localhost:8000"

def check_health():
    """检查服务健康状态"""
    print("=" * 60)
    print("1. 检查服务健康状态")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/health")
        data = response.json()

        print(f"✓ 状态: {data.get('status')}")
        print(f"✓ 文档数量: {data.get('documents_in_store')}")
        print(f"✓ LLM 可用: {data.get('llm_available')}")
        if data.get('llm_available'):
            print(f"✓ 模型: {data.get('llm_model')}")
            print(f"✓ 服务地址: {data.get('llm_base_url')}")
        print()

        return data.get('llm_available', False)
    except Exception as e:
        print(f"✗ 错误: {e}")
        print()
        return False

def upload_test_file():
    """上传测试文件"""
    print("=" * 60)
    print("2. 上传测试文件")
    print("=" * 60)

    # 创建测试文件内容
    test_content = """
    FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API，基于 Python 标准类型提示。

    它具有以下特点：
    1. 快速：基于 Starlette 和 Pydantic 极速开发
    2. 独立部署：代码与框架解耦
    3. 自动生成 API 文档：Swagger UI 和 ReDoc

    FastAPI 支持异步处理，可以使用 async/await 语法来提高性能。
    """

    try:
        files = {'file': ('test_file.txt', test_content, 'text/plain')}
        response = requests.post(f"{API_BASE}/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ 文件上传成功: {data['filename']}")
            print(f"✓ 文件大小: {data['file_size']} 字节")
            print(f"✓ 文本块数量: {data['chunks_count']}")
            print(f"✓ 保存路径: {data['filepath']}")
            print()
            return True
        else:
            print(f"✗ 上传失败: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def ask_question(question):
    """提问并获取 LLM 答案"""
    print("=" * 60)
    print("3. 提问测试")
    print("=" * 60)
    print(f"问题: {question}")
    print("-" * 60)

    try:
        response = requests.post(f"{API_BASE}/ask", params={'question': question})

        if response.status_code == 200:
            data = response.json()
            print(f"✓ 问题: {data['question']}")
            print(f"✓ 模型: {data.get('model', 'N/A')}")
            print()
            print("回答:")
            print("-" * 60)
            print(data['answer'])
            print("-" * 60)
            print()
            return True
        else:
            print(f"✗ 请求失败: {response.json()}")
            print()
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        print()
        return False

def main():
    """主测试流程"""
    print("\n🚀 LLM 集成测试脚本")
    print()

    # 检查 LLM 是否可用
    if not check_health():
        print("⚠️  LLM 服务不可用，请检查环境变量配置")
        print("   ANTHROPIC_BASE_URL: http://127.0.0.1:8000/v1")
        print("   ANTHROPIC_AUTH_TOKEN: 你的令牌")
        print("   ANTHROPIC_MODEL: glm-4.7-flash")
        return

    # 上传测试文件
    if not upload_test_file():
        print("⚠️  文件上传失败，跳过提问测试")
        return

    # 等待 1 秒
    time.sleep(1)

    # 测试问题
    questions = [
        "FastAPI 的特点是什么？",
        "请总结一下这个文档的主要内容。",
    ]

    # 依次提问
    for i, q in enumerate(questions, 1):
        print(f"\n【测试问题 {i}/{len(questions)}】")
        ask_question(q)
        time.sleep(1)  # 避免请求过于频繁

    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
