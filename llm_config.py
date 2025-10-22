import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
llm_config = {
    "config_list": [
        {
            "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),  # DeepSeek 聊天模型
            "api_key": os.environ.get("DEEPSEEK_API_KEY"),
            "base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),  # DeepSeek API 基础 URL
            "api_type": "openai",  # DeepSeek 兼容 OpenAI API 格式
        }
    ]
}