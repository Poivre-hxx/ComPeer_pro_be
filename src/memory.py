# The Memory module of ComPeer.
from src.VectorDB import vectorDB
from src.tools import load_prompt
from src.settings import API_KEY
from langchain_openai import OpenAIEmbeddings
from typing import Union
import os
import json
import datetime

class Memory:
    def __init__(self, user_ids):
        # store CA's presonas
        self.personas = {}
        self.proactive_personas = {}
        
        # store short term memory and long term memory
        self.short_term_memory = {}
        self.long_term_memory = {}
        
        # set embedding model
        self.embedding = OpenAIEmbeddings(openai_api_key=API_KEY)

        self.user_special_state = {}
        
        # set each participants personas and memory
        for user_id in user_ids:
            self.personas[user_id] = load_prompt(f"personas_{user_id}.txt")
            self.proactive_personas[user_id] = load_prompt(f"proactive_{user_id}.txt")
            self.short_term_memory[user_id] = [{"role": "system", "content": self.personas[user_id]}]
            self.short_term_memory[user_id] += self.load_memory(user_id)
            self.long_term_memory[user_id] = vectorDB(self.embedding, f'history/history_{user_id}.csv')
    
    def record_special_state(self, user_id, danger_type, message):
        
        # 获取当前时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if user_id not in self.user_special_state:
            self.user_special_state[user_id] = []
        
        # 记录该危险信息
        self.user_special_state[user_id].append({
            'danger_type': danger_type,
            'timestamp': timestamp
        })

        print(f"记录更新: {user_id} - {danger_type} - {timestamp}")
    
    def get_user_special_state(self, user_id):
        return self.user_special_state.get(user_id, [])

    def store_short_term_memory(self, user_id, entries):
        for i in entries:
            self.short_term_memory[user_id].append(i)
        
        if len(self.short_term_memory[user_id]) > 20:
            # Transfer the 2nd and 3rd entries to long-term memory (1st is system_prompt)
            if self.short_term_memory[user_id][1]["role"]=="assistant":
                del self.short_term_memory[user_id][1]
            move_to_long_term = self.short_term_memory[user_id][1:3]
            print(f"the long term memory is {move_to_long_term}")
            print(f"the embedded message is {move_to_long_term[0]['content']}")
            self.store_long_term_memory(user_id, move_to_long_term[0]["content"], move_to_long_term)
            self.short_term_memory[user_id] = [self.short_term_memory[user_id][0]] + self.short_term_memory[user_id][3:]

        with open(f'memory/memory_{user_id}.jsonl', 'w', encoding='utf-8') as file:
            for entry in self.short_term_memory[user_id][:20]:
                file.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def store_long_term_memory(self, user_id, text:Union[str, list], history):
        #  embbed and store long_term_memory
        self.long_term_memory[user_id].store(text, history)
    

    def search_related_memory(self, user_id, text: str, top_n: int = 3):
        # search top_n related memory
        return self.long_term_memory[user_id].query(text, top_n)
        
    def load_memory(self, user_id):
        memory_path = f'memory/memory_{user_id}.jsonl'
        if not os.path.exists(memory_path):
            with open(memory_path, 'w', encoding='utf-8') as file:
                pass
        try:
            memory = []
            with open(memory_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip(): 
                        memory.append(json.loads(line.strip()))
            return memory[2:]
    
        except FileNotFoundError:
            return []

