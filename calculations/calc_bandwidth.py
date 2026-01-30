def calculate_bandwidth_storage(num_cams, days, fps, res_str, comp_str):
    """
    دالة لحساب الباندويدث والمساحة التخزينية.
    المدخلات:
    - num_cams: عدد الكاميرات (int)
    - days: عدد الأيام (int)
    - fps: عدد الإطارات (int)
    - res_str: نص الدقة (مثل "2MP (1080p)")
    - comp_str: نص الضغط (مثل "H.265")
    
    المخرجات:
    - total_bandwidth_mbps (float)
    - total_storage_tb (float)
    """
    
    # 1. تحديد الـ Bitrate الأساسي بناءً على الدقة
    # القيم دي مستخرجة من كودك القديم
    base_bitrates = {
        "2MP (1080p)": 4096,
        "4MP (2K)": 8192,
        "5MP": 10240,
        "8MP (4K)": 16384,
        "12MP": 20480
    }
    # لو الدقة مش موجودة، افترض 2MP
    current_bitrate = base_bitrates.get(res_str, 4096)

    # 2. معامل الضغط (Compression Factor)
    if "H.265+" in comp_str:
        comp_factor = 0.35
    elif "H.265" in comp_str:
        comp_factor = 0.50
    else: # H.264
        comp_factor = 1.0

    # 3. حساب الـ Bitrate للكاميرا الواحدة
    # المعادلة: (Bitrate * Compression * (FPS/30))
    # بنفترض إن الـ Base Bitrate محسوب على 30 FPS
    final_bitrate_per_cam_kbps = current_bitrate * comp_factor * (fps / 30)
    final_bitrate_per_cam_mbps = final_bitrate_per_cam_kbps / 1024

    # 4. الحسابات الإجمالية
    total_bandwidth_mbps = final_bitrate_per_cam_mbps * num_cams
    
    total_seconds = days * 24 * 3600
    # التحويل من ميجابت لـ تيرا بايت:
    # (Mbps * seconds) / 8 = MegaBytes
    # MegaBytes / 1024 / 1024 = TeraBytes
    total_storage_mb = total_bandwidth_mbps * total_seconds / 8
    total_storage_tb = total_storage_mb / 1024 / 1024

    return total_bandwidth_mbps, total_storage_tb