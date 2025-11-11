#!/usr/bin/env python3
# test_final_fix.py
"""
اختبار الإصلاح النهائي
"""

from intelligent_agent import IntelligentAgent

def test_tunisian_months():
    print("="*60)
    print("🧪 اختبار أسماء الشهور التونسية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        ("موعد مع زميلي يوم 17 جانفي 2026", "موعد مع زميلي"),
        ("لقاء مع الأستاذ 5 فيفري 2026", "لقاء مع الأستاذ"),
        ("اجتماع 20 جوان 2025", "اجتماع"),
        ("موعد مع الطبيب 15 جويلية 2025", "موعد مع الطبيب"),
    ]
    
    passed = 0
    failed = 0
    
    for message, expected_title in test_cases:
        language = agent.detect_language(message)
        title, _ = agent._extract_title_and_description(message, language)
        
        print(f"\n📝 '{message}'")
        print(f"   العنوان: '{title}'")
        print(f"   المتوقع: '{expected_title}'")
        
        if title == expected_title:
            print("   ✅ صحيح!")
            passed += 1
        else:
            print("   ❌ خطأ!")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 النتيجة: {passed}/{len(test_cases)} نجح")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_tunisian_months()