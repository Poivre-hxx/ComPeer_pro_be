# The Memory module of ComPeer.
# from src.VectorDB import vectorDB
# from src.tools import load_prompt
# from src.settings import API_KEY
# from langchain_openai import OpenAIEmbeddings
# from typing import Union
# import os
# import json

# class Memory:
#     def __init__(self, user_ids):
#         # store CA's presonas agent的人格字典
#         self.personas = {}
#         #根据人格，事件和策略生成对话
#         self.proactive_personas = {}
        
#         # store short term memory and long term memory，长期记忆和短期记忆字典
#         self.short_term_memory = {}
#         self.long_term_memory = {}
        
#         # set embedding model
#         self.embedding = OpenAIEmbeddings(openai_api_key=API_KEY)
        
#         # set each participants personas and memory
#         for user_id in user_ids:
#             self.personas[user_id] = load_prompt(f"personas_{user_id}.txt")
#             self.proactive_personas[user_id] = load_prompt(f"proactive_{user_id}.txt")
#             self.short_term_memory[user_id] = [{"role": "system", "content": self.personas[user_id]}]
#             self.short_term_memory[user_id] += self.load_memory(user_id)
#             #长期记忆
#             self.long_term_memory[user_id] = vectorDB(self.embedding, f'history/history_{user_id}.csv')

#     def store_short_term_memory(self, user_id, entries):
#         for i in entries:
#             self.short_term_memory[user_id].append(i)
        
        #将短期记忆转化为长期记忆
        # if len(self.short_term_memory[user_id]) > 20:
        #     # Transfer the 2nd and 3rd entries to long-term memory (1st is system_prompt)
        #     if self.short_term_memory[user_id][1]["role"]=="assistant":
        #         del self.short_term_memory[user_id][1]
        #     move_to_long_term = self.short_term_memory[user_id][1:3]
        #     print(f"the long term memory is {move_to_long_term}")
        #     print(f"the embedded message is {move_to_long_term[0]['content']}")
        #     self.store_long_term_memory(user_id, move_to_long_term[0]["content"], move_to_long_term)
        #     self.short_term_memory[user_id] = [self.short_term_memory[user_id][0]] + self.short_term_memory[user_id][3:]

#         with open(f'memory/memory_{user_id}.jsonl', 'w', encoding='utf-8') as file:
#             for entry in self.short_term_memory[user_id][:20]:
#                 file.write(json.dumps(entry, ensure_ascii=False) + '\n')

#     def store_long_term_memory(self, user_id, text:Union[str, list], history):
#         #  embbed and store long_term_memory
#         self.long_term_memory[user_id].store(text, history)
    

#     def search_related_memory(self, user_id, text: str, top_n: int = 3):
#         # search top_n related memory
#         return self.long_term_memory[user_id].query(text, top_n)

#     #加载之前的短期记忆    
#     def load_memory(self, user_id):
#         memory_path = f'memory/memory_{user_id}.jsonl'
#         if not os.path.exists(memory_path):
#             with open(memory_path, 'w', encoding='utf-8') as file:
#                 pass
#         try:
#             memory = []
#             with open(memory_path, 'r', encoding='utf-8') as file:
#                 for line in file:
#                     if line.strip(): 
#                         memory.append(json.loads(line.strip()))
#             #返回 memory 列表中从第三个元素开始的所有元素。这意味着前两个元素将被忽略
#             return memory[2:]
    
#         except FileNotFoundError:
#             return []

import os
import json

class Memory:
    def __init__(self, user_ids):
        """
        初始化本地内存管理器，用于每个用户维护简单的对话历史。
        """
        self.user_ids = user_ids
        self.memory_dict = {uid: [] for uid in user_ids}

        self.short_term_memory = {uid: [] for uid in user_ids}
        self.memory_path = "memory"

        if not os.path.exists(self.memory_path):
            os.makedirs(self.memory_path)

        self._load_all_memories()

    def _load_all_memories(self):
        """
        加载所有用户的记忆文件。
        """
        for uid in self.user_ids:
            path = os.path.join(self.memory_path, f"{uid}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.memory_dict[uid] = json.load(f)

    def retrieve(self, user_id, query=None):
        """
        简化的 retrieve 方法，返回该用户的全部记忆（可选支持关键词匹配）。
        """
        memory = self.memory_dict.get(user_id, [])
        if query:
            # 可选关键词筛选
            return [m for m in memory if query in m]
        return memory

    def update(self, user_id, content):
        """
        向用户的记忆中添加新内容。
        """
        if user_id not in self.memory_dict:
            self.memory_dict[user_id] = []

        self.memory_dict[user_id].append(content)

        # 持久化到文件
        path = os.path.join(self.memory_path, f"{user_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.memory_dict[user_id], f, ensure_ascii=False, indent=2)

    def ensure_user(self, user_id):
        if user_id not in self.memory_dict:
            self.memory_dict[user_id] = []
        if not hasattr(self, "short_term_memory"):
            self.short_term_memory = {}
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = [] 

    def store_short_term_memory(self, user_id, content):
        if not hasattr(self, "short_term_memory"):
            self.short_term_memory = {}
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = []
        self.short_term_memory[user_id].append(content)
        self.short_term_memory[user_id] = self.short_term_memory[user_id][-5:]
