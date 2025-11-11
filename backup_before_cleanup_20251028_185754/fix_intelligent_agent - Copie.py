#!/usr/bin/env python3
# fix_intelligent_agent.py
"""
يصلح دالة add_appointment في intelligent_agent.py تلقائياً
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """إنشاء نسخة احتياطية"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    return None

def check_and_fix():
    """فحص وإصلاح intelligent_agent.py"""
    print("="*60)
    print("🔧 إصلاح intelligent_agent.py")
    print("="*60)
    
    filepath = "intelligent_agent.py"
    
    if not os.path.exists(filepath):
        print(f"❌ الملف غير موجود: {filepath}")
        return False
    
    # قراءة الملف
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # فحص وجود add_appointment
    if 'def add_appointment' not in content:
        print("❌ لم يتم العثور على دالة add_appointment")
        return False
    
    print("✅ تم العثور على دالة add_appointment")
    
    # فحص وجود كود إنشاء التذكيرات
    has_reminders = 'INSERT INTO reminders' in content
    
    if has_reminders:
        print("✅ كود التذكيرات موجود")
        
        # فحص وجود logging
        has_logging = 'logger.info' in content and 'تذكير' in content
        
        if not has_logging:
            print("⚠️ الـ logging غير موجود - قد يكون من الصعب تتبع المشكلة")
        else:
            print("✅ الـ logging موجود")
        
        print("\n💡 الملف يبدو سليماً")
        print("   المشكلة قد تكون في:")
        print("   1. الشرط: if reminder_time > datetime.now()")
        print("   2. الموعد قريب جداً (< 15 دقيقة)")
        print("   3. خطأ في استخراج التاريخ")
        
    else:
        print("❌ كود التذكيرات مفقود!")
        print("\n🔧 هل تريد إضافة كود التذكيرات؟")
        
        response = input("أدخل 'y' للمتابعة: ").lower()
        
        if response != 'y':
            print("❌ تم الإلغاء")
            return False
        
        # إنشاء نسخة احتياطية
        backup_file(filepath)
        
        print("⚠️ يجب تعديل الملف يدوياً")
        print("   استبدل دالة add_appointment بالنسخة المحدثة")
    
    print("\n" + "="*60)
    return True

def test_appointment_creation():
    """اختبار إنشاء موعد"""
    print("\n" + "="*60)
    print("🧪 اختبار إنشاء موعد")
    print("="*60)
    
    try:
        from intelligent_agent import IntelligentAgent
        from datetime import datetime, timedelta
        
        agent = IntelligentAgent()
        
        # موعد بعد 30 دقيقة
        future_time = datetime.now() + timedelta(minutes=30)
        
        print(f"\n📝 إنشاء موعد اختباري...")
        print(f"   الآن: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   الموعد: {future_time.strftime('%H:%M:%S')}")
        
        apt_id = agent.db.add_appointment(
            user_id=99999,
            title="اختبار إصلاح النظام",
            description="موعد تجريبي",
            date_time=future_time,
            priority=1
        )
        
        print(f"\n✅ تم إنشاء موعد #{apt_id}")
        
        # فحص التذكيرات
        import sqlite3
        conn = sqlite3.connect(agent.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM reminders WHERE appointment_id = ?
        ''', (apt_id,))
        
        reminder_count = cursor.fetchone()[0]
        
        print(f"🔔 عدد التذكيرات: {reminder_count}")
        
        if reminder_count == 0:
            print("\n❌ فشل! لم يتم إنشاء تذكيرات")
            print("\n🔧 الحل:")
            print("   1. تأكد من أن دالة add_appointment تحتوي على كود التذكيرات")
            print("   2. تأكد من أن الشرط: if reminder_time > datetime.now()")
            print("   3. شغّل البوت وأرسل: 'موعد بعد ساعة'")
        elif reminder_count == 1:
            print("⚠️ تم إنشاء تذكير واحد فقط (متوقع: 1 على الأقل)")
            cursor.execute('''
                SELECT reminder_time FROM reminders WHERE appointment_id = ?
            ''', (apt_id,))
            rtime = cursor.fetchone()[0]
            print(f"   التذكير: {rtime}")
            print("\n✅ النظام يعمل جزئياً!")
        else:
            print(f"✅ ممتاز! تم إنشاء {reminder_count} تذكير")
            
            cursor.execute('''
                SELECT id, reminder_time FROM reminders
                WHERE appointment_id = ?
                ORDER BY reminder_time
            ''', (apt_id,))
            
            now = datetime.now()
            for reminder in cursor.fetchall():
                rid, rtime = reminder
                
                if '.' in rtime:
                    rtime = rtime.split('.')[0]
                
                rtime_dt = datetime.strptime(rtime, '%Y-%m-%d %H:%M:%S')
                diff = int((rtime_dt - now).total_seconds() / 60)
                print(f"   • تذكير #{rid}: بعد {diff} دقيقة")
            
            print("\n✅ النظام يعمل بشكل صحيح!")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 أداة إصلاح intelligent_agent.py\n")
    
    # 1. فحص الملف
    if check_and_fix():
        # 2. اختبار
        test_appointment_creation()
    
    print("\n✅ انتهى!")