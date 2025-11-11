# test_reminders.py
"""
اختبار شامل لنظام التذكيرات
"""

import sqlite3
from datetime import datetime, timedelta
from intelligent_agent import IntelligentAgent

def check_reminders_system():
    """فحص نظام التذكيرات"""
    print("="*60)
    print("🔔 اختبار نظام التذكيرات")
    print("="*60)
    
    agent = IntelligentAgent()
    conn = sqlite3.connect(agent.db.db_path)
    cursor = conn.cursor()
    
    # 1. فحص جدول التذكيرات
    print("\n1️⃣ فحص جدول التذكيرات...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
    if cursor.fetchone():
        print("✅ جدول التذكيرات موجود")
    else:
        print("❌ جدول التذكيرات غير موجود!")
        return False
    
    # 2. فحص هيكل الجدول
    print("\n2️⃣ فحص هيكل جدول التذكيرات...")
    cursor.execute("PRAGMA table_info(reminders)")
    columns = cursor.fetchall()
    print("   الأعمدة الموجودة:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 3. إضافة موعد تجريبي
    print("\n3️⃣ إضافة موعد تجريبي...")
    future_time = datetime.now() + timedelta(minutes=5)
    
    try:
        apt_id = agent.db.add_appointment(
            user_id=999,
            title="اختبار التذكيرات",
            description="موعد تجريبي لاختبار النظام",
            date_time=future_time,
            priority=1
        )
        print(f"✅ تم إضافة موعد رقم: {apt_id}")
        print(f"   موعد الموعد: {future_time.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"❌ خطأ في إضافة الموعد: {e}")
        return False
    
    # 4. فحص التذكيرات المُنشأة
    print("\n4️⃣ فحص التذكيرات المُنشأة تلقائياً...")
    cursor.execute('''
        SELECT id, appointment_id, reminder_time, sent
        FROM reminders
        WHERE appointment_id = ?
        ORDER BY reminder_time
    ''', (apt_id,))
    
    reminders = cursor.fetchall()
    if reminders:
        print(f"✅ تم إنشاء {len(reminders)} تذكير")
        for reminder in reminders:
            reminder_id, apt_id, reminder_time, sent = reminder
            status = "✅ مرسل" if sent else "⏳ في الانتظار"
            print(f"   - تذكير #{reminder_id}: {reminder_time} ({status})")
    else:
        print("⚠️ لم يتم إنشاء أي تذكيرات!")
        print("   السبب: الموعد قريب جداً (أقل من ساعة)")
    
    # 5. فحص التذكيرات الحالية
    print("\n5️⃣ فحص جميع التذكيرات في النظام...")
    cursor.execute('''
        SELECT COUNT(*) FROM reminders
    ''')
    total_reminders = cursor.fetchone()[0]
    print(f"   إجمالي التذكيرات: {total_reminders}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM reminders WHERE sent = 0
    ''')
    pending_reminders = cursor.fetchone()[0]
    print(f"   التذكيرات المعلقة: {pending_reminders}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM reminders WHERE sent = 1
    ''')
    sent_reminders = cursor.fetchone()[0]
    print(f"   التذكيرات المرسلة: {sent_reminders}")
    
    # 6. فحص التذكيرات القادمة
    print("\n6️⃣ التذكيرات القادمة (خلال 48 ساعة)...")
    now = datetime.now()
    future = now + timedelta(hours=48)
    
    cursor.execute('''
        SELECT r.id, r.reminder_time, a.title, a.date_time, r.sent
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.reminder_time BETWEEN ? AND ?
        ORDER BY r.reminder_time
    ''', (now.strftime('%Y-%m-%d %H:%M:%S'), future.strftime('%Y-%m-%d %H:%M:%S')))
    
    upcoming = cursor.fetchall()
    if upcoming:
        print(f"✅ لديك {len(upcoming)} تذكير قادم:")
        for reminder in upcoming[:5]:  # أول 5 فقط
            rid, rtime, title, atime, sent = reminder
            status = "✅" if sent else "⏳"
            print(f"   {status} {rtime} → {title} (الموعد: {atime})")
    else:
        print("   📭 لا توجد تذكيرات قادمة")
    
    # 7. اختبار التذكيرات الفائتة (للتنظيف)
    print("\n7️⃣ فحص التذكيرات الفائتة...")
    cursor.execute('''
        SELECT COUNT(*) FROM reminders
        WHERE reminder_time < datetime('now') AND sent = 0
    ''')
    missed = cursor.fetchone()[0]
    if missed > 0:
        print(f"⚠️ لديك {missed} تذكير فائت لم يُرسل")
        print("   (قد تحتاج لتشغيل نظام التذكيرات)")
    else:
        print("✅ لا توجد تذكيرات فائتة")
    
    conn.close()
    
    print("\n" + "="*60)
    return True


def test_reminder_logic():
    """اختبار منطق إنشاء التذكيرات"""
    print("\n" + "="*60)
    print("🧪 اختبار منطق إنشاء التذكيرات")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        ("موعد بعد 30 ساعة", timedelta(hours=30)),  # يجب إنشاء 2 تذكير
        ("موعد بعد 3 ساعات", timedelta(hours=3)),    # يجب إنشاء 1 تذكير
        ("موعد بعد 30 دقيقة", timedelta(minutes=30)), # لا تذكيرات
    ]
    
    for description, time_delta in test_cases:
        print(f"\n📝 {description}:")
        future_time = datetime.now() + time_delta
        
        try:
            apt_id = agent.db.add_appointment(
                user_id=888,
                title=description,
                description="اختبار",
                date_time=future_time,
                priority=2
            )
            
            conn = sqlite3.connect(agent.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM reminders WHERE appointment_id = ?', (apt_id,))
            reminder_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"   الموعد: {future_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   عدد التذكيرات: {reminder_count}")
            
            if time_delta > timedelta(hours=24):
                if reminder_count == 2:
                    print("   ✅ صحيح (24 ساعة + 1 ساعة قبل)")
                else:
                    print(f"   ⚠️ متوقع 2، حصلنا على {reminder_count}")
            elif time_delta > timedelta(hours=1):
                if reminder_count >= 1:
                    print("   ✅ صحيح (1 ساعة قبل على الأقل)")
                else:
                    print(f"   ⚠️ متوقع 1+، حصلنا على {reminder_count}")
            else:
                if reminder_count == 0:
                    print("   ✅ صحيح (موعد قريب جداً)")
                else:
                    print(f"   ⚠️ متوقع 0، حصلنا على {reminder_count}")
                    
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    print("\n" + "="*60)


def check_reminder_system_status():
    """فحص حالة نظام التذكيرات"""
    print("\n" + "="*60)
    print("🔍 حالة نظام التذكيرات")
    print("="*60)
    
    try:
        from telegram_bot import TelegramBot
        print("\n1️⃣ فحص telegram_bot.py...")
        print("   ✅ الملف موجود")
        
        # فحص وجود دالة check_reminders
        import inspect
        if hasattr(TelegramBot, 'check_reminders'):
            print("   ✅ دالة check_reminders موجودة")
        else:
            print("   ❌ دالة check_reminders غير موجودة")
        
        # فحص وجود دالة setup_jobs
        if hasattr(TelegramBot, 'setup_jobs'):
            print("   ✅ دالة setup_jobs موجودة")
        else:
            print("   ⚠️ دالة setup_jobs غير موجودة")
        
    except ImportError as e:
        print(f"   ❌ خطأ في استيراد telegram_bot: {e}")
    
    # فحص نظام التذكيرات البسيط
    try:
        import os
        if os.path.exists('simple_reminders.py'):
            print("\n2️⃣ نظام التذكيرات البسيط:")
            print("   ✅ simple_reminders.py موجود")
            from simple_reminders import SimpleReminderSystem
            print("   ✅ يمكن استيراد SimpleReminderSystem")
        else:
            print("\n2️⃣ نظام التذكيرات البسيط:")
            print("   ⚠️ simple_reminders.py غير موجود")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    print("\n" + "="*60)


def generate_reminder_report():
    """تقرير شامل عن التذكيرات"""
    print("\n" + "="*60)
    print("📊 تقرير التذكيرات الشامل")
    print("="*60)
    
    agent = IntelligentAgent()
    conn = sqlite3.connect(agent.db.db_path)
    cursor = conn.cursor()
    
    # إحصائيات عامة
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN sent = 1 THEN 1 END) as sent,
            COUNT(CASE WHEN sent = 0 THEN 1 END) as pending
        FROM reminders
    ''')
    
    total, sent, pending = cursor.fetchone()
    
    print(f"""
📈 الإحصائيات:
   • إجمالي التذكيرات: {total}
   • المرسلة: {sent} ({(sent/total*100) if total > 0 else 0:.1f}%)
   • المعلقة: {pending} ({(pending/total*100) if total > 0 else 0:.1f}%)
""")
    
    # التذكيرات حسب الحالة
    cursor.execute('''
        SELECT 
            DATE(reminder_time) as day,
            COUNT(*) as count,
            COUNT(CASE WHEN sent = 1 THEN 1 END) as sent_count
        FROM reminders
        WHERE reminder_time >= date('now', '-7 days')
        GROUP BY DATE(reminder_time)
        ORDER BY day
    ''')
    
    print("📅 التذكيرات حسب اليوم (آخر 7 أيام):")
    for row in cursor.fetchall():
        day, count, sent_count = row
        print(f"   • {day}: {count} تذكير ({sent_count} مرسل)")
    
    conn.close()
    print("\n" + "="*60)


if __name__ == "__main__":
    print("🚀 بدء اختبار نظام التذكيرات الشامل\n")
    
    # الاختبارات الرئيسية
    check_reminders_system()
    test_reminder_logic()
    check_reminder_system_status()
    generate_reminder_report()
    
    print("\n" + "="*60)
    print("✅ انتهت جميع الاختبارات!")
    print("="*60)
    
    print("""
💡 ملاحظات:
1. نظام التذكيرات يعمل عند تشغيل البوت
2. يتم فحص التذكيرات كل 60 ثانية
3. التذكيرات تُنشأ تلقائياً: قبل 24 ساعة و 1 ساعة
4. إذا كان الموعد قريباً (<1 ساعة)، لا تُنشأ تذكيرات

🔧 لتفعيل التذكيرات:
   python run.py → اختر 1 (تشغيل البوت)
    """)