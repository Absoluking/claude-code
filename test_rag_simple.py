"""
简单的 RAG 测试脚本
"""
import requests
import os

# 设置正确的 LLM API 配置
os.environ['ANTHROPIC_BASE_URL'] = 'https://open.bigmodel.cn/api/paas/v4'
os.environ['ANTHROPIC_AUTH_TOKEN'] = '61965768265f46f581a45aa9d91be121.BBmentHLsM1rwjdL'
os.environ['ANTHROPIC_MODEL'] = 'glm-4-flash'

BASE_URL = "http://localhost:8000"

print('=== Test RAG Flow ===')
print(f'LLM API: {os.environ["ANTHROPIC_BASE_URL"]}')
print(f'Model: {os.environ["ANTHROPIC_MODEL"]}')
print()

# Test 1: Upload file
print('1. Uploading test file...')
content = '''向量数据库是一种用于存储和检索向量嵌入的数据库系统。
RAG（Retrieval-Augmented Generation）结合了信息检索和生成式 AI。
ChromaDB 是流行的开源向量数据库。
嵌入模型将文本转换为向量表示。'''
files = {'file': ('rag.txt', content)}
resp = requests.post(f'{BASE_URL}/upload', files=files)
if resp.status_code == 200:
    print('   File uploaded successfully')
    print(f'   Chunks: {resp.json()["chunks_count"]}')
else:
    print(f'   Failed: {resp.status_code}')
print()

# Test 2: Ask question
print('2. Asking question...')
question = '什么是向量数据库？'
payload = {'question': question}
resp = requests.post(f'{BASE_URL}/ask', json=payload)

print(f'   Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'   Model: {data["model"]}')
    print(f'   Retrieved chunks: {data["results_count"]}')
    print(f'   Answer: {data["answer"][:150]}...')
    print()
    print('   Full Answer:')
    print('-' * 60)
    print(data['answer'])
    print('-' * 60)
else:
    print(f'   Error: {resp.text}')
