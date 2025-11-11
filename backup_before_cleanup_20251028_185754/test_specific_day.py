#!/usr/bin/env python3
# test_specific_day.py
"""
اختبار ميزة: عرض مواعيد يوم محدد
"""

from intelligent_agent import IntelligentAgent
from datetime import datetime, timedelta

def create_test_appointments():
    """إنشاء مواعيد تجريبية للاختبار"""
    print("="*60)
    print("📝 إنشاء مواعيد تجريبية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    # حذف المواعيد التجريبية القديمة
    import sqlite3
    conn = sqlite3.connect(agent.db.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE user_id = 777")
    conn.commit()
    conn.close()
    
    test_appointments = [
        # اليوم
        (datetime.now().replace(hour=10, minute=0), "اجتماع صباحي", "اجتماع فريق العمل", 1),
        (datetime.now().replace(hour=14, minute=30), "موعد الغداء", "غداء عمل", 2),
        (datetime.now().replace(hour=17, minute=0), "مكالمة مهمة", "اتصال بالعميل", 1),
        
        # غداً
        (datetime.now() + timedelta(days=1, hours=9), "موعد مع الطبيب", "فحص دوري", 1),
        (datetime.now() + timedelta(days=1, hours=15), "تسليم مشروع", "موعد نهائي", 1),
        
        # يوم الأحد القادم
        (datetime.now() + timedelta(days=6), "رحلة عائلية", "نزهة في الحديقة", 3),
        (datetime.now() + timedelta(days=6, hours=2), "تمرين رياضي", "الجري الصباحي", 2),
    ]
    
    print(f"\n✅ إنشاء {len(test_appointments)} موعد تجريبي...\n")
    
    for apt_time, title, desc, priority in test_appointments:
        apt_id = agent.db.add_appointment(
            user_id=777,
            title=title,
            description=desc,
            date_time=apt_time,
            priority=priority
        )
        print(f"   • {title} - {apt_time.strftime('%d/%m %H:%M')}")
    
    print("\n" + "="*60)


def test_arabic_queries():
    """اختبار الاستفسارات بالعربية"""
    print("\n" + "="*60)
    print("🇸🇦 اختبار الاستفسارات بالعربية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        "ما هي مواعيدي اليوم؟",
        "مواعيدي غداً",
        "مواعيدي يوم الأحد",
        "ما هي مواعيدي في 25/10/2025",
        "عرض مواعيدي اليوم",
    ]
    
    for query in test_cases:
        print(f"\n💬 المستخدم: {query}")
        print("─"*60)
        
        # تصنيف النية
        intent = agent.classify_intent(query)
        print(f"🎯 النية: {intent}")
        
        # الرد الكامل
        response = agent.process_message(user_id=777, message=query)
        print(f"\n🤖 البوت:")
        print(response)
        print("─"*60)


def test_french_queries():
    """اختبار الاستفسارات بالفرنسية"""
    print("\n" + "="*60)
    print("🇫🇷 اختبار الاستفسارات بالفرنسية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        "Quels sont mes rendez-vous aujourd'hui?",
        "Mes RDV demain",
        "Mes rendez-vous lundi",
        "RDV du 25/10/2025",
    ]
    
    for query in test_cases:
        print(f"\n💬 Utilisateur: {query}")
        print("─"*60)
        
        intent = agent.classify_intent(query)
        print(f"🎯 Intent: {intent}")
        
        response = agent.process_message(user_id=777, message=query)
        print(f"\n🤖 Bot:")
        print(response)
        print("─"*60)


def test_english_queries():
    """اختبار الاستفسارات بالإنجليزية"""
    print("\n" + "="*60)
    print("🇬🇧 اختبار الاستفسارات بالإنجليزية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        "What are my appointments today?",
        "My appointments tomorrow",
        "Appointments on Monday",
        "Show my appointments for 25/10/2025",
    ]
    
    for query in test_cases:
        print(f"\n💬 User: {query}")
        print("─"*60)
        
        intent = agent.classify_intent(query)
        print(f"🎯 Intent: {intent}")
        
        response = agent.process_message(user_id=777, message=query)
        print(f"\n🤖 Bot:")
        print(response)
        print("─"*60)


def test_edge_cases():
    """اختبار الحالات الحدية"""
    print("\n" + "="*60)
    print("🧪 اختبار الحالات الحدية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    edge_cases = [
        ("مواعيدي أمس", "يوم ماضي"),
        ("مواعيدي الأسبوع القادم", "أسبوع كامل"),
        ("مواعيدي في تاريخ غير موجود", "لا مواعيد"),
    ]
    
    for query, description in edge_cases:
        print(f"\n🔍 {description}: {query}")
        print("─"*60)
        
        try:
            response = agent.process_message(user_id=777, message=query)
            print(response)
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
        
        print("─"*60)


def show_usage_examples():
    """عرض أمثلة الاستخدام"""
    print("\n" + "="*60)
    print("💡 أمثلة الاستخدام")
    print("="*60)
    
    examples = {
        "🇸🇦 العربية": [
            "ما هي مواعيدي اليوم؟",
            "مواعيدي غداً",
            "مواعيدي يوم الأحد",
            "مواعيدي في 25/10/2025",
            "عرض مواعيدي اليوم",
        ],
        "🇫🇷 Français": [
            "Quels sont mes rendez-vous aujourd'hui?",
            "Mes RDV demain",
            "Mes rendez-vous lundi",
            "RDV du 25/10/2025",
        ],
        "🇬🇧 English": [
            "What are my appointments today?",
            "My appointments tomorrow",
            "Appointments on Monday",
            "Show my appointments for 25/10/2025",
        ]
    }
    
    for language, queries in examples.items():
        print(f"\n{language}")
        print("─"*60)
        for query in queries:
            print(f"   • {query}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("\n🚀 اختبار ميزة: عرض مواعيد يوم محدد\n")
    
    # 1. إنشاء مواعيد تجريبية
    create_test_appointments()
    
    # 2. عرض أمثلة الاستخدام
    show_usage_examples()
    
    # 3. الاختبارات
    test_arabic_queries()
    test_french_queries()
    test_english_queries()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار!")
    print("="*60)
    
    print("""
💡 الخطوة التالية:
   1. شغّل البوت: python telegram_bot.py
   2. أرسل: "ما هي مواعيدي اليوم؟"
   3. أو: "Mes rendez-vous demain"
   4. أو: "My appointments on Monday"
   
🎉 البوت سيعطيك مواعيد اليوم المحدد!
    """)