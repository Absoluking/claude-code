#!/usr/bin/env python
"""Test script for the FastAPI vector store integration"""
import subprocess
import time
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_upload():
    """Test upload endpoint"""
    print("\n=== Testing Upload Endpoint ===")

    # Create a test file
    test_content = """
    这是一个测试文件，用于测试向量数据库集成。

    该服务使用 HuggingFace 的嵌入模型 BAAI/bge-small-zh-v1.5 对上传的文件进行语义索引。
    文本会被分割成 500 字符的块，块之间有 100 字符的重叠。

    支持的文件类型包括：.txt, .md, .pdf
    """

    files = {'file': ('test_file.txt', test_content, 'text/plain')}
    response = requests.post(f"{BASE_URL}/upload", files=files)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_ask():
    """Test ask endpoint"""
    print("\n=== Testing Ask Endpoint ===")

    # First check if we have documents uploaded
    health_response = requests.get(f"{BASE_URL}/health")
    if health_response.json().get('documents_in_store', 0) == 0:
        print("No documents in store. Skipping ask test.")
        return True

    question = "这个文件的功能是什么？"
    payload = {"question": question}

    response = requests.post(f"{BASE_URL}/ask", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"Question: {question}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("Starting server test...")

    # Start the server
    process = subprocess.Popen(
        ['python', 'main.py'],
        cwd='E:\\claude code\\fastapi-file-upload',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print("Waiting for server to start (this may take a minute to load the model)...")
    time.sleep(25)  # Wait for server to start and model to load

    try:
        # Run tests
        results = []
        results.append(("Root", test_root()))
        results.append(("Health", test_health()))
        results.append(("Upload", test_upload()))
        results.append(("Ask", test_ask()))

        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {name}")

        all_passed = all(r[1] for r in results)
        print("="*50)
        if all_passed:
            print("All tests passed!")
        else:
            print("Some tests failed!")
        print("="*50)

    finally:
        # Stop the server
        print("\nStopping server...")
        process.terminate()
        time.sleep(2)
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    main()
