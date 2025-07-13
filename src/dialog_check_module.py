from datetime import datetime, timedelta
import openai


def __init__(self, api_key, base_url, memory_module):
    self.client = openai.Client(api_key=api_key)
    self.base_url = base_url
    self.memory_module = memory_module  # 从内存模块获取历史对话

def dialog_pre_check(self, userId,input_str):
    now = datetime.now()
    yesterday_datetime = now - timedelta(days=1)
    yesterday_str = yesterday_datetime.strftime("%Y-%m-%d")
    time_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    prompt_str = '【用户输入】'
    prompt_str += input_str
    prompt_str += '\n【危险行为检测任务】'
    prompt_str += '\n 请根据以上所有信息内容,判断用户是否存在以下任何一种情况:'
    prompt_str += '\n- 身体不适：表现出明显或潜在的身体不适（例如，痛、发烧、晕等）'
    prompt_str += '\n- 计划困难：表现出面对计划或目标的困难、挑战或无法完成的语言/行动/想法'
    prompt_str += '\n- 需要帮助：提及或暗示需要帮助的内容（例如，寻求帮助、请求支持等）'
    prompt_str += '\n- 心情不适：表现出心情不适的情绪（例如，悲伤、孤独、失落等）'
    prompt_str += '\n- 愿望表达：提及或暗示心愿或未来期望的内容（例如，希望做某事、表达未来目标等）'

    prompt_str += '\n【输出要求】'
    prompt_str += '\n- 如果存在任何危险信息，请输出相应的类型。例如：身体不适、计划困难、需要帮助、心情不适、愿望表达。'
    prompt_str += '\n- 判断并总结具体的情况。'
    prompt_str += '\n- 若不存在这些情况，请不要输出任何消息。'
    prompt_str += '\n- 严格遵守输出要求,绝对不要遗漏或违反格式。'

    sys_msg = [{
        "role": "system",
        "content": prompt_str
    }]
    
    # 调用 OpenAI API 获取安全检查的结果
    response = self.client.chat.completions.create(
        model="deepseek", 
        messages=sys_msg,
        stream=False
    )
    
    res = response['choices'][0]['message']['content']
    res = res.replace("```", "").replace("json", "")

    # 如果发现危险预警
    if '身' in res or '体' in res :
        print(" ⚠️ " + time_to + " 身体不适:" + res)
        return "身体不适",userId

    elif '计' in res or '划' in res or '困' in res or '难' in res :
        print(" ⚠️ " + time_to + " 计划困难:" + res)
        return "计划困难",userId
    
    elif '需' in res or '要' in res or '帮' in res or '助' in res :
        print(" ⚠️ " + time_to + " 需要帮助:" + res)
        return "需要帮助",userId
    
    elif '心' in res or '情' in res :
        print(" ⚠️ " + time_to + " 心情不适:" + res)
        return "心情不适",userId
    
    elif '愿' in res or '望' in res or '表' in res or '达' :
        print(" ⚠️ " + time_to + " 心情不适:" + res)
        return "愿望表达",userId
    else:
        return "暂无",userId


def dialog_funny_Event_check(self, userId,input_str):

    """
    判断并记录危险或有趣的事件
    """
    now = datetime.now()
    yesterday_datetime = now - timedelta(days=1)
    yesterday_str = yesterday_datetime.strftime("%Y-%m-%d")
    time_to = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 构建提示内容
    prompt_str = '【用户输入】'
    prompt_str += input_str
    prompt_str += '\n【事件检测任务】'
    prompt_str += '\n请根据以上所有信息内容,判断用户是否存在以下任何一种情况:'
    prompt_str += '\n- 有趣/喜悦/温馨/有意义/教育性强/印象深刻的事件'

    prompt_str += '\n【输出要求】'
    prompt_str += '\n- 如果存在相关信息，请输出相应的类型。例如：有趣事件、喜悦事件、有意义事件、教育事件、印象事件。'
    prompt_str += '\n- 判断并总结具体的情况。'
    prompt_str += '\n- 严格遵守输出要求,绝对不要遗漏或违反格式。'

    sys_msg = [{
        "role": "system",
        "content": prompt_str
    }]

    # 调用 OpenAI API 获取事件检测结果
    response = self.client.chat.completions.create(
        model="deepseek", 
        messages=sys_msg,
        stream=False
    )
    
    res = response['choices'][0]['message']['content']
    res = res.replace("```", "").replace("json", "").strip()

    # 记录事件
    if '有趣' in res:
        print(f"⚠️ {time_to} 有趣事件: {res}")
        return "有趣事件", userId

    elif '喜悦' in res :
        print(f"⚠️ {time_to} 喜悦事件: {res}")
        return "喜悦事件", userId

    elif '意义' in res :
        print(f"⚠️ {time_to} 有意义事件: {res}")
        return "有意义事件", userId

    elif '教育' in res :
        print(f"⚠️ {time_to} 教育事件: {res}")
        return "教育事件", userId

    elif '印象事件' in res :
        print(f"⚠️ {time_to} 印象事件: {res}")
        return "印象事件", userId

    else:
        return "暂无", userId

