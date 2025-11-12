import requests

def test_api_access():
    """测试不同方式访问API"""

    print("=== API访问测试 ===")

    # 1. 直接访问Django服务
    print("\n1. 直接访问Django服务 (http://localhost:8020):")
    try:
        response = requests.get('http://localhost:8020/api/courses/lessons/')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")

    # 2. 通过nginx代理访问
    print("\n2. 通过nginx代理访问 (http://localhost):")
    try:
        response = requests.get('http://localhost/api/courses/lessons/')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"错误: {e}")

    # 3. 测试课程详情API
    print("\n3. 测试课程详情API:")
    try:
        response = requests.get('http://localhost:8020/api/courses/courses/day2130-day01/')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_api_access()