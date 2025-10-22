import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()

# ==================== 天气查询函数 ====================
async def get_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    api_key = "becab1d22273f6792a96265302e1057b"
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(base_url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return f"""
城市: {data.get('name', city)}
天气: {data['weather'][0]['description']}
温度: {data['main']['temp']}°C
湿度: {data['main']['humidity']}%
风速: {data['wind']['speed']} m/s
"""
            else:
                return f"获取天气信息失败: {resp.status_code}"
    except Exception as e:
        return f"天气查询错误: {str(e)}"

# 同步版本的天气查询函数
def get_weather_sync(city: str) -> str:
    return asyncio.run(get_weather(city))

# ==================== IP查询函数 ====================
async def get_ip_location(ip: str) -> str:
    """查询IP地址的归属地信息"""
    try:
        async with httpx.AsyncClient() as client:
            # 使用ipapi.co免费API
            response = await client.get(f"http://ipapi.co/{ip}/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    return f"IP查询失败: {data.get('reason', '未知错误')}"
                
                location_info = f"""
IP地址: {ip}
国家: {data.get('country_name', '未知')}
地区: {data.get('region', '未知')}
城市: {data.get('city', '未知')}
运营商: {data.get('org', '未知')}
时区: {data.get('timezone', '未知')}
经纬度: {data.get('latitude', '未知')}, {data.get('longitude', '未知')}
"""
                return location_info
            else:
                return f"IP查询失败，状态码: {response.status_code}"
    except Exception as e:
        return f"IP查询错误: {str(e)}"

# 同步版本的IP查询函数
def get_ip_location_sync(ip: str) -> str:
    return asyncio.run(get_ip_location(ip))

# ==================== 配置LLM ====================
llm_config = {
    "config_list": [
        {
            "model": "deepseek-chat",
            "api_key": "sk-bbb938ce229d471b964eafee206668f3",
            "base_url": "https://api.deepseek.com",
            "api_type": "openai",
        }
    ]
}

# ==================== 天气助手Agent ====================
weather_llm_config = llm_config.copy()
weather_llm_config["functions"] = [
    {
        "name": "get_weather",
        "description": "查询指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 Beijing, Shanghai, New York"
                }
            },
            "required": ["city"]
        }
    }
]

weather_assistant = AssistantAgent(
    name="weather_assistant",
    system_message="""你是一个专业的天气查询助手。你的职责是：
1. 当用户询问天气时，使用get_weather函数查询指定城市的天气
2. 如果用户询问多个城市，请逐个查询并汇总结果
3. 用友好、专业的中文回复天气信息
4. 可以提供穿衣建议、出行建议等额外信息
5. 如果城市名称不明确，请询问用户具体的城市名称
6. 专注于天气相关的问题，其他问题请转交给相关专家""",
    llm_config=weather_llm_config,
    function_map={
        "get_weather": get_weather_sync
    }
)

# ==================== IP查询助手Agent ====================
ip_llm_config = llm_config.copy()
ip_llm_config["functions"] = [
    {
        "name": "get_ip_location",
        "description": "查询IP地址的归属地信息",
        "parameters": {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "description": "IP地址，如 8.8.8.8, 114.114.114.114"
                }
            },
            "required": ["ip"]
        }
    }
]

ip_assistant = AssistantAgent(
    name="ip_assistant",
    system_message="""你是一个专业的IP地址查询助手。你的职责是：
1. 当用户询问IP地址归属地时，使用get_ip_location函数查询
2. 提供详细的IP地理位置信息
3. 用专业、准确的中文回复查询结果
4. 可以解释IP地址的基本信息和地理位置含义
5. 专注于IP相关的问题，其他问题请转交给相关专家""",
    llm_config=ip_llm_config,
    function_map={
        "get_ip_location": get_ip_location_sync
    }
)

# ==================== 通用助手Agent ====================
general_assistant = AssistantAgent(
    name="general_assistant",
    system_message="""你是一个通用助手，负责协调和回答一般性问题。你的职责是：
1. 回答用户的普通问题和对话
2. 识别用户需求并将其路由到专业助手
3. 当用户询问天气时，请转交给weather_assistant
4. 当用户询问IP地址时，请转交给ip_assistant
5. 协调多个专业助手的工作""",
    llm_config=llm_config
)

# ==================== 用户代理 ====================
user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config=False,
    human_input_mode="ALWAYS"
)

# ==================== 方式一：直接调用特定助手 ====================
def chat_with_weather_assistant():
    """直接与天气助手对话"""
    user_proxy.initiate_chat(
        weather_assistant,
        message="请查询北京和上海的天气情况，并给我出行建议"
    )

def chat_with_ip_assistant():
    """直接与IP助手对话"""
    user_proxy.initiate_chat(
        ip_assistant,
        message="请查询IP地址 8.8.8.8 和 114.114.114.114 的归属地信息"
    )

# ==================== 方式二：使用群组聊天（多agent协同） ====================
def start_group_chat():
    """启动多agent协同的群组聊天"""
    # 创建群组聊天
    group_chat = GroupChat(
        agents=[user_proxy, weather_assistant, ip_assistant, general_assistant],
        messages=[],
        max_round=10
    )
    
    # 创建群组聊天管理器
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config
    )
    
    # 启动群组聊天
    user_proxy.initiate_chat(
        manager,
        message="""你好！我是一个需要帮助的用户。我有几个问题：
        1. 我想知道北京和纽约的天气情况
        2. 我还想查询一下IP地址 8.8.8.8 的信息
        3. 另外，能告诉我今天日期吗？
        请帮我处理这些问题。"""
    )

# ==================== 方式三：智能路由助手 ====================
router_assistant = AssistantAgent(
    name="router_assistant",
    system_message="""你是一个智能路由助手，负责分析用户意图并将任务分配给合适的专家。
    
根据问题类型选择专家：
- 天气相关：转给weather_assistant
- IP地址、地理位置：转给ip_assistant  
- 其他一般问题：自己回答或转给general_assistant

请先分析用户问题，然后决定由哪个专家处理，或者直接回答。""",
    llm_config=llm_config
)

def chat_with_router():
    """通过路由助手进行智能对话"""
    user_proxy.initiate_chat(
        router_assistant,
        message="我想查询北京的天气，还想知道IP地址 8.8.8.8 在哪里"
    )

# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=== 多Agent系统启动 ===")
    print("1. 天气查询助手")
    print("2. IP查询助手") 
    print("3. 多Agent协同聊天")
    print("4. 智能路由对话")
    
    choice = input("请选择对话模式 (1-4): ").strip()
    
    if choice == "1":
        print("\n=== 启动天气查询助手 ===")
        chat_with_weather_assistant()
    elif choice == "2":
        print("\n=== 启动IP查询助手 ===")
        chat_with_ip_assistant()
    elif choice == "3":
        print("\n=== 启动多Agent协同聊天 ===")
        start_group_chat()
    elif choice == "4":
        print("\n=== 启动智能路由对话 ===")
        chat_with_router()
    else:
        print("无效选择，使用默认的天气查询")
        chat_with_weather_assistant()