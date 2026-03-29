import requests

# 测试RAG系统
print("=== 测试RAG系统 ===\n")

# 测试1: 剧情相关对话（应该触发RAG）
print("测试1: 剧情相关对话 - 我想拜师学艺")
response1 = requests.post(
    "http://localhost:8002/api/npcs/老者/chat",
    json={
        "input": "我想拜师学艺",
        "history": [],
        "player_id": "test_player_1"
    }
)
print(f"状态码: {response1.status_code}")
result1 = response1.json()
print(f"回复: {result1['response'][:100]}...")
print()

# 查看玩家状态
print("查看玩家状态1")
response1_state = requests.get("http://localhost:8002/api/player/state?player_id=test_player_1")
print(f"状态码: {response1_state.status_code}")
state1 = response1_state.json()
print(f"玩家状态: {state1}")
print()

# 测试2: 触发下一个剧情节点
print("测试2: 触发下一个剧情节点 - 聚灵台在哪里？")
response2 = requests.post(
    "http://localhost:8002/api/npcs/老者/chat",
    json={
        "input": "聚灵台在哪里？",
        "history": [],
        "player_id": "test_player_1"
    }
)
print(f"状态码: {response2.status_code}")
result2 = response2.json()
print(f"回复: {result2['response'][:100]}...")
print()

# 再次查看玩家状态
print("查看玩家状态2")
response2_state = requests.get("http://localhost:8002/api/player/state?player_id=test_player_1")
print(f"状态码: {response2_state.status_code}")
state2 = response2_state.json()
print(f"玩家状态: {state2}")
print()

# 测试3: 自由对话
print("测试3: 自由对话 - 今天天气真好")
response3 = requests.post(
    "http://localhost:8002/api/npcs/老者/chat",
    json={
        "input": "今天天气真好",
        "history": [],
        "player_id": "test_player_1"
    }
)
print(f"状态码: {response3.status_code}")
result3 = response3.json()
print(f"回复: {result3['response'][:100]}...")
print()

print("\n=== 测试完成 ===")
