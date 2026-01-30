def calculate_power_ups(num_cams, cam_type_str, night_mode_active, backup_str):
    """
    حسابات الطاقة بناءً على كود الديسك توب
    """
    # 1. تحديد استهلاك الكاميرا (Wattage Estimation)
    if "Fixed" in cam_type_str:
        base_watts = 7
    elif "Motorized" in cam_type_str:
        base_watts = 12
    elif "PTZ" in cam_type_str:
        base_watts = 25
    else:
        base_watts = 7 # Default

    # زيادة الوضع الليلي (Night Mode Adder)
    if night_mode_active:
        base_watts += 3 # Warm light consumes more

    total_watts_raw = num_cams * base_watts
    
    # معامل أمان 20% (Safety Buffer 1.20)
    total_watts_safe = total_watts_raw * 1.20

    # 2. اقتراح السويتش (Switch Suggestion)
    if total_watts_safe == 0:
        switch_sugg = "N/A"
    elif total_watts_safe < 60:
        switch_sugg = "4/8 Port PoE (60W)"
    elif total_watts_safe < 120:
        switch_sugg = "8/16 Port PoE (150W)"
    elif total_watts_safe < 240:
        switch_sugg = "16/24 Port PoE (250W)"
    elif total_watts_safe < 370:
        switch_sugg = "24 Port PoE (370W+)"
    else:
        switch_sugg = "Multiple Switches Required"

    # 3. حساب ساعات التشغيل (Backup Hours Parsing)
    if "15 Min" in backup_str: hours = 0.25
    elif "30 Min" in backup_str: hours = 0.5
    elif "1 Hour" in backup_str: hours = 1.0
    elif "2 Hour" in backup_str: hours = 2.0
    elif "4 Hour" in backup_str: hours = 4.0
    else: hours = 0 # Default

    # 4. حساب UPS والبطاريات
    # VA Calculation (Power Factor 0.7)
    required_va = total_watts_safe / 0.7
    
    # Battery Calculation (Rough Estimate for 12V system)
    required_ah = (total_watts_safe * hours) / 12

    return total_watts_safe, switch_sugg, required_va, required_ah