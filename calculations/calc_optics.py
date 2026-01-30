def calculate_lens_dori(distance, width, scene_type, res_str):
    """
    حساب العدسة المناسبة وجودة الصورة (DORI)
    """
    # 1. ثوابت الفيزياء (Standard 1/2.8" Sensor)
    sensor_w = 5.18 
    
    # 2. تحديد عدد البكسلات العرضية (Horizontal Pixels)
    if "2MP" in res_str: h_pixels = 1920
    elif "4MP" in res_str: h_pixels = 2560
    elif "5MP" in res_str: h_pixels = 2880
    elif "8MP" in res_str: h_pixels = 3840
    else: h_pixels = 3840 # Default 4K

    # 3. محرك اختيار العدسة (Lens Selection Engine)
    rec_lens = 2.8
    reason = "Standard Wide"

    # أ) السور الخارجي (Perimeter Fence)
    if "Perimeter" in scene_type:
        if distance <= 20:
            rec_lens = 2.8; reason = "Short Range (Wide)"
        elif distance <= 40:
            rec_lens = 3.6; reason = "Medium Range"
        elif distance <= 70:
            rec_lens = 6.0; reason = "Long Range"
        else:
            rec_lens = 12.0; reason = "Extra Long Range"
            
    # ب) الجراجات والمواقف (Parking)
    elif "Parking" in scene_type:
        if distance <= 25:
            rec_lens = 2.8; reason = "Overview"
        elif distance <= 40:
            rec_lens = 3.6; reason = "Detail Oriented"
        else:
            rec_lens = 6.0; reason = "Large Area"
            
    # ج) الغرف الداخلية (Indoor)
    else:
        # بنستخدم نسبة الطول للعرض عشان نعرف شكل الغرفة
        safe_width = width if width > 0 else 1 # منع القسمة على صفر
        ratio = distance / safe_width
        
        if ratio < 1.5:
            rec_lens = 2.8; reason = "Square Room (Wide)"
        elif ratio < 3.0:
            rec_lens = 3.6; reason = "Rectangular Room"
        else:
            rec_lens = 6.0; reason = "Corridor / Hallway"

    # 4. حسابات الجودة (DORI / PPM)
    # المعادلة: عرض الرؤية الفعلي = (المسافة * عرض السنسور) / البعد البؤري
    actual_view_width = (distance * sensor_w) / rec_lens
    if actual_view_width <= 0: actual_view_width = 1
    
    # PPM = عدد البكسلات / عرض الرؤية بالمتر
    ppm = h_pixels / actual_view_width

    # 5. تصنيف الجودة (Smart Status)
    quality_text = "OBSERVATION"
    quality_color = "#E63946" # Red
    
    if ppm >= 250:
        quality_text = "IDENTIFICATION" # تحديد الهوية (وش)
        quality_color = "#2EC4B6" # Green
    elif ppm >= 125:
        quality_text = "RECOGNITION" # التعرف (شخص معروف)
        quality_color = "#2EC4B6" # Green
    elif ppm >= 50:
        quality_text = "DETECTION" # كشف حركة
        quality_color = "#FCA311" # Orange

    return rec_lens, reason, quality_text, ppm, quality_color