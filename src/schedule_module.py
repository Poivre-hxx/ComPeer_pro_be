# The schedule module of ComPeer, responsible for initialize schedule, eval the importance of event, and update the schedule.
from src.tools import load_prompt,get_today_info
from src.settings import USE_REAL_WORLD_INFORMATION
from datetime import datetime
#from openai import OpenAI
import json
from src.llm_silicon import SiliconFlowLLM
import io

class schedule_module:
    #初始化只注册了userid
    def __init__(self,user_ids):
        self.user_ids=user_ids
        

    def initialize_schedule(self, reflection):
        llm = SiliconFlowLLM()
        for user_id in self.user_ids:
            #提示词
            guidance_prompt = load_prompt(f'schedule_generation_{user_id}.txt')
            print(f'Begin to generate the schedule of {user_id}.')
            # #天气信息
            # if USE_REAL_WORLD_INFORMATION:
            #     today_data = get_today_info()
            # else:
            #     today_data = ""
            schedule_is_json = False
            while not schedule_is_json:
                print(f"reflection of {user_id} is {reflection[user_id]}")
                messages = [
                {"role": "system", "content": guidance_prompt + '\n' + 
                 "Environmental information, such as today’s date, temperature, and weather: " + '\n' +
                 "The reflection of today’s interaction, which summarizes the user’s current state and future challenges. You need to base your schedule for tomorrow’s support on its content: " + reflection[user_id] + '\n' +
                 "Now output the schedule in JSON format."}
                ]   

                try:
                    output = llm.chat(messages)  # ✅ 使用 SiliconFlowLLM 接口
                    schedule_str = output.replace("```", "").replace("json", "").strip()
                    print("获得schedule反馈")
                    print(schedule_str.encode("utf-8", errors="replace").decode("utf-8"))
                    #print(schedule_str)

                    schedule_json = json.loads(schedule_str)
                    print(f"{user_id} generate successfully!")
                    schedule_is_json = True

                    with io.open(f'schedule/today_schedule_{user_id}.json', 'w', encoding='utf-8') as f:
                        json.dump(schedule_json, f, ensure_ascii=False, indent=4)
                except json.JSONDecodeError:
                    print("[ERROR] LLM output is not valid JSON, retrying...")
                except Exception as e:
                    print(f"[ERROR] Failed to generate schedule for {user_id}: {e}")
                    break  # 避免死循环
                # print(f"reflection of {user_id} is {reflection[user_id]}")
                # client = OpenAI()
                # schedule = client.chat.completions.create(
                #     model="gpt-4o",
                #     messages=[{"role": "system", "content": guidance_prompt + '\n' + 
                #                                             " Environmental information, such as today’s date, temperature, and weather:" + 
                #                                             str(today_data) + '\n' + 
                #                                             "The reflection of today’s interaction, which summarizes the user’s current state and future challenges. You need to base your schedule for tomorrow’s support on its content: :" + 
                #                                             reflection[user_id]+ '\n' +
                #                                             "Now output the schedule."}],
                # ).choices[0].message.content
                # #将字符串schedule中的所有"```"和"json"替换为空字符串，并去除字符串两端的空白字符
                # schedule = schedule.replace("```", "").replace("json","").strip()
                # print(schedule)
                # try:
                # # transfer content to JSON
                # #json.loads()函数是Python标准库json模块中的一个函数，它用于将JSON格式的字符串转换为Python的字典或列表
                #     schedule_json = json.loads(schedule)
                #     print(f"{user_id} generate successfully!")
                #     schedule_is_json = True  
                #     #'w'：这是文件打开模式，表示写入模式。如果文件已存在，它会被覆盖；如果不存在，会创建一个新文件
                #     with open(f'schedule/today_schedule_{user_id}.json', 'w', encoding='utf-8') as f:
                #         #将schedule_json对象序列化为JSON格式并写入到文件f中
                #         json.dump(schedule_json, f, ensure_ascii=False, indent=4)
                # except json.JSONDecodeError:
                #     print("it is not json and try begin...")

    
    def update_schedule(self, user_id, extracted_event):
        print(f"updating schedule...")
        print(f"the event is {extracted_event}")
        with open(f"schedule/today_schedule_{user_id}.json", "r",encoding="utf-8") as file:
            existing_data = json.load(file)
        updated_data = self.insert_sorted_json(existing_data, extracted_event)
        with open(f"schedule/today_schedule_{user_id}.json", "w",encoding="utf-8") as file:
            json.dump(updated_data, file, indent=4, ensure_ascii=False)
            print("update!")
    
    def insert_sorted_json(self,existing_data, new_data):
        new_time = new_data["Timing"]
        for i, data in enumerate(existing_data):
            if new_time < data["Timing"]:
                existing_data.insert(i, new_data)
                return existing_data
        existing_data.append(new_data)
        return existing_data
    
    def compute_importance(self, event):
        prompt=load_prompt('eval.txt')
        input=[{"role": "system", "content": prompt + event}]
        llm = SiliconFlowLLM()
        response = llm.chat(input)
        #client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini", 
        #     messages=input
        # )
        try:
            float_number = float(response.choices[0].message.content)
        except ValueError:
        # return default
            float_number = 0.5
        return float_number
    