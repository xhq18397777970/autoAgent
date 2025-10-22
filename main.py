import os
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
llm_config = {
    "config_list": [
        {
            "model": "deepseek-chat",  # DeepSeek 聊天模型
            "api_key": "sk-bbb938ce229d471b964eafee206668f3",
            "base_url": "https://api.deepseek.com",  # DeepSeek API 基础 URL
            "api_type": "openai",  # DeepSeek 兼容 OpenAI API 格式
        }
    ]
}

assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

user_proxy.initiate_chat(
    assistant,
    message= "给我讲个笑话"
)