import ipaddress

def calculate_network_details(ip_input, cidr_selection):
    """
    حساب تفاصيل الشبكة (IP Calculator Logic)
    """
    try:
        # 1. تنظيف المدخلات
        ip_str = ip_input.strip()
        
        # استخراج CIDR من النص (مثلاً "/24" من "/24 (254 Hosts)")
        if " " in cidr_selection:
            cidr = cidr_selection.split(" ")[0]
        else:
            cidr = cidr_selection
        
        full_network_str = f"{ip_str}{cidr}"
        
        # 2. إنشاء كائن الشبكة (بنتجاهل الـ Host bits الزيادة بـ strict=False)
        network = ipaddress.IPv4Network(full_network_str, strict=False)
        
        # 3. استخراج المعلومات
        net_id = str(network.network_address)
        netmask = str(network.netmask)
        broadcast = str(network.broadcast_address)
        
        # عدد الأجهزة المتاحة (بنشيل الـ Network ID والـ Broadcast)
        num_hosts = network.num_addresses - 2
        if num_hosts < 0: num_hosts = 0
        
        # 4. حساب المدى (Range)
        range_str = "No usable hosts"
        if num_hosts > 0:
            # طريقة سريعة لحساب الأول والأخير بدون Loop (عشان الشبكات الكبيرة متعلّقش)
            first_ip = str(network.network_address + 1)
            last_ip = str(network.broadcast_address - 1)
            range_str = f"{first_ip}  >>>  {last_ip}"
            
        return net_id, netmask, broadcast, num_hosts, range_str, "Success"
        
    except ValueError:
        return "-", "-", "-", 0, "Invalid IP Format", "Error"
    except Exception as e:
        return "-", "-", "-", 0, "Unknown Error", "Error"