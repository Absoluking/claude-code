"""
查找正确的 LLM API 端点
"""
import requests

# 尝试不同的可能的端点
base_url = "https://open.bigmodel.cn/api/anthropic"
api_key = "61965768265f46f581a45aa9d91be121.BBmentHLsM1rwjdL"
model = "glm-4.7-flash"

endpoints = [
    "/chat/completions",
    "/v1/chat/completions",
    "/v3/chat/completions",
    "/v4/chat/completions",
    "/api/anthropic/v1/chat/completions",
    "/api/anthropic/chat/completions",
]

for endpoint in endpoints:
    url = base_url + endpoint
    print(f"\nTesting: {url}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Success: {result.get('success', 'N/A')}")
            print(f"  Message: {result.get('msg', 'N/A')}")
            if 'choices' in result:
                print(f"  Choices: {len(result['choices'])}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {str(e)}")
