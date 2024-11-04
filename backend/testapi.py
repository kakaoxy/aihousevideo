from dotenv import load_dotenv
import os
# 设置环境变量
# 加载.env文件
load_dotenv()

# 获取API密钥
api_key = os.environ.get('API_KEY')

print('接收到API密钥', api_key)