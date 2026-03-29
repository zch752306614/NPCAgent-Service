from sentence_transformers import SentenceTransformer
import chromadb
import json
from typing import List, Dict, Optional
import os

class RAGStoryManager:
    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        try:
            self.embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"加载嵌入模型失败: {e}")
            print("使用备用模型...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="story_nodes",
            metadata={"hnsw:space": "cosine"}
        )
        self.story_knowledge = self._load_story_knowledge()
        self._initialize_knowledge_base()
    
    def _load_story_knowledge(self) -> Dict:
        return {
            "剧情节点": [
                {
                    "节点ID": "village_001",
                    "节点类型": "关键节点",
                    "前置条件": [],
                    "触发关键词": ["拜师", "入门", "修仙", "求道", "学艺"],
                    "剧情描述": "老者引导玩家了解修仙基础",
                    "NPC回复模板": "（慈祥地看着你）年轻人有志向，修仙之路虽艰险，但若心诚，必有所成。老朽当年也是从青云门外门弟子做起，虽资质平平，但也略知一二。",
                    "下一步剧情": ["village_002"],
                    "奖励": ["获得：修仙入门知识"],
                    "失败后果": ["无法进入青云门"]
                },
                {
                    "节点ID": "village_002",
                    "节点类型": "关键节点",
                    "前置条件": ["village_001"],
                    "触发关键词": ["聚灵台", "灵根", "测试", "测灵"],
                    "剧情描述": "玩家在聚灵台测试灵根",
                    "NPC回复模板": "（指向镇东方向）镇东有一座废弃的聚灵台，虽已荒废，但仍能感应灵根。你若有心，可去一试。记住，修仙之路，九死一生，需有决心。",
                    "下一步剧情": ["village_003", "village_004"],
                    "奖励": ["获得：灵根测试结果"],
                    "分支条件": {
                        "灵根优秀": "village_003",
                        "灵根普通": "village_004",
                        "无灵根": "village_005"
                    }
                },
                {
                    "节点ID": "village_003",
                    "节点类型": "引导节点",
                    "前置条件": ["village_002"],
                    "触发关键词": ["功法", "修炼", "法术", "技能"],
                    "剧情描述": "传授基础功法",
                    "NPC回复模板": "（欣慰地点头）既然你有此天赋，老夫便传你一套《基础吐纳诀》，助你推开这第一扇仙门。",
                    "下一步剧情": ["village_006"],
                    "奖励": ["获得：基础吐纳诀"]
                },
                {
                    "节点ID": "village_004",
                    "节点类型": "引导节点",
                    "前置条件": ["village_002"],
                    "触发关键词": ["努力", "坚持", "勤奋"],
                    "剧情描述": "鼓励玩家坚持修炼",
                    "NPC回复模板": "（拍拍你的肩膀）修仙一途，资质固然重要，但更重要的是恒心。古往今来，多少资质平庸者凭毅力登临绝顶。你若肯努力，未必不能成事。",
                    "下一步剧情": ["village_006"],
                    "奖励": ["获得：修炼建议"]
                },
                {
                    "节点ID": "village_005",
                    "节点类型": "关键节点",
                    "前置条件": ["village_002"],
                    "触发关键词": ["放弃", "离开", "回去"],
                    "剧情描述": "玩家选择放弃修仙",
                    "NPC回复模板": "（叹了口气）修仙之路，本就非人人可走。你若心意已决，老夫也不强求。不过，这青牛镇虽小，却也安宁，你若愿意，可在此安身立命。",
                    "下一步剧情": ["village_end"],
                    "奖励": [],
                    "失败后果": ["剧情结束"]
                },
                {
                    "节点ID": "village_006",
                    "节点类型": "关键节点",
                    "前置条件": ["village_003", "village_004"],
                    "触发关键词": ["青云门", "上山", "拜见掌门"],
                    "剧情描述": "前往青云门",
                    "NPC回复模板": "（指向青云山方向）青云门就在那云雾缭绕的山巅。你既已入门，便可前往一试。记住，入门之后，便是真正的修仙之路，切莫懈怠。",
                    "下一步剧情": ["mountain_001"],
                    "奖励": ["获得：青云门通行令"],
                    "失败后果": ["无法进入青云门"]
                },
                {
                    "节点ID": "mountain_001",
                    "节点类型": "关键节点",
                    "前置条件": ["village_006"],
                    "触发关键词": ["掌门", "拜见", "入门"],
                    "剧情描述": "拜见青云门掌门",
                    "NPC回复模板": "（青云子端坐于大殿之上，目光如电）年轻人，既已至此，便让我看看你的资质。",
                    "下一步剧情": ["mountain_002"],
                    "奖励": ["获得：入门测试资格"]
                },
                {
                    "节点ID": "mountain_002",
                    "节点类型": "引导节点",
                    "前置条件": ["mountain_001"],
                    "触发关键词": ["师兄", "师姐", "请教"],
                    "剧情描述": "与师兄师姐交流",
                    "NPC回复模板": "（师兄微笑着）师弟，既已入门，便要勤加修炼。若有不懂之处，尽管来问我。",
                    "下一步剧情": ["mountain_003"],
                    "奖励": ["获得：修炼指导"]
                },
                {
                    "节点ID": "mountain_003",
                    "节点类型": "关键节点",
                    "前置条件": ["mountain_002"],
                    "触发关键词": ["任务", "试炼", "挑战"],
                    "剧情描述": "接受门派任务",
                    "NPC回复模板": "（掌门沉吟片刻）既如此，便给你一个试炼任务。去后山秘境，取回一枚灵石。此行虽不凶险，却也能磨炼心性。",
                    "下一步剧情": ["cave_001"],
                    "奖励": ["获得：试炼任务"]
                },
                {
                    "节点ID": "cave_001",
                    "节点类型": "关键节点",
                    "前置条件": ["mountain_003"],
                    "触发关键词": ["秘境", "洞穴", "探索"],
                    "剧情描述": "探索神秘洞穴",
                    "NPC回复模板": "（神秘老人从阴影中走出）年轻人，既已至此，便是有缘。这洞穴中藏有上古传承，你可愿一试？",
                    "下一步剧情": ["cave_002"],
                    "奖励": ["获得：上古传承线索"]
                },
                {
                    "节点ID": "cave_002",
                    "节点类型": "引导节点",
                    "前置条件": ["cave_001"],
                    "触发关键词": ["传承", "功法", "宝物"],
                    "剧情描述": "获得传承",
                    "NPC回复模板": "（神秘老人点头）既如此，便传你这套《青云诀》。此乃上古传承，你需勤加修炼，莫要辜负了这份机缘。",
                    "下一步剧情": ["end_001"],
                    "奖励": ["获得：青云诀"]
                },
                {
                    "节点ID": "end_001",
                    "节点类型": "关键节点",
                    "前置条件": ["cave_002"],
                    "触发关键词": ["完成", "结束", "成就"],
                    "剧情描述": "剧情完成",
                    "NPC回复模板": "（老者欣慰地看着你）年轻人，恭喜你踏上了真正的修仙之路。但这只是开始，前路漫漫，还需你自行探索。老夫能做的，只有这些了。",
                    "下一步剧情": [],
                    "奖励": ["获得：修仙之路开启"]
                }
            ],
            
            "角色设定": [
                {
                    "角色名": "老者",
                    "性格": ["慈祥", "见多识广", "乐于助人"],
                    "说话风格": "古风、温和、带点仙侠气息",
                    "常用词汇": ["老朽", "年轻人", "修仙一途", "道友"],
                    "禁忌话题": ["现代科技", "其他门派机密"]
                },
                {
                    "角色名": "青云子",
                    "性格": ["威严", "公正", "看重资质"],
                    "说话风格": "庄重、简洁、不怒自威",
                    "常用词汇": ["本座", "弟子", "修为", "境界"],
                    "禁忌话题": ["门派秘辛", "过往恩怨"]
                },
                {
                    "角色名": "师兄",
                    "性格": ["热情", "耐心", "乐于助人"],
                    "说话风格": "亲切、随和、像邻家大哥",
                    "常用词汇": ["师弟", "师妹", "修炼", "功法"],
                    "禁忌话题": []
                },
                {
                    "角色名": "神秘老人",
                    "性格": ["神秘", "高深", "看透世事"],
                    "说话风格": "玄奥、深邃、似有深意",
                    "常用词汇": ["机缘", "传承", "因果", "道"],
                    "禁忌话题": ["身份", "来历"]
                }
            ],
            
            "世界设定": [
                {
                    "主题": "修仙体系",
                    "内容": "境界划分：练气期、筑基期、金丹期、元婴期、化神期、炼虚期、合体期、大乘期、渡劫期",
                    "关键词": ["境界", "修为", "灵气", "突破"]
                },
                {
                    "主题": "灵根体系",
                    "内容": "灵根分为金木水火土五行，以及变异灵根如风雷冰等。灵根越纯净，修炼速度越快",
                    "关键词": ["灵根", "五行", "变异", "资质"]
                },
                {
                    "主题": "门派体系",
                    "内容": "修仙界门派林立，青云门是附近最大的门派，以剑修和丹道闻名",
                    "关键词": ["门派", "青云门", "剑修", "丹道"]
                }
            ]
        }
    
    def _initialize_knowledge_base(self):
        if self.collection.count() == 0:
            print("初始化剧情知识库...")
            self._add_story_nodes()
            print(f"知识库初始化完成，共添加 {self.collection.count()} 个节点")
    
    def _add_story_nodes(self):
        nodes = self.story_knowledge["剧情节点"]
        for node in nodes:
            text = f"{node['剧情描述']} {node['NPC回复模板']}"
            vector = self.embedder.encode(text).tolist()
            self.collection.add(
                documents=[text],
                embeddings=[vector],
                metadatas=[{
                    "节点ID": node["节点ID"],
                    "节点类型": node["节点类型"],
                    "触发关键词": ",".join(node["触发关键词"]),
                    "前置条件": ",".join(node["前置条件"]),
                    "下一步剧情": ",".join(node["下一步剧情"])
                }],
                ids=[node["节点ID"]]
            )
    
    def _detect_intent(self, player_input: str) -> str:
        story_keywords = []
        for node in self.story_knowledge["剧情节点"]:
            story_keywords.extend(node["触发关键词"])
        
        for keyword in story_keywords:
            if keyword in player_input:
                return "story_related"
        
        return "free_chat"
    
    def _retrieve_story_nodes(self, player_input: str, top_k: int = 5) -> List[Dict]:
        query_vector = self.embedder.encode(player_input).tolist()
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        
        retrieved_nodes = []
        if results["ids"] and results["ids"][0]:
            print(f"[RAG] 向量检索到的节点ID: {results['ids'][0]}")
            for i in range(len(results["ids"][0])):
                node_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else 0
                print(f"[RAG] 节点 {node_id} 的相似度: {distance}")
                retrieved_nodes.append({
                    "节点ID": node_id,
                    "节点类型": metadata.get("节点类型", ""),
                    "触发关键词": metadata.get("触发关键词", ""),
                    "前置条件": metadata.get("前置条件", ""),
                    "下一步剧情": metadata.get("下一步剧情", ""),
                    "相似度": distance
                })
        
        # 添加关键词匹配的节点（优先级更高）
        keyword_matched_nodes = []
        for node in self.story_knowledge["剧情节点"]:
            for keyword in node["触发关键词"]:
                if keyword in player_input:
                    # 检查是否已经在检索结果中
                    if not any(n["节点ID"] == node["节点ID"] for n in retrieved_nodes):
                        print(f"[RAG] 关键词匹配找到节点: {node['节点ID']} (关键词: {keyword})")
                        keyword_matched_nodes.append({
                            "节点ID": node["节点ID"],
                            "节点类型": node["节点类型"],
                            "触发关键词": ",".join(node["触发关键词"]),
                            "前置条件": ",".join(node["前置条件"]),
                            "下一步剧情": ",".join(node["下一步剧情"]),
                            "相似度": 0.0  # 关键词匹配的优先级最高
                        })
                    break
        
        # 将关键词匹配的节点放在最前面
        retrieved_nodes = keyword_matched_nodes + retrieved_nodes
        
        return retrieved_nodes
    
    def _check_prerequisites(self, nodes: List[Dict], player_state: Dict) -> List[Dict]:
        valid_nodes = []
        completed_nodes = player_state.get("completed_nodes", [])
        
        print(f"[RAG] 玩家已完成节点: {completed_nodes}")
        
        for node in nodes:
            prerequisites_str = node.get("前置条件", "")
            print(f"[RAG] 节点 {node['节点ID']} 的前置条件: '{prerequisites_str}'")
            
            if not prerequisites_str or prerequisites_str.strip() == "":
                print(f"[RAG] 节点 {node['节点ID']} 无前置条件，符合条件")
                valid_nodes.append(node)
                continue
            
            prerequisites = prerequisites_str.split(",")
            print(f"[RAG] 节点 {node['节点ID']} 前置条件列表: {prerequisites}")
            
            if all(req.strip() in completed_nodes for req in prerequisites if req.strip()):
                print(f"[RAG] 节点 {node['节点ID']} 符合前置条件")
                valid_nodes.append(node)
            else:
                print(f"[RAG] 节点 {node['节点ID']} 不符合前置条件")
        
        return valid_nodes
    
    def _get_character_setting(self, npc_name: str) -> Dict:
        for character in self.story_knowledge["角色设定"]:
            if character["角色名"] == npc_name:
                return character
        return {}
    
    def _get_world_setting(self, topic: str) -> Optional[Dict]:
        for setting in self.story_knowledge["世界设定"]:
            if topic in setting["关键词"]:
                return setting
        return None
    
    def process_dialogue(
        self, 
        npc_name: str, 
        player_input: str, 
        dialogue_history: List[Dict],
        player_state: Dict
    ) -> Dict:
        print(f"[RAG] 处理对话: NPC={npc_name}, 输入={player_input}")
        
        intent = self._detect_intent(player_input)
        print(f"[RAG] 意图识别结果: {intent}")
        
        if intent == "story_related":
            relevant_nodes = self._retrieve_story_nodes(player_input)
            print(f"[RAG] 检索到 {len(relevant_nodes)} 个相关节点")
            
            valid_nodes = self._check_prerequisites(relevant_nodes, player_state)
            print(f"[RAG] 符合前置条件的节点: {len(valid_nodes)}")
            
            if valid_nodes:
                node = valid_nodes[0]
                node_type = node["节点类型"]
                print(f"[RAG] 选择节点: {node['节点ID']}, 类型: {node_type}")
                
                if node_type == "关键节点":
                    return {
                        "回复类型": "关键剧情",
                        "回复内容": self._get_node_response(node["节点ID"]),
                        "节点ID": node["节点ID"],
                        "下一步剧情": node["下一步剧情"].split(","),
                        "奖励": self._get_node_rewards(node["节点ID"])
                    }
                elif node_type == "引导节点":
                    return {
                        "回复类型": "引导剧情",
                        "回复内容": self._get_node_response(node["节点ID"]),
                        "节点ID": node["节点ID"],
                        "下一步剧情": node["下一步剧情"].split(","),
                        "奖励": self._get_node_rewards(node["节点ID"])
                    }
            else:
                print(f"[RAG] 没有符合条件的节点，使用AI自由对话")
        
        character = self._get_character_setting(npc_name)
        print(f"[RAG] 使用AI自由对话，角色设定: {character.get('角色名', '未知')}")
        return {
            "回复类型": "自由对话",
            "回复内容": None,
            "角色设定": character
        }
    
    def _get_node_response(self, node_id: str) -> str:
        for node in self.story_knowledge["剧情节点"]:
            if node["节点ID"] == node_id:
                return node["NPC回复模板"]
        return ""
    
    def _get_node_rewards(self, node_id: str) -> List[str]:
        for node in self.story_knowledge["剧情节点"]:
            if node["节点ID"] == node_id:
                return node.get("奖励", [])
        return []
    
    def update_player_state(self, player_state: Dict, completed_node_id: str):
        if "completed_nodes" not in player_state:
            player_state["completed_nodes"] = []
        
        if completed_node_id not in player_state["completed_nodes"]:
            player_state["completed_nodes"].append(completed_node_id)
        
        rewards = self._get_node_rewards(completed_node_id)
        if "inventory" not in player_state:
            player_state["inventory"] = []
        
        for reward in rewards:
            if reward not in player_state["inventory"]:
                player_state["inventory"].append(reward)
        
        return player_state
