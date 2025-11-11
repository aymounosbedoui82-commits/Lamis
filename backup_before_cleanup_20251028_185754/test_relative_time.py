# test_relative_time.py
"""
اختبار استخراج الوقت النسبي (بعد X دقيقة/ساعة)
"""

from intelligent_agent import IntelligentAgent
from datetime import datetime, timedelta

def test_relative_time():
    """اختبار صيغ الوقت النسبي"""
    print("="*60)
    print("🧪 اختبار الوقت النسبي")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        # عربي
        ("موعد اليوم بعد 40 دقيقة", "ar", 40, "minutes"),
        ("موعد بعد ساعتين", "ar", 2, "hours"),
        ("اجتماع بعد 3 ساعات", "ar", 3, "hours"),
        ("موعد بعد 10 دقائق", "ar", 10, "minutes"),
        ("لقاء بعد يوم", "ar", 1, "days"),
        
        # فرنسي
        ("RDV dans 30 minutes", "fr", 30, "minutes"),
        ("Réunion dans 2 heures", "fr", 2, "hours"),
        ("RDV dans 1 heure", "fr", 1, "hours"),
        
        # إنجليزي
        ("Meeting in 45 minutes", "en", 45, "minutes"),
        ("Appointment in 3 hours", "en", 3, "hours"),
        ("Call in 1 hour", "en", 1, "hours"),
    ]
    
    now = datetime.now()
    passed = 0
    failed = 0
    
    for text, language, value, unit in test_cases:
        try:
            result = agent.extract_datetime(text, language)
            
            # حساب الفرق المتوقع
            if unit == "minutes":
                expected = now + timedelta(minutes=value)
            elif unit == "hours":
                expected = now + timedelta(hours=value)
            elif unit == "days":
                expected = now + timedelta(days=value)
            
            # حساب الفرق الفعلي
            diff = (result - now).total_seconds() / 60  # بالدقائق
            expected_diff = (expected - now).total_seconds() / 60
            
            # قبول فرق ±2 دقيقة
            if abs(diff - expected_diff) <= 2:
                print(f"✅ '{text}'")
                print(f"   → {result.strftime('%H:%M')} (بعد {int(diff)} دقيقة)")
                passed += 1
            else:
                print(f"❌ '{text}'")
                print(f"   → {result.strftime('%H:%M')} (متوقع: بعد {int(expected_diff)} دقيقة)")
                failed += 1
                
        except Exception as e:
            print(f"❌ '{text}' → خطأ: {e}")
            failed += 1
    
    print(f"\n📊 النتيجة: {passed}/{len(test_cases)} نجح")
    print("="*60)


def test_mixed_patterns():
    """اختبار الأنماط المختلطة"""
    print("\n" + "="*60)
    print("🧪 اختبار الأنماط المختلطة")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        # نسبي + وقت محدد (يجب أن يتجاهل الوقت النسبي)
        "موعد غداً الساعة 3 مساءً",
        "موعد اليوم 14:30",
        
        # نسبي فقط
        "موعد بعد 30 دقيقة",
        "اجتماع بعد ساعتين",
    ]
    
    for text in test_cases:
        try:
            result = agent.extract_datetime(text, "ar")
            print(f"✅ '{text}'")
            print(f"   → {result.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"❌ '{text}' → خطأ: {e}")
    
    print("="*60)


def test_edge_cases():
    """اختبار الحالات الحدية"""
    print("\n" + "="*60)
    print("🧪 اختبار الحالات الحدية")
    print("="*60)
    
    agent = IntelligentAgent()
    
    edge_cases = [
        ("موعد بعد دقيقة واحدة", "ar"),
        ("موعد بعد 120 دقيقة", "ar"),
        ("RDV dans 0 minutes", "fr"),
        ("Meeting in 1 minute", "en"),
    ]
    
    for text, language in edge_cases:
        try:
            result = agent.extract_datetime(text, language)
            print(f"✅ '{text}'")
            print(f"   → {result.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"⚠️ '{text}' → {e}")
    
    print("="*60)


def practical_example():
    """مثال عملي كامل"""
    print("\n" + "="*60)
    print("💡 مثال عملي: 'موعد اليوم بعد 40 دقيقة'")
    print("="*60)
    
    agent = IntelligentAgent()
    text = "موعد اليوم بعد 40 دقيقة"
    
    # معالجة كاملة
    user_id = 999
    response = agent.process_message(user_id, text)
    
    print(f"📝 الرسالة: {text}")
    print(f"\n🤖 الرد:")
    print(response)
    
    # التحقق من التذكيرات
    import sqlite3
    conn = sqlite3.connect(agent.db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id FROM appointments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (user_id,))
    
    apt_row = cursor.fetchone()
    if apt_row:
        apt_id = apt_row[0]
        
        cursor.execute('''
            SELECT reminder_time
            FROM reminders
            WHERE appointment_id = ?
            ORDER BY reminder_time
        ''', (apt_id,))
        
        reminders = cursor.fetchall()
        print(f"\n🔔 التذكيرات ({len(reminders)}):")
        for reminder in reminders:
            rtime = datetime.strptime(reminder[0], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            diff_minutes = (rtime - now).total_seconds() / 60
            print(f"   • بعد {int(diff_minutes)} دقيقة ({rtime.strftime('%H:%M')})")
    
    conn.close()
    print("="*60)


if __name__ == "__main__":
    print("🚀 اختبار شامل للوقت النسبي\n")
    
    test_relative_time()
    test_mixed_patterns()
    test_edge_cases()
    practical_example()
    
    print("\n✅ انتهت جميع الاختبارات!")
    print("""
💡 ملاحظة:
   الآن يمكنك استخدام صيغ مثل:
   
   🇸🇦 العربية:
      • موعد بعد 30 دقيقة
      • اجتماع بعد ساعتين
      • لقاء بعد 3 أيام
   
   🇫🇷 الفرنسية:
      • RDV dans 30 minutes
      • Réunion dans 2 heures
   
   🇬🇧 الإنجليزية:
      • Meeting in 45 minutes
      • Call in 2 hours
    """)