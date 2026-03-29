import requests

# 测试获取场景列表
print("测试获取场景列表...")
try:
    response = requests.get("http://localhost:8002/api/scenes")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试获取NPC对话
print("\n测试获取NPC对话...")
try:
    response = requests.get("http://localhost:8002/api/npcs/老者/dialogues")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试对话功能
print("\n测试对话功能...")
try:
    response = requests.post(
        "http://localhost:8002/api/npcs/老者/chat",
        json={
            "input": "我是来拜师学艺的",
            "history": []
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
