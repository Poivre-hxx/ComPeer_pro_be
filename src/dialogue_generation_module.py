# The dialogue generation module of ComPeer, including LLM_1(psychological_companion), LLM_2(passive_replyer), and LLM_3(proactive_sender) of ComPeer.

from src.tools import load_prompt
#from openai import OpenAI
from src.llm_silicon import SiliconFlowLLM

class psychological_companion:
    def __init__(self):
        LLM_1_response_role = load_prompt("psychological_companion_proactive.txt")
        LLM_1_proactive_role = load_prompt("psychological_companion_proactive.txt")
        self.response_role_prompt = LLM_1_response_role
        self.proactive_role_prompt = LLM_1_proactive_role
        self.llm = SiliconFlowLLM()

    #选择心理治疗策略
    def select_response_strategy(self, user_input):
        history = [{"role": "system", "content": self.response_role_prompt}]
        history.append({"role": "user", "content": user_input})
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o", 
        #     messages=history
        # )
        # print(response.choices[0].message.content)
        # return response.choices[0].message.content
        response = self.llm.chat(history)
        print(response)
        return response
    
    #根据时间选择生成策略
    def select_proactive_strategy(self, event):
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o", 
        #     messages=message
        # )
        # print(response.choices[0].message.content)
        # return response.choices[0].message.content
        message = [{"role": "system", "content": self.proactive_role_prompt + '\n' + str(event)}]
        response = self.llm.chat(message)
        print(response)
        return response

class passive_replyer:
    def __init__(self):
        self.llm = SiliconFlowLLM()
        return
    #根据现在的输入，长期记忆和短期记忆和选择的策列来生成回复
    def generate_passive_reply(self, user_input, related_memory, short_term_memory, selected_strategy):
        conversation_context = short_term_memory.copy()
        print(f"user input: {user_input}, related_memory:{related_memory}, selected_strategy:{selected_strategy}")
        conversation_context.append({"role":"user","content":user_input + '\n' + related_memory + '\n' + selected_strategy})
        # print(conversation_context[-1])
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o", 
        #     messages=conversation_context
        # )
        # return response.choices[0].message.content
        response = self.llm.chat(conversation_context)
        print(response)
        return response

class proactive_sender:
    def __init__(self):
        self.llm = SiliconFlowLLM()
        return
    
    def generate_proactive_message(self, event, persona, selected_strategy):
        content = persona + '\n' + '\n The event information:'+ event + '\n' + selected_strategy
        print(f"event: {event}, selected_strategy:{selected_strategy}")
        conversation_context = [{"role":"system","content":content}]
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o", 
        #     messages=conversation_context
        # )
        # return response.choices[0].message.content
        response = self.llm.chat(conversation_context)
        return response




