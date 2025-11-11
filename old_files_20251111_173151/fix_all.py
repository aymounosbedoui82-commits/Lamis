#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 إصلاح شامل لمشاكل Lamis Bot
⚡ حل سريع بنقرة واحدة
"""

import sqlite3
import os
from datetime import datetime

def print_header(title):
    """طباعة عنوان منسق"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def fix_duplicates():
    """إصلاح المواعيد المكررة"""
    print_header("🔧 إصلاح المواعيد المكررة")
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print(f"\n⚠️ قاعدة البيانات غير موجودة: {db_path}")
        print("💡 تأكد من أنك في المجلد الصحيح")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص المكررات
        cursor.execute('''
            SELECT user_id, title, date_time, COUNT(*) as count
            FROM appointments
            GROUP BY user_id, title, date_time
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("\n✅ لا توجد مواعيد مكررة!")
            conn.close()
            return True
        
        print(f"\n⚠️ وجدت {len(duplicates)} مجموعة مكررة:")
        total_duplicates = 0
        for user_id, title, date_time, count in duplicates:
            total_duplicates += (count - 1)
            print(f"   • '{title[:30]}...' ({count} مرة)")
        
        print(f"\n🗑️ سيتم حذف {total_duplicates} موعد مكرر")
        print("💡 سيتم الاحتفاظ بأحدث نسخة من كل موعد")
        
        # حذف المكررات
        deleted = 0
        for user_id, title, date_time, count in duplicates:
            cursor.execute('''
                SELECT id, created_at
                FROM appointments
                WHERE user_id = ? AND title = ? AND date_time = ?
                ORDER BY created_at DESC
            ''', (user_id, title, date_time))
            
            all_ids = cursor.fetchall()
            ids_to_delete = [row[0] for row in all_ids[1:]]
            
            if ids_to_delete:
                placeholders = ','.join('?' * len(ids_to_delete))
                cursor.execute(
                    f'DELETE FROM appointments WHERE id IN ({placeholders})',
                    ids_to_delete
                )
                deleted += len(ids_to_delete)
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ تم! حُذف {deleted} موعد مكرر")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False


def add_calendar_command():
    """إضافة أمر /calendar"""
    print_header("➕ إضافة أمر /calendar")
    
    telegram_bot = "telegram_bot.py"
    
    if not os.path.exists(telegram_bot):
        print(f"\n⚠️ {telegram_bot} غير موجود")
        print("💡 تأكد من أنك في المجلد الصحيح")
        return False
    
    try:
        with open(telegram_bot, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # فحص إذا كان موجود
        if 'CommandHandler("calendar"' in content or "CommandHandler('calendar'" in content:
            print("\n✅ أمر /calendar موجود بالفعل!")
            return True
        
        # إضافة الأمر
        old_line = 'self.app.add_handler(CommandHandler("week", self.week_command))'
        new_line = old_line + '\n        self.app.add_handler(CommandHandler("calendar", self.week_command))  # Alias'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open(telegram_bot, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("\n✅ تم! /calendar يعمل الآن")
            print("💡 يعمل مثل /week تماماً")
            return True
        else:
            print("\n⚠️ لم يتم العثور على الموقع المناسب")
            print("💡 أضف هذا السطر يدوياً في _setup_handlers:")
            print('   self.app.add_handler(CommandHandler("calendar", self.week_command))')
            return False
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False


def show_stats():
    """عرض إحصائيات المواعيد"""
    print_header("📊 إحصائيات المواعيد")
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print(f"\n⚠️ قاعدة البيانات غير موجودة")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إجمالي
        cursor.execute('SELECT COUNT(*) FROM appointments')
        total = cursor.fetchone()[0]
        print(f"\n📋 إجمالي المواعيد: {total}")
        
        # حسب المستخدم
        cursor.execute('''
            SELECT user_id, COUNT(*) as count
            FROM appointments
            GROUP BY user_id
        ''')
        by_user = cursor.fetchall()
        print(f"\n👥 حسب المستخدم:")
        for user_id, count in by_user:
            print(f"   • مستخدم {user_id}: {count} موعد")
        
        # اليوم
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM appointments
            WHERE date(date_time) = ?
        ''', (today,))
        today_count = cursor.fetchone()[0]
        print(f"\n📅 مواعيد اليوم: {today_count}")
        
        # القادم
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT COUNT(*) FROM appointments
            WHERE date_time >= ?
        ''', (now,))
        upcoming = cursor.fetchone()[0]
        print(f"⏭️ مواعيد قادمة: {upcoming}")
        print(f"⏮️ مواعيد سابقة: {total - upcoming}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return False


def main():
    """الإصلاح الشامل"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  🔧 إصلاح شامل - Lamis Bot                      ║
║                                                                  ║
║  سيتم إصلاح:                                                    ║
║  ✅ المواعيد المكررة                                            ║
║  ✅ إضافة أمر /calendar                                         ║
║  ✅ عرض الإحصائيات                                             ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # التحقق من المجلد
    if not os.path.exists('agent_data.db') and not os.path.exists('telegram_bot.py'):
        print("\n❌ هذا ليس مجلد المشروع!")
        print("💡 انتقل إلى مجلد المشروع أولاً:")
        print("   cd /path/to/lamis-bot")
        print("   python fix_all.py")
        return
    
    results = {
        'duplicates': False,
        'calendar': False,
        'stats': False
    }
    
    # 1. إصلاح المكررات
    results['duplicates'] = fix_duplicates()
    
    # 2. إضافة /calendar
    results['calendar'] = add_calendar_command()
    
    # 3. عرض الإحصائيات
    results['stats'] = show_stats()
    
    # الملخص النهائي
    print_header("✅ ملخص النتائج")
    
    print("\n📊 الإصلاحات:")
    print(f"   {'✅' if results['duplicates'] else '❌'} إصلاح المواعيد المكررة")
    print(f"   {'✅' if results['calendar'] else '❌'} إضافة /calendar")
    print(f"   {'✅' if results['stats'] else '❌'} عرض الإحصائيات")
    
    if all(results.values()):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                     🎉 تم بنجاح!                                 ║
╚══════════════════════════════════════════════════════════════════╝

📝 الخطوات التالية:

1. أعد تشغيل البوت:
   python run.py

2. اختبر الإصلاحات:
   /today      → تحقق من عدم التكرار
   /calendar   → يجب أن يعمل الآن

3. استمتع! 🚀
        """)
    else:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                  ⚠️ بعض الإصلاحات فشلت                         ║
╚══════════════════════════════════════════════════════════════════╝

📝 راجع الرسائل أعلاه لمعرفة السبب
💡 أو تواصل للحصول على المساعدة
        """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()