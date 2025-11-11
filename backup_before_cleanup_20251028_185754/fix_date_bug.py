#!/usr/bin/env python3
# fix_date_bug.py
"""
اختبار وإصلاح مشكلة استخراج التاريخ
"""

import re
from datetime import datetime

def test_date_extraction():
    """اختبار استخراج التاريخ"""
    
    # أسماء الشهور مع اللهجة التونسية
    month_names_ar = {
        'يناير': 1, 'جانفي': 1,
        'فبراير': 2, 'فيفري': 2,
        'مارس': 3,
        'أبريل': 4, 'أفريل': 4,
        'مايو': 5, 'ماي': 5,
        'يونيو': 6, 'جوان': 6,
        'يوليو': 7, 'جويلية': 7,
        'أغسطس': 8, 'أوت': 8,
        'سبتمبر': 9,
        'أكتوبر': 10,
        'نوفمبر': 11,
        'ديسمبر': 12
    }
    
    test_cases = [
        "موعد يوم 23 أكتوبر 2025 الساعة 19:45",
        "لقاء 17 جانفي 2026 على الساعة 17:30",
        "اجتماع 5 ماي 2025",
    ]
    
    print("="*60)
    print("🧪 اختبار استخراج التاريخ")
    print("="*60)
    
    for text in test_cases:
        print(f"\n📝 النص: {text}")
        
        # البحث عن نمط التاريخ
        for month_name, month_num in month_names_ar.items():
            pattern = rf'(\d{{1,2}})\s+{month_name}(?:\s+(\d{{4}}))?'
            match = re.search(pattern, text.lower())
            
            if match:
                day = int(match.group(1))
                year = int(match.group(2)) if match.group(2) else datetime.now().year
                
                print(f"   ✅ وجدت: يوم {day}, شهر {month_name} ({month_num}), سنة {year}")
                
                try:
                    date = datetime(year, month_num, day)
                    print(f"   📅 التاريخ النهائي: {date.strftime('%Y-%m-%d')}")
                except ValueError as e:
                    print(f"   ❌ خطأ: {e}")
                
                break
        else:
            print("   ❌ لم يُعثر على تاريخ")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_date_extraction()