#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 اختبار شامل - مع تفاصيل الأخطاء
"""

import sys
import os

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_time_extraction_detailed():
    """اختبار مع طباعة تفصيلية"""
    
    try:
        from intelligent_agent import IntelligentAgent
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        print("\n💡 الحل: تأكد من وجود intelligent_agent.py في نفس المجلد")
        return False
    
    agent = IntelligentAgent()
    
    test_cases = [
        # (النص، الساعة المتوقعة، الدقائق المتوقعة، الوصف)
        
        # أرقام عادية
        ("موعد على الساعة 4 مساء", 16, 0, "أرقام عادية مع مساء"),
        ("موعد غدا على الساعة 10 صباحا", 10, 0, "أرقام عادية مع صباحا"),
        
        # أرقام بالحروف - الحالات المهمة
        ("موعد على الساعة الرابعة مساء", 16, 0, "الرابعة مساء"),
        ("موعد غدا على الساعة العاشرة صباحا", 10, 0, "العاشرة صباحا"),
        
        # صيغ دقيقة
        ("موعد 14:30", 14, 30, "صيغة XX:XX"),
        
        # صيغة فرنسية
        ("RDV à 11h00", 11, 0, "صيغة فرنسية 11h00"),
        ("RDV à 9h", 9, 0, "صيغة فرنسية 9h"),
    ]
    
    print("="*80)
    print("🧪 اختبار استخراج الوقت - تفصيلي")
    print("="*80)
    print()
    
    passed = 0
    failed = 0
    failed_cases = []
    
    for text, expected_hour, expected_minute, description in test_cases:
        print(f"📝 الاختبار: {description}")
        print(f"   النص: '{text}'")
        
        try:
            result = agent._extract_time(text)
            
            if result:
                hour, minute = result
                
                if hour == expected_hour and minute == expected_minute:
                    print(f"   ✅ النتيجة: {hour:02d}:{minute:02d} (صحيح!)")
                    passed += 1
                else:
                    print(f"   ❌ النتيجة: {hour:02d}:{minute:02d}")
                    print(f"   ⚠️  المتوقع: {expected_hour:02d}:{expected_minute:02d}")
                    failed += 1
                    failed_cases.append({
                        'text': text,
                        'expected': f"{expected_hour:02d}:{expected_minute:02d}",
                        'actual': f"{hour:02d}:{minute:02d}",
                        'description': description
                    })
            else:
                print(f"   ❌ النتيجة: لم يتم استخراج الوقت")
                print(f"   ⚠️  المتوقع: {expected_hour:02d}:{expected_minute:02d}")
                failed += 1
                failed_cases.append({
                    'text': text,
                    'expected': f"{expected_hour:02d}:{expected_minute:02d}",
                    'actual': 'None',
                    'description': description
                })
        
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
            failed += 1
            failed_cases.append({
                'text': text,
                'expected': f"{expected_hour:02d}:{expected_minute:02d}",
                'actual': f'Error: {e}',
                'description': description
            })
        
        print()
    
    print("="*80)
    print(f"📊 النتيجة النهائية:")
    print(f"   ✅ نجح: {passed}/{len(test_cases)}")
    print(f"   ❌ فشل: {failed}/{len(test_cases)}")
    print("="*80)
    
    if failed_cases:
        print("\n" + "="*80)
        print("📋 ملخص الحالات الفاشلة:")
        print("="*80)
        for i, case in enumerate(failed_cases, 1):
            print(f"\n{i}. {case['description']}")
            print(f"   النص: {case['text']}")
            print(f"   المتوقع: {case['expected']}")
            print(f"   الفعلي: {case['actual']}")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = test_time_extraction_detailed()
        
        if success:
            print("\n🎉 جميع الاختبارات نجحت!")
            sys.exit(0)
        else:
            print("\n⚠️ بعض الاختبارات فشلت - راجع التفاصيل أعلاه")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)