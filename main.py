from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from rag_manager import RAGStoryManager

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama API配置
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.5"

# 剧情数据
story_data = {
    "scenes": {
        "village": {
            "name": "青牛镇",
            "description": "一个宁静的山村，位于青云山脚下，是通往青云门的必经之路",
            "npcs": ["老者", "村民甲", "药铺老板"]
        },
        "mountain": {
            "name": "青云山",
            "description": "云雾缭绕的修仙圣地，青云门所在地，山巅有千年古刹",
            "npcs": ["掌门", "师兄", "师姐", "扫地僧"]
        },
        "cave": {
            "name": "神秘洞穴",
            "description": "青云山后山的一处隐秘洞穴，据说藏有上古传承",
            "npcs": ["神秘老人", "守护兽"]
        }
    },
    "npcs": {
        "老者": {
            "name": "老者",
            "personality": "慈祥、见多识广、乐于助人",
            "backstory": "青牛镇的老居民，曾经是青云门的外门弟子，因资质有限未能更进一步",
            "dialogues": [
                {
                    "id": 1,
                    "text": "年轻人，你是第一次来青牛镇吧？看你骨骼清奇，似乎不是普通人。老朽在这镇上住了几十年，见过不少像你这样的求道之人。",
                    "options": [
                        "是的，前辈，我是来寻找修仙之路的",
                        "晚辈听说青云门招收弟子，特来一试",
                        "请问前辈，这里就是青云门吗？"
                    ]
                },
                {
                    "id": 2,
                    "text": "哈哈，这里可不是青云门，只是山脚下的一个小镇。不过要上青云门，得先经过老朽这一关。修仙之路讲究缘分，你可有什么机缘？",
                    "options": [
                        "晚辈只是听闻青云门大名，特来拜师",
                        "说来惭愧，晚辈昨夜梦见仙人指路",
                        "机缘？晚辈不懂，还请前辈明示"
                    ]
                },
                {
                    "id": 3,
                    "text": "修仙界广袤无垠，门派林立。青云门是附近最大的门派，但入门要求极高。你且说说，为何想修仙？",
                    "options": [
                        "为了长生不老",
                        "为了保护重要的人",
                        "为了探索这世间的奥秘"
                    ]
                },
                {
                    "id": 4,
                    "text": "（捋了捋胡须）长生者，需有坚韧道心；护人者，需有足够实力；求知者，需有慧根灵性。你既然有这份心气，不妨先测测灵根。",
                    "options": [
                        "灵根是什么？如何测试？",
                        "晚辈愿意测试，请前辈指点",
                        "在此之前，晚辈想了解更多"
                    ]
                },
                {
                    "id": 5,
                    "text": "（指向镇外一处微微发光的方向）镇东有一座废弃的聚灵台，虽已荒废，但仍能感应灵根。你若有心，可去一试。记住，修仙之路，九死一生，需有决心。",
                    "options": [
                        "多谢前辈指引，晚辈这就去试试",
                        "前辈不随晚辈同去吗？",
                        "晚辈想先在镇上逛逛"
                    ]
                }
            ]
        },
        "村民甲": {
            "name": "村民甲",
            "personality": "热情、朴实、好奇",
            "backstory": "青牛镇的普通村民，世代居住于此",
            "dialogues": [
                {
                    "id": 1,
                    "text": "嘿，外乡人，第一次来我们青牛镇吧？",
                    "options": [
                        "是的，请问这里有什么好去处？",
                        "我是来修仙的",
                        "请问青云门怎么走？"
                    ]
                }
            ]
        },
        "药铺老板": {
            "name": "药铺老板",
            "personality": "精明、势利、见多识广",
            "backstory": "青牛镇药铺的老板，经常与修仙者打交道",
            "dialogues": [
                {
                    "id": 1,
                    "text": "客官，要点什么药材？我这里有上好的百年人参。",
                    "options": [
                        "我是来问路的",
                        "修仙需要什么药材？",
                        "听说青云门要招收弟子了？"
                    ]
                }
            ]
        },
        "掌门": {
            "name": "青云子",
            "personality": "威严、公正、看重资质",
            "backstory": "青云门掌门，金丹期修士，掌管门派已有百年",
            "dialogues": [
                {
                    "id": 1,
                    "text": "来者何人？竟敢擅闯青云门！",
                    "options": [
                        "晚辈是来拜师的",
                        "晚辈仰慕青云门已久",
                        "请掌门收我为徒"
                    ]
                },
                {
                    "id": 2,
                    "text": "修仙之道，讲究缘分与资质。你可知我青云门的入门要求？",
                    "options": [
                        "请掌门赐教",
                        "晚辈愿接受任何考验",
                        "资质重要还是努力重要？"
                    ]
                }
            ]
        },
        "师兄": {
            "name": "林峰",
            "personality": "开朗、热心、好胜",
            "backstory": "青云门内门弟子，筑基期修士，入门已有十年",
            "dialogues": [
                {
                    "id": 1,
                    "text": "师弟（师妹），第一次来青云门吧？有什么需要帮忙的吗？",
                    "options": [
                        "请问如何才能拜入青云门？",
                        "师兄，修仙苦吗？",
                        "青云门有哪些修行法门？"
                    ]
                }
            ]
        },
        "师姐": {
            "name": "林小婉",
            "personality": "温柔、善良、细心",
            "backstory": "青云门内门弟子，筑基期修士，擅长炼丹",
            "dialogues": [
                {
                    "id": 1,
                    "text": "你好，看你面生，是来参加入门测试的吧？",
                    "options": [
                        "是的，师姐",
                        "请问入门测试难吗？",
                        "师姐是怎么加入青云门的？"
                    ]
                }
            ]
        },
        "神秘老人": {
            "name": "神秘老人",
            "personality": "神秘、高深、孤傲",
            "backstory": "隐居在神秘洞穴中的大能，疑似元婴期修士",
            "dialogues": [
                {
                    "id": 1,
                    "text": "有趣，居然有人能找到这里。你是如何发现这个洞穴的？",
                    "options": [
                        "晚辈误打误撞来到这里",
                        "晚辈追寻上古传承而来",
                        "请问前辈是何方神圣？"
                    ]
                }
            ]
        }
    },
    "story_arcs": [
        {
            "id": 1,
            "name": "初入仙途",
            "description": "从凡人到修仙者的第一步",
            "scenes": ["village", "mountain"],
            "tasks": [
                "与青牛镇老者交谈",
                "前往青云门",
                "通过入门测试",
                "拜入青云门"
            ]
        },
        {
            "id": 2,
            "name": "秘境探险",
            "description": "发现神秘洞穴，获得上古传承",
            "scenes": ["mountain", "cave"],
            "tasks": [
                "在后山发现神秘洞穴",
                "战胜守护兽",
                "获得上古传承",
                "返回青云门"
            ]
        }
    ]
}

# 对话管理系统
class DialogueManager:
    def __init__(self):
        self.story_data = story_data
        self.current_story_arc = 1  # 当前剧情弧
        self.rag_manager = RAGStoryManager()
        self.player_states = {}  # 存储玩家状态
    
    def get_npc_dialogues(self, npc_name):
        if npc_name in self.story_data["npcs"]:
            return self.story_data["npcs"][npc_name]["dialogues"]
        return []
    
    def generate_response(self, npc_name, player_input, dialogue_history, player_id="default"):
        npc = self.story_data["npcs"].get(npc_name)
        if not npc:
            return "抱歉，我不认识这个人。"
        
        # 获取或初始化玩家状态
        if player_id not in self.player_states:
            self.player_states[player_id] = {
                "completed_nodes": [],
                "inventory": [],
                "current_scene": "village"
            }
        
        player_state = self.player_states[player_id]
        
        # 使用RAG系统处理对话
        rag_result = self.rag_manager.process_dialogue(
            npc_name, 
            player_input, 
            dialogue_history, 
            player_state
        )
        
        # 如果RAG返回关键剧情或引导剧情，直接使用
        if rag_result["回复类型"] in ["关键剧情", "引导剧情"]:
            # 更新玩家状态
            if rag_result.get("节点ID"):
                self.rag_manager.update_player_state(player_state, rag_result["节点ID"])
            
            response = rag_result["回复内容"]
            
            # 如果有奖励，添加到回复中
            if rag_result.get("奖励"):
                reward_text = "\n\n【系统提示】" + "、".join(rag_result["奖励"])
                response += reward_text
            
            return response
        
        # 否则使用AI自由对话
        return self._generate_free_response(npc, player_input, dialogue_history, rag_result.get("角色设定", {}))
    
    def _generate_free_response(self, npc, player_input, dialogue_history, character_setting):
        # 获取当前剧情弧
        current_arc = self.story_data["story_arcs"][self.current_story_arc - 1]
        
        # 构建AI提示
        prompt = f"你是{npc['name']}，{npc['personality']}。{npc['backstory']}。\n"
        
        # 添加角色设定
        if character_setting:
            prompt += f"性格特点：{', '.join(character_setting.get('性格', []))}\n"
            prompt += f"说话风格：{character_setting.get('说话风格', '')}\n"
            prompt += f"常用词汇：{', '.join(character_setting.get('常用词汇', []))}\n"
            if character_setting.get('禁忌话题'):
                prompt += f"禁忌话题：{', '.join(character_setting.get('禁忌话题', []))}\n"
        
        prompt += "你正在和一个想要修仙的年轻人对话。\n"
        prompt += f"当前剧情：{current_arc['name']} - {current_arc['description']}\n"
        prompt += "你的任务是：\n"
        prompt += "1. 保持符合你人格的对话风格\n"
        prompt += "2. 自然地回答玩家的问题\n"
        prompt += "3. 使用符合修仙世界的语言和表达方式\n"
        prompt += "4. 不要说任何现代或不符合修仙世界的内容\n"
        prompt += "5. 保持对话的趣味性和互动性\n"
        prompt += "对话历史：\n"
        
        # 只保留最近的10条对话，避免提示过长
        recent_history = dialogue_history[-10:]
        for msg in recent_history:
            if msg["speaker"] == "player":
                prompt += f"年轻人：{msg['text']}\n"
            else:
                prompt += f"{npc['name']}：{msg['text']}\n"
        
        prompt += f"年轻人：{player_input}\n"
        prompt += f"{npc['name']}："
        
        # 调用Ollama API
        try:
            print(f"调用Ollama API，模型: {MODEL_NAME}")
            print(f"提示长度: {len(prompt)}")
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,  # 禁用thinking模式
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 800  # 增加生成token数量，确保回复完整
                    }
                },
                timeout=60  # 添加60秒超时
            )
            print(f"Ollama API响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"Ollama API响应: {result}")
            response_text = result.get("response", "").strip()
            print(f"返回响应: '{response_text}'")
            return response_text if response_text else "抱歉，我暂时无法回答你的问题。"
        except requests.exceptions.Timeout:
            print("Ollama API超时")
            return "抱歉，AI思考时间过长，请稍后再试。"
        except Exception as e:
            print(f"Ollama API error: {e}")
            import traceback
            traceback.print_exc()
            return "抱歉，我暂时无法回答你的问题。"
    
    def get_player_state(self, player_id="default"):
        return self.player_states.get(player_id, {
            "completed_nodes": [],
            "inventory": [],
            "current_scene": "village"
        })

dialogue_manager = DialogueManager()

# API端点
@app.get("/api/scenes")
def get_scenes():
    return story_data["scenes"]

@app.get("/api/npcs/{npc_name}/dialogues")
def get_npc_dialogues(npc_name: str):
    dialogues = dialogue_manager.get_npc_dialogues(npc_name)
    if not dialogues:
        raise HTTPException(status_code=404, detail="NPC not found")
    return dialogues

@app.post("/api/npcs/{npc_name}/chat")
def chat_with_npc(npc_name: str, data: dict):
    player_input = data.get("input", "")
    dialogue_history = data.get("history", [])
    player_id = data.get("player_id", "default")
    
    response = dialogue_manager.generate_response(npc_name, player_input, dialogue_history, player_id)
    return {"response": response}

@app.get("/api/player/state")
def get_player_state(player_id: str = "default"):
    return dialogue_manager.get_player_state(player_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
