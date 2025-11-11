#!/usr/bin/env python3
# test_full_system.py
"""
اختبار شامل للنظام بعد الإصلاح
"""

from intelligent_agent import IntelligentAgent
from datetime import datetime

def test_system():
    print("="*60)
    print("🧪 اختبار شامل للنظام")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        {
            'input': 'لدي موعد مع الطبيب اليوم بعد 20 دقيقة',
            'expected_title': 'موعد مع الطبيب',
            'expected_date_contains': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'input': 'لدي موعد مع أستاذي يوم 23 أكتوبر 2025 على الساعة 19:45',
            'expected_title': 'موعد مع أستاذي',
            'expected_date_contains': '2025-10-23 19:45'
        },
        {
            'input': 'لدي موعد مع زميلي يوم 17 جانفي 2026 على الساعة 17:30',
            'expected_title': 'موعد مع زميلي',
            'expected_date_contains': '2026-01-17 17:30'
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"الاختبار {i}:")
        print(f"{'='*60}")
        print(f"📝 المدخل: {test['input']}")
        
        # استخراج العنوان
        language = agent.detect_language(test['input'])
        title, description = agent._extract_title_and_description(test['input'], language)
        
        print(f"\n📌 العنوان المستخرج: '{title}'")
        print(f"   المتوقع: '{test['expected_title']}'")
        
        if title == test['expected_title']:
            print("   ✅ صحيح!")
        else:
            print("   ❌ خطأ!")
        
        # استخراج التاريخ
        date_time = agent.extract_datetime(test['input'], language)
        date_str = date_time.strftime('%Y-%m-%d %H:%M')
        
        print(f"\n📅 التاريخ المستخرج: {date_str}")
        print(f"   المتوقع: {test['expected_date_contains']}")
        
        if test['expected_date_contains'] in date_str:
            print("   ✅ صحيح!")
        else:
            print("   ❌ خطأ!")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60)

if __name__ == "__main__":
    test_system()