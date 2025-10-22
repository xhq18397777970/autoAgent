import hashlib
import requests
import time
import json

class DomainAPIClient:
    """域名API客户端类，封装鉴权和请求逻辑"""
    
    def __init__(self, app_code='xhq', erp='xiehanqi.jackson', business_id='6abe3998080d92d648d7ad461bd67f38'):
        """
        初始化API客户端
        
        Args:
            app_code (str): 分配给接入应用的唯一标识
            erp (str): 当前操作者erp
            business_id (str): 接入应用标识对应的token
        """
        self.app_code = app_code
        self.erp = erp
        self.business_id = business_id
        self.base_url = "http://api-np.jd.local/V1/Dns"
    
    def _generate_auth_headers(self):
        """
        生成鉴权请求头
        
        Returns:
            dict: 包含鉴权信息的请求头
        """
        timestamp = str(int(time.time()))
        time_str = time.strftime("%H%M%Y%m%d", time.localtime(int(timestamp)))
        sign_str = f"{self.erp}#{self.business_id}NP{time_str}"
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        return {
            "Content-type": "application/json",
            "appCode": self.app_code,
            "erp": self.erp,
            "timestamp": timestamp,
            "sign": sign
        }
    
    def query_domains_info(self, domains, **kwargs):
        """
        查询域名信息接口
        
        Args:
            domains (list): 需要查询的域名列表
            **kwargs: 其他可选参数，如 primary, service_type 等
        
        Returns:
            dict: 接口返回的JSON数据
        """
        url = f"{self.base_url}/domainsInfo"
        headers = self._generate_auth_headers()
        
        # 构造请求体
        post_data = {"domains": domains}
        post_data.update(kwargs)  # 添加其他可选参数
        
        try:
            response = requests.post(url, headers=headers, json=post_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"请求失败，状态码: {response.status_code}",
                    "response_text": response.text
                }
        except Exception as e:
            return {
                "error": True,
                "message": f"请求异常: {str(e)}"
            }
    
    def check_domain_status(self, domain):
        """
        检测域名状态接口，判定域名是否空闲
        
        Args:
            domain (str): 要检测的域名
        
        Returns:
            dict: 包含域名状态信息的字典
        """
        url = f"{self.base_url}/domainCheck"
        headers = self._generate_auth_headers()
        params = {"domain": domain}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"请求失败，状态码: {response.status_code}",
                    "response_text": response.text
                }
        except Exception as e:
            return {
                "error": True,
                "message": f"请求异常: {str(e)}"
            }
    
    def batch_check_domain_status(self, domains):
        """
        批量检测多个域名的状态
        
        Args:
            domains (list): 要检测的域名列表
        
        Returns:
            dict: 包含所有域名检测结果的字典
        """
        results = {}
        
        print(f"🚀 开始批量检测 {len(domains)} 个域名的状态...")
        print("=" * 80)
        
        for i, domain in enumerate(domains, 1):
            print(f"\n📍 检测进度: {i}/{len(domains)} - {domain}")
            result = self.check_domain_status(domain)
            results[domain] = result
            
            # 简短显示结果
            if result.get('error'):
                print(f"   ❌ 检测失败: {result.get('message', 'Unknown error')}")
            else:
                data = result.get('data', {})
                status = data.get('status')
                msg = data.get('msg', '')
                availability = "可申请" if status == -1 else "不可申请"
                print(f"   📊 状态: {msg} ({availability})")
            
            # 避免请求过于频繁，添加小延迟
            if i < len(domains):
                time.sleep(0.5)
        
        print(f"\n✅ 批量检测完成！")
        return results


def format_domain_info_output(response_data):
    """
    格式化输出域名查询接口的结果
    
    Args:
        response_data (dict): 接口返回的JSON数据
    """
    if not response_data:
        print("❌ 无响应数据")
        return
    
    # 检查是否有错误
    if response_data.get('error'):
        print(f"❌ 域名信息查询失败")
        print(f"错误信息: {response_data.get('message', 'Unknown error')}")
        if response_data.get('status_code'):
            print(f"状态码: {response_data.get('status_code')}")
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


def format_domain_status_output(response_data, domain):
    """
    格式化输出域名状态检测结果
    
    Args:
        response_data (dict): 接口返回的JSON数据
        domain (str): 检测的域名
    """
    if not response_data:
        print("❌ 无响应数据")
        return
    
    # 检查是否有错误
    if response_data.get('error'):
        print(f"❌ 域名状态检测失败")
        print(f"域名: {domain}")
        print(f"错误信息: {response_data.get('message', 'Unknown error')}")
        if response_data.get('status_code'):
            print(f"状态码: {response_data.get('status_code')}")
        return
    
    # 检查响应状态
    if response_data.get('resStatus') != 200:
        print(f"❌ 接口调用失败")
        print(f"域名: {domain}")
        print(f"状态码: {response_data.get('resStatus', 'Unknown')}")
        print(f"错误信息: {response_data.get('resMsg', 'Unknown error')}")
        return
    
    # 获取数据部分
    data = response_data.get('data', {})
    status = data.get('status')
    msg = data.get('msg', '')
    
    print("=" * 60)
    print(f"🔍 域名状态检测结果")
    print("=" * 60)
    print(f"🌐 域名: {domain}")
    print(f"📊 状态码: {status}")
    print(f"📝 状态描述: {msg}")
    
    # 根据状态码提供详细说明
    status_descriptions = {
        -1: "✅ 域名不存在（可以申请）",
        1: "🔗 DNS已解析域名",
        2: "🏪 商家域名",
        3: "🔒 NP系统预留域名"
    }
    
    if status in status_descriptions:
        print(f"💡 状态说明: {status_descriptions[status]}")
    
    # 判断域名是否空闲
    is_available = status == -1
    availability_status = "🟢 可申请" if is_available else "🔴 不可申请"
    print(f"🎯 可用性: {availability_status}")
    
    print("=" * 60)


# 便捷函数，保持向后兼容性
def query_domains_info(domains, app_code='xhq', erp='xiehanqi.jackson', business_id='6abe3998080d92d648d7ad461bd67f38', **kwargs):
    """
    查询域名信息的便捷函数
    
    Args:
        domains (list): 需要查询的域名列表
        app_code (str): 分配给接入应用的唯一标识
        erp (str): 当前操作者erp
        business_id (str): 接入应用标识对应的token
        **kwargs: 其他可选参数
    
    Returns:
        dict: 接口返回的JSON数据
    """
    client = DomainAPIClient(app_code, erp, business_id)
    return client.query_domains_info(domains, **kwargs)




def batch_check_domain_status(domains, app_code='xhq', erp='xiehanqi.jackson', business_id='6abe3998080d92d648d7ad461bd67f38'):
    """
    批量检测域名状态的便捷函数
    
    Args:
        domains (list): 要检测的域名列表
        app_code (str): 分配给接入应用的唯一标识
        erp (str): 当前操作者erp
        business_id (str): 接入应用标识对应的token
    
    Returns:
        dict: 包含所有域名检测结果的字典
    """
    client = DomainAPIClient(app_code, erp, business_id)
    return client.batch_check_domain_status(domains)


# 示例使用
if __name__ == "__main__":
    # 创建API客户端实例
    client = DomainAPIClient()
    
    # === 域名信息查询示例 ===
    print("🔍 域名信息查询示例")
    print("=" * 80)
    
    domains_to_query = ["graycluster-bind-check.jd.local", "jd.local"]
    result = client.query_domains_info(domains_to_query)
    
    print("原始返回结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n🎨 格式化输出:")
    format_domain_info_output(result)
    
    print("\n" + "="*100 + "\n")
    
    # === 域名状态检测示例 ===
    print("🔍 域名状态检测示例")
    print("=" * 80)
    
    # 单个域名检测
    test_domain = "test.jd.com"
    print(f"检测单个域名: {test_domain}")
    status_result = client.check_domain_status(test_domain)
    format_domain_status_output(status_result, test_domain)
    
    print("\n" + "-"*80 + "\n")
    
    # 批量域名检测
    test_domains = ["graycluster-bind-check.jd.local", "jd.local"]
    batch_results = client.batch_check_domain_status(test_domains)
    
    print(f"\n📋 批量检测详细结果:")
    for domain, result in batch_results.items():
        print(f"\n--- {domain} ---")
        format_domain_status_output(result, domain)