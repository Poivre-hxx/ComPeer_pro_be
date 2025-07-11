API_KEY = "sk-cahozzqdcfhmbapmktxrsdmstyhxcxalejiolbwpegtphwgy"
BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"

# Reminder: `CITY` and `USE_REAL_WORLD_INFORMATION` in `src/settings.py` are used to get the real-world information in generating schedules. 
# If you are not located in China, please **ignore** `CITY` 
# and set `USE_REAL_WORLD_INFORMATION` to **False** 
# (we will support other regions in future versions).

CITY = "北京" # (e.g.,"上海")
USE_REAL_WORLD_INFORMATION = False