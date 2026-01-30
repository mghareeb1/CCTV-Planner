def calculate_voltage_drop(length, cable_cat, material, load_str):
    """
    حساب فقد الجهد في كابلات الشبكة
    """
    # 1. تحليل استهلاك الطاقة (Parse Watts)
    # المتوقع: نص مثل "7W (Fixed)"
    try:
        power_watts = float(load_str.split("W")[0])
    except:
        power_watts = 7.0 # Default

    # 2. الثوابت (Constants)
    SOURCE_VOLTAGE = 48.0 # PoE Standard Voltage
    
    # 3. حساب المقاومة (Resistance Ohms/m)
    # Cat6 مقاومته أقل من Cat5e
    if "Cat6" in cable_cat:
        base_resistance = 0.15
    else: # Cat5e
        base_resistance = 0.188
    
    # 4. عقوبة خامة الكابل (Material Penalty)
    # النحاس المخلوط ألومنيوم (CCA) مقاومته أعلى بـ 50%
    if "CCA" in material:
        resistance_per_meter = base_resistance * 1.5 
    else:
        resistance_per_meter = base_resistance

    total_resistance = resistance_per_meter * length

    # 5. قانون أوم (Ohm's Law)
    # Current (I) = Power (P) / Voltage (V)
    # Voltage Drop (Vd) = Current (I) * Resistance (R)
    current_amps = power_watts / SOURCE_VOLTAGE
    voltage_drop = current_amps * total_resistance
    final_voltage = SOURCE_VOLTAGE - voltage_drop

    # 6. تحليل الحالة (Smart Status Logic)
    limit_voltage_af = 37.0 # الحد الأدنى لـ PoE العادي
    limit_voltage_at = 42.5 # الحد الأدنى لـ PoE+ (المواتير)
    
    status_text = "UNKNOWN"
    status_msg = ""
    status_color = "#9E9E9E"

    # أ) فحص الجهد (Power Check)
    if final_voltage >= limit_voltage_at:
        status_text = "EXCELLENT"
        status_color = "#2EC4B6" # Green
        status_msg = "Safe for all cameras (PTZ included)"
    elif final_voltage >= limit_voltage_af:
        status_text = "WARNING"
        status_color = "#FCA311" # Orange
        status_msg = "Safe for fixed cams, Risk for PTZ"
    else:
        status_text = "CRITICAL FAIL"
        status_color = "#E63946" # Red
        status_msg = "Voltage too low! Camera won't boot."

    # ب) فحص سلامة البيانات (Data Integrity Check) - CCA Risk
    # كابلات CCA بتفقد إشارة الداتا بعد 75 متر حتى لو الباور واصل
    if "CCA" in material and length > 75:
        status_text = "DATA RISK"
        status_color = "#E63946"
        status_msg = "CCA Cable > 75m causes Packet Loss!"
    
    # ج) تجاوز المعايير القياسية
    if length > 100:
        status_text = "OVER LIMIT"
        status_color = "#E63946"
        status_msg = "Exceeds Ethernet Standard (100m)"

    return final_voltage, voltage_drop, status_text, status_msg, status_color