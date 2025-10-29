# tool_of_test.py
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api(endpoint, method="GET", data=None, headers=None):
    """测试真实API连接"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"不支持的HTTP方法: {method}")
            return None

        print(f"\n{'=' * 60}")
        print(f"测试接口: {method} {endpoint}")
        if data:
            print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")

        try:
            result = response.json()
            print("返回数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print(f"响应内容: {response.text}")

        print(f"{'=' * 60}")

        return response.json() if response.text else None

    except Exception as e:
        print(f"请求失败: {e}")
        return None

