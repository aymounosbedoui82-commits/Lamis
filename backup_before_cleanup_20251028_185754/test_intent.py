# test_intent.py
"""
اختبار سريع لتصنيف النوايا واستخراج التواريخ
"""

from intelligent_agent import IntelligentAgent
from datetime import datetime

def test_intent_classification():
    """اختبار تصنيف النوايا"""
    print("="*60)
    print("🧪 اختبار تصنيف النوايا")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        # حالات إضافة موعد
        ("موعد غداً الساعة 3 مساءً", "add_appointment"),
        ("موعد غدا الساعة 3 مساء", "add_appointment"),
        ("أريد موعد يوم الأحد", "add_appointment"),
        ("اجتماع غداً", "add_appointment"),
        ("RDV demain à 15h", "add_appointment"),
        ("Appointment tomorrow at 3pm", "add_appointment"),
        
        # حالات عرض المواعيد
        ("عرض مواعيدي", "list_appointments"),
        ("أظهر المواعيد", "list_appointments"),
        ("afficher mes rendez-vous", "list_appointments"),
        ("show my appointments", "list_appointments"),
        
        # حالات التحية
        ("مرحبا", "greeting"),
        ("Bonjour", "greeting"),
        ("Hello", "greeting"),
        
        # حالات الشكر
        ("شكراً", "thanks"),
        ("Merci", "thanks"),
        ("Thanks", "thanks"),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_intent in test_cases:
        detected_intent = agent.classify_intent(text)
        
        if detected_intent == expected_intent:
            print(f"✅ '{text}' → {detected_intent}")
            passed += 1
        else:
            print(f"❌ '{text}' → {detected_intent} (متوقع: {expected_intent})")
            failed += 1
    
    print(f"\n📊 النتيجة: {passed}/{len(test_cases)} نجح")
    print("="*60)


def test_datetime_extraction():
    """اختبار استخراج التواريخ"""
    print("\n" + "="*60)
    print("🧪 اختبار استخراج التواريخ")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        ("موعد غداً الساعة 3 مساءً", "ar"),
        ("موعد غدا الساعة 3 مساء", "ar"),
        ("اجتماع اليوم 10 صباحاً", "ar"),
        ("موعد 15:30", "ar"),
        ("RDV demain à 14h", "fr"),
        ("Meeting tomorrow at 10am", "en"),
        ("موعد يوم الأحد الساعة 5 مساءً", "ar"),
    ]
    
    for text, language in test_cases:
        try:
            result = agent.extract_datetime(text, language)
            print(f"✅ '{text}'")
            print(f"   → {result.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"❌ '{text}' → خطأ: {e}")
    
    print("="*60)


def test_full_process():
    """اختبار العملية الكاملة"""
    print("\n" + "="*60)
    print("🧪 اختبار العملية الكاملة")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_messages = [
        "موعد غداً الساعة 3 مساءً",
        "عرض مواعيدي",
        "مرحبا",
        "شكراً"
    ]
    
    for message in test_messages:
        print(f"\n💬 المستخدم: {message}")
        response = agent.process_message(user_id=1, message=message)
        print(f"🤖 البوت:\n{response}")
        print("-"*60)
    
    print("="*60)


def test_specific_case():
    """اختبار الحالة المحددة من المستخدم"""
    print("\n" + "="*60)
    print("🎯 اختبار الحالة: 'موعد غدا الساعة 3 مساء'")
    print("="*60)
    
    agent = IntelligentAgent()
    
    text = "موعد غدا الساعة 3 مساء"
    
    # 1. كشف اللغة
    language = agent.detect_language(text)
    print(f"1️⃣ اللغة المكتشفة: {language}")
    
    # 2. تصنيف النية
    intent = agent.classify_intent(text)
    print(f"2️⃣ النية المكتشفة: {intent}")
    
    # 3. استخراج التاريخ والوقت
    try:
        date_time = agent.extract_datetime(text, language)
        print(f"3️⃣ التاريخ والوقت: {date_time.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"3️⃣ خطأ في استخراج التاريخ: {e}")
    
    # 4. المعالجة الكاملة
    print(f"\n4️⃣ الرد الكامل:")
    response = agent.process_message(user_id=1, message=text)
    print(response)
    
    print("="*60)


if __name__ == "__main__":
    print("🚀 بدء الاختبارات الشاملة\n")
    
    # اختبار الحالة المحددة أولاً
    test_specific_case()
    
    # اختبارات أخرى
    test_intent_classification()
    test_datetime_extraction()
    test_full_process()
    
    print("\n✅ انتهت جميع الاختبارات!")