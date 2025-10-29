# test_real_api.py
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


def test_real_scenarios():
    """测试真实场景"""
    print("🚀 开始真实API测试（连接真实数据库）...")

    # 1. 测试患者登录 - 使用真实患者ID 1 (mao)
    print("\n1. 测试真实患者登录")
    login_data = {
        "username": "1",  # 真实患者ID
        "password": "123456",  # 根据你的AuthService逻辑
        "role": "patient"
    }
    login_result = test_api("/auth/login", "POST", login_data)

    if login_result and login_result.get("code") == 200:
        patient_token = login_result["data"]["token"]
        print(f"✅ 真实登录成功！token: {patient_token[:20]}...")

        # 2. 测试获取真实患者信息
        print("\n2. 测试获取真实患者信息")
        headers = {"Authorization": f"Bearer {patient_token}"}
        profile_result = test_api("/auth/profile", "GET", headers=headers)

        # 验证返回的数据是否与数据库一致
        if profile_result and profile_result.get("code") == 200:
            profile_data = profile_result["data"]
            print(f"✅ 获取到真实患者信息: ID={profile_data['id']}, 姓名={profile_data['name']}")

    # 3. 测试医生登录 - 使用真实医生ID 1
    print("\n3. 测试真实医生登录")
    doctor_login_data = {
        "username": "1",  # 真实医生ID
        "password": "123456",
        "role": "doctor"
    }
    doctor_login = test_api("/auth/login", "POST", doctor_login_data)

    if doctor_login and doctor_login.get("code") == 200:
        doctor_token = doctor_login["data"]["token"]

        # 4. 测试获取真实医生信息
        print("\n4. 测试获取真实医生信息")
        headers = {"Authorization": f"Bearer {doctor_token}"}
        doctor_profile = test_api("/auth/profile", "GET", headers=headers)

        if doctor_profile and doctor_profile.get("code") == 200:
            doctor_data = doctor_profile["data"]
            print(f"✅ 获取到真实医生信息: ID={doctor_data['id']}, 姓名={doctor_data['name']}")


if __name__ == "__main__":
    test_real_scenarios()
    print("\n🎉 真实API测试完成！")