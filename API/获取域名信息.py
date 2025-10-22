

import hashlib
import requests
import time
import json

# === 参数配置 ===
appCode = 'xhq'         # 请替换为实际分配的appCode
erp = 'xiehanqi.jackson'                 # 当前操作者erp
businessId = '6abe3998080d92d648d7ad461bd67f38'   # 即token
domains = ["graycluster-bind-check.jd.local","jd.local"]  # 需要查询的域名列表

# === 时间戳与签名 ===
timestamp = str(int(time.time()))
timeStr = time.strftime("%H%M%Y%m%d", time.localtime(int(timestamp)))
sign_str = f"{erp}#{businessId}NP{timeStr}"
sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

# === 构造请求头 ===
headers = {
    "Content-type": "application/json",
    "appCode": appCode,
    "erp": erp,
    "timestamp": timestamp,
    "sign": sign
}

# === 构造请求体 ===
post_data = {
    "domains": domains
    # 其他可选参数按需添加，如：
    # "primary": "",
    # "service_type": 2,
    # ...
}

# === 执行请求 ===
url = "http://api-np.jd.local/V1/Dns/domainsInfo"

response = requests.post(url, headers=headers, json=post_data)
# 若为GET请求，可替换为 requests.get(..., params=xxx)
def format_domain_info_output(response_data):
    """
    格式化输出域名查询接口的结果
    
    Args:
        response_data (dict): 接口返回的JSON数据
    """
    if not response_data:
        print("❌ 无响应数据")
        return
    
    # 检查响应状态
    if response_data.get('resStatus') != 200:
        print(f"❌ 接口调用失败")
        print(f"状态码: {response_data.get('resStatus', 'Unknown')}")
        print(f"错误信息: {response_data.get('resMsg', 'Unknown error')}")
        return
    
    # 获取数据部分
    data = response_data.get('data', {})
    count = data.get('count', '0')
    infos = data.get('infos', [])
    
    print("=" * 80)
    print(f"🔍 域名查询结果 (共找到 {count} 个域名)")
    print("=" * 80)
    
    if not infos:
        print("📭 未找到任何域名信息")
        return
    
    for i, info in enumerate(infos, 1):
        print(f"\n📌 域名 #{i}")
        print("-" * 60)
        
        # 基本信息
        print(f"🌐 域名: {info.get('domain', 'N/A')}")
        print(f"📊 状态: {info.get('status_desc', 'N/A')} (代码: {info.get('status', 'N/A')})")
        print(f"🔧 服务类型: {info.get('service_type', 'N/A')}")
        print(f"🌍 网络: {info.get('network', 'N/A')}")
        print(f"⭐ 重要性: {info.get('primary', 'N/A')}")
        
        # 环境信息
        print(f"🏗️  应用环境: {info.get('app_env', 'N/A')}")
        if info.get('app_env_sub'):
            print(f"   └─ 子环境: {info.get('app_env_sub')}")
        if info.get('app_env_more'):
            print(f"   └─ 更多信息: {info.get('app_env_more')}")
        if info.get('app_env_url') and info.get('app_env_url') != '无':
            print(f"   └─ 环境URL: {info.get('app_env_url')}")
        
        # 项目信息
        project_name = info.get('project_name', 'N/A')
        project_id = info.get('project_id', '')
        if project_id:
            print(f"📁 项目: {project_name} (ID: {project_id})")
        else:
            print(f"📁 项目: {project_name}")
        
        # 负责人信息
        print(f"👤 负责人: {info.get('owner', 'N/A')}")
        if info.get('owner_email'):
            print(f"   └─ 邮箱: {info.get('owner_email')}")
        
        # 管理员信息
        manage_name = info.get('manage_name', 'N/A')
        manage_erp = info.get('manage_erp', '')
        if manage_erp:
            print(f"👨‍💼 管理员: {manage_name} ({manage_erp})")
        else:
            print(f"👨‍💼 管理员: {manage_name}")
        
        # 组织信息
        org_fullname = info.get('org_fullname', '')
        if org_fullname:
            print(f"🏢 组织: {org_fullname}")
        
        # 授权人信息
        authorizer = info.get('authorizer', [])
        if authorizer:
            print(f"🔐 授权人: {', '.join(authorizer)}")
        
        # 其他信息
        if info.get('is_third_buss') == '1':
            print("🔗 第三方业务: 是")
        
        if info.get('remark'):
            print(f"📝 备注: {info.get('remark')}")
    
    print("\n" + "=" * 80)
    print(f"✅ 查询完成，共处理 {len(infos)} 个域名")
    print("=" * 80)


if response.status_code == 200:
    print("请求成功，返回结果：")
    response_json = response.json()
    print(response_json)
    print("\n" + "🎨 格式化输出:")
    format_domain_info_output(response_json)
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)
