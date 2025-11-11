#!/usr/bin/env python3
# check_database.py
"""
فحص شامل لقاعدة البيانات والتذكيرات
"""

import sqlite3
from datetime import datetime
import os

def check_database():
    """فحص قاعدة البيانات"""
    print("="*60)
    print("🔍 فحص قاعدة البيانات")
    print("="*60)
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة!")
        print(f"   المسار: {os.path.abspath(db_path)}")
        return False
    
    print(f"✅ قاعدة البيانات موجودة")
    print(f"   المسار: {os.path.abspath(db_path)}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. فحص الجداول
    print("\n📋 الجداول:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   • {table}: {count} صف")
    
    # 2. فحص المواعيد الأخيرة
    print("\n📅 آخر 5 مواعيد:")
    cursor.execute('''
        SELECT id, user_id, title, date_time, created_at
        FROM appointments
        ORDER BY id DESC
        LIMIT 5
    ''')
    
    appointments = cursor.fetchall()
    if appointments:
        for apt in appointments:
            apt_id, user_id, title, date_time, created_at = apt
            print(f"   • موعد #{apt_id}: {title[:30]}...")
            print(f"     المستخدم: {user_id}")
            print(f"     التاريخ: {date_time}")
            print(f"     تم إنشاؤه: {created_at}")
            
            # فحص التذكيرات لهذا الموعد
            cursor.execute('''
                SELECT COUNT(*) FROM reminders WHERE appointment_id = ?
            ''', (apt_id,))
            reminder_count = cursor.fetchone()[0]
            print(f"     🔔 التذكيرات: {reminder_count}")
            print()
    else:
        print("   ⚠️ لا توجد مواعيد")
    
    # 3. فحص التذكيرات
    print("\n🔔 التذكيرات:")
    cursor.execute('SELECT COUNT(*) FROM reminders')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reminders WHERE sent = 0')
    pending = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reminders WHERE sent = 1')
    sent = cursor.fetchone()[0]
    
    print(f"   • الإجمالي: {total}")
    print(f"   • المعلقة: {pending}")
    print(f"   • المرسلة: {sent}")
    
    # 4. التذكيرات المتأخرة
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        SELECT COUNT(*) FROM reminders
        WHERE reminder_time <= ? AND sent = 0
    ''', (now,))
    overdue = cursor.fetchone()[0]
    
    if overdue > 0:
        print(f"\n⚠️  تذكيرات متأخرة (يجب إرسالها): {overdue}")
        
        cursor.execute('''
            SELECT r.id, r.reminder_time, a.title, a.user_id
            FROM reminders r
            JOIN appointments a ON r.appointment_id = a.id
            WHERE r.reminder_time <= ? AND r.sent = 0
            LIMIT 5
        ''', (now,))
        
        print("\n   التفاصيل:")
        for reminder in cursor.fetchall():
            rid, rtime, title, user_id = reminder
            print(f"   • تذكير #{rid}: {title[:30]}...")
            print(f"     الوقت: {rtime}")
            print(f"     المستخدم: {user_id}")
    else:
        print(f"\n✅ لا توجد تذكيرات متأخرة")
    
    # 5. فحص بنية جدول التذكيرات
    print("\n🏗️  بنية جدول reminders:")
    cursor.execute("PRAGMA table_info(reminders)")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, name, col_type, notnull, default, pk = col
        print(f"   • {name} ({col_type})")
    
    conn.close()
    
    print("\n" + "="*60)
    return True


def test_add_appointment_manually():
    """اختبار إضافة موعد يدوياً"""
    print("\n" + "="*60)
    print("🧪 اختبار إضافة موعد")
    print("="*60)
    
    try:
        from intelligent_agent import IntelligentAgent
        from datetime import datetime, timedelta
        
        agent = IntelligentAgent()
        
        # إنشاء موعد بعد 25 دقيقة
        future_time = datetime.now() + timedelta(minutes=25)
        
        print(f"\n📝 إنشاء موعد اختباري...")
        print(f"   الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   وقت الموعد: {future_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        apt_id = agent.db.add_appointment(
            user_id=99999,
            title="اختبار - موعد تجريبي",
            description="اختبار النظام",
            date_time=future_time,
            priority=1
        )
        
        print(f"✅ تم إنشاء موعد رقم: {apt_id}")
        
        # فحص التذكيرات المُنشأة
        conn = sqlite3.connect(agent.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, reminder_time, sent
            FROM reminders
            WHERE appointment_id = ?
            ORDER BY reminder_time
        ''', (apt_id,))
        
        reminders = cursor.fetchall()
        
        print(f"\n🔔 التذكيرات المُنشأة: {len(reminders)}")
        
        if len(reminders) == 0:
            print("   ❌ لم يتم إنشاء أي تذكيرات!")
            print("   المشكلة: دالة add_appointment لا تعمل بشكل صحيح")
        else:
            now = datetime.now()
            for reminder in reminders:
                rid, rtime, sent = reminder
                
                # تنظيف التاريخ
                if '.' in rtime:
                    rtime = rtime.split('.')[0]
                
                rtime_dt = datetime.strptime(rtime, '%Y-%m-%d %H:%M:%S')
                diff = (rtime_dt - now).total_seconds() / 60
                
                if diff < 0:
                    print(f"   • تذكير #{rid}: متأخر {abs(int(diff))} دقيقة 🚨")
                else:
                    print(f"   • تذكير #{rid}: بعد {int(diff)} دقيقة ⏰")
        
        conn.close()
        
        print("\n" + "="*60)
        return apt_id
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n🚀 فحص شامل للنظام\n")
    
    # 1. فحص قاعدة البيانات
    db_ok = check_database()
    
    if not db_ok:
        print("\n❌ قاعدة البيانات بها مشاكل!")
        exit(1)
    
    # 2. اختبار إضافة موعد
    apt_id = test_add_appointment_manually()
    
    if apt_id:
        print("\n✅ الاختبار نجح!")
        print(f"\n💡 الخطوة التالية:")
        print(f"   1. شغّل البوت: python telegram_bot.py")
        print(f"   2. يجب أن ترى التذكير #{apt_id} يُرسل تلقائياً")
    else:
        print("\n❌ فشل الاختبار!")
        print("\n🔧 يجب إصلاح دالة add_appointment")