#!/usr/bin/env python3
# fix_bot_issues.py
"""
🔧 إصلاح المشاكل المكتشفة في Lamis Bot
"""

import sqlite3
from datetime import datetime
import os

def fix_duplicate_appointments(db_path="agent_data.db"):
    """
    إصلاح المواعيد المكررة
    
    المشكلة: نفس الموعد يظهر عدة مرات
    الحل: حذف المكررات مع الاحتفاظ بالأحدث
    """
    print("="*70)
    print("🔧 إصلاح المواعيد المكررة")
    print("="*70)
    
    if not os.path.exists(db_path):
        print(f"\n❌ قاعدة البيانات غير موجودة: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. فحص المواعيد المكررة
        print("\n🔍 فحص المواعيد المكررة...")
        
        cursor.execute('''
            SELECT user_id, title, date_time, COUNT(*) as count
            FROM appointments
            GROUP BY user_id, title, date_time
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("   ✅ لا توجد مواعيد مكررة!")
            conn.close()
            return True
        
        print(f"\n⚠️ وجدت {len(duplicates)} مجموعة من المواعيد المكررة:")
        
        for user_id, title, date_time, count in duplicates:
            print(f"   • '{title}' في {date_time} (مكرر {count} مرة)")
        
        # 2. حذف المكررات (الاحتفاظ بالأحدث فقط)
        confirm = input("\n❓ هل تريد حذف المواعيد المكررة؟ (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("\n❌ تم الإلغاء")
            conn.close()
            return False
        
        print("\n🗑️ حذف المكررات...")
        deleted = 0
        
        for user_id, title, date_time, count in duplicates:
            # الحصول على جميع المواعيد المكررة
            cursor.execute('''
                SELECT id, created_at
                FROM appointments
                WHERE user_id = ? AND title = ? AND date_time = ?
                ORDER BY created_at DESC
            ''', (user_id, title, date_time))
            
            all_ids = cursor.fetchall()
            
            # الاحتفاظ بالأول (الأحدث) وحذف الباقي
            ids_to_delete = [row[0] for row in all_ids[1:]]
            
            if ids_to_delete:
                placeholders = ','.join('?' * len(ids_to_delete))
                cursor.execute(f'DELETE FROM appointments WHERE id IN ({placeholders})', ids_to_delete)
                deleted += len(ids_to_delete)
                print(f"   ✅ حذف {len(ids_to_delete)} موعد مكرر: '{title}'")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ تم حذف {deleted} موعد مكرر!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_appointment_stats(db_path="agent_data.db"):
    """عرض إحصائيات المواعيد"""
    print("\n" + "="*70)
    print("📊 إحصائيات المواعيد")
    print("="*70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إجمالي المواعيد
        cursor.execute('SELECT COUNT(*) FROM appointments')
        total = cursor.fetchone()[0]
        print(f"\n📋 إجمالي المواعيد: {total}")
        
        # المواعيد حسب المستخدم
        cursor.execute('''
            SELECT user_id, COUNT(*) as count
            FROM appointments
            GROUP BY user_id
        ''')
        by_user = cursor.fetchall()
        print(f"\n👥 المواعيد حسب المستخدم:")
        for user_id, count in by_user:
            print(f"   • المستخدم {user_id}: {count} موعد")
        
        # المواعيد اليوم
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM appointments
            WHERE date(date_time) = ?
        ''', (today,))
        today_count = cursor.fetchone()[0]
        print(f"\n📅 مواعيد اليوم ({today}): {today_count}")
        
        # المواعيد القادمة
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT COUNT(*) FROM appointments
            WHERE date_time >= ?
        ''', (now,))
        upcoming = cursor.fetchone()[0]
        print(f"⏭️ المواعيد القادمة: {upcoming}")
        
        # المواعيد السابقة
        past = total - upcoming
        print(f"⏮️ المواعيد السابقة: {past}")
        
        conn.close()
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")


def add_calendar_command():
    """
    إضافة أمر /calendar إلى البوت
    
    المشكلة: المستخدم حاول /calendar لكنه غير موجود
    الحل: إضافة الأمر
    """
    print("\n" + "="*70)
    print("➕ إضافة أمر /calendar")
    print("="*70)
    
    telegram_bot_path = "telegram_bot.py"
    
    if not os.path.exists(telegram_bot_path):
        print(f"\n❌ الملف غير موجود: {telegram_bot_path}")
        print("💡 قم بتشغيل هذا السكريبت من المجلد الرئيسي للمشروع")
        return False
    
    print("\n📝 الكود المطلوب لإضافة /calendar:")
    print("-"*70)
    
    code_to_add = '''
# في دالة _setup_handlers، أضف هذا السطر:
self.app.add_handler(CommandHandler("calendar", self.calendar_command))

# ثم أضف هذه الدالة الجديدة:
async def calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض التقويم - يعادل /week"""
    await self.week_command(update, context)
'''
    
    print(code_to_add)
    print("-"*70)
    
    print("\n💡 الخطوات:")
    print("1. افتح ملف telegram_bot.py")
    print("2. في دالة _setup_handlers (حوالي السطر 68)، أضف:")
    print("   self.app.add_handler(CommandHandler('calendar', self.calendar_command))")
    print("3. أو ببساطة، /calendar يمكن أن يكون alias لـ /week")
    print("\n✅ يمكنك أيضاً استخدام /week بدلاً من /calendar")


def create_calendar_patch():
    """إنشاء patch لإضافة /calendar"""
    patch_content = """
# إضافة هذا السطر في _setup_handlers (بعد السطر 68):
self.app.add_handler(CommandHandler("calendar", self.week_command))
"""
    
    with open("/home/claude/calendar_command_patch.txt", "w", encoding="utf-8") as f:
        f.write(patch_content)
    
    print("\n✅ تم إنشاء ملف: calendar_command_patch.txt")
    print("   يحتوي على الكود المطلوب")


def main():
    """البرنامج الرئيسي"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            🔧 إصلاح مشاكل Lamis Bot                              ║
║                                                                  ║
║  المشاكل المكتشفة:                                              ║
║  1. ❌ تكرار المواعيد في العرض                                  ║
║  2. ❌ الأمر /calendar غير موجود                                ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nالخيارات:")
    print("1. إصلاح المواعيد المكررة")
    print("2. عرض إحصائيات المواعيد")
    print("3. كيفية إضافة أمر /calendar")
    print("4. تنفيذ الكل")
    print("5. خروج")
    
    while True:
        choice = input("\n👉 اختر رقم (1-5): ").strip()
        
        if choice == '1':
            fix_duplicate_appointments()
            
        elif choice == '2':
            show_appointment_stats()
            
        elif choice == '3':
            add_calendar_command()
            create_calendar_patch()
            
        elif choice == '4':
            # تنفيذ الكل
            fix_duplicate_appointments()
            show_appointment_stats()
            add_calendar_command()
            create_calendar_patch()
            break
            
        elif choice == '5':
            print("\n👋 وداعاً!")
            break
            
        else:
            print("❌ خيار غير صحيح")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()