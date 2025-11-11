# fix_reminders.py
"""
فحص وإصلاح نظام إرسال التذكيرات
"""

import sqlite3
from datetime import datetime
import os

def check_reminder_status():
    """فحص حالة التذكيرات"""
    print("="*60)
    print("🔍 فحص حالة نظام التذكيرات")
    print("="*60)
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. إحصائيات عامة
    print("\n📊 الإحصائيات:")
    
    cursor.execute("SELECT COUNT(*) FROM reminders")
    total = cursor.fetchone()[0]
    print(f"   إجمالي التذكيرات: {total}")
    
    cursor.execute("SELECT COUNT(*) FROM reminders WHERE sent = 0")
    pending = cursor.fetchone()[0]
    print(f"   المعلقة (لم تُرسل): {pending}")
    
    cursor.execute("SELECT COUNT(*) FROM reminders WHERE sent = 1")
    sent = cursor.fetchone()[0]
    print(f"   المرسلة: {sent}")
    
    # 2. التذكيرات الفائتة (كان يجب إرسالها)
    print("\n⚠️ التذكيرات الفائتة:")
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT r.id, r.reminder_time, a.title, a.user_id
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.sent = 0 AND r.reminder_time < ?
        ORDER BY r.reminder_time DESC
        LIMIT 5
    ''', (now,))
    
    missed = cursor.fetchall()
    if missed:
        print(f"   لديك {len(missed)} تذكير فائت!")
        for reminder_id, rtime, title, user_id in missed:
            print(f"   • ID {reminder_id}: {rtime} - {title} (User: {user_id})")
    else:
        print("   ✅ لا توجد تذكيرات فائتة")
    
    # 3. التذكيرات القادمة (القريبة)
    print("\n⏰ التذكيرات القادمة (خلال ساعة):")
    
    future = (datetime.now().timestamp() + 3600)
    future_str = datetime.fromtimestamp(future).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT r.id, r.reminder_time, a.title, a.user_id
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.sent = 0 AND r.reminder_time BETWEEN ? AND ?
        ORDER BY r.reminder_time
    ''', (now, future_str))
    
    upcoming = cursor.fetchall()
    if upcoming:
        print(f"   لديك {len(upcoming)} تذكير قادم!")
        for reminder_id, rtime, title, user_id in upcoming:
            rtime_dt = datetime.strptime(rtime, '%Y-%m-%d %H:%M:%S')
            minutes_left = (rtime_dt - datetime.now()).total_seconds() / 60
            print(f"   • ID {reminder_id}: بعد {int(minutes_left)} دقيقة - {title}")
    else:
        print("   📭 لا توجد تذكيرات قادمة خلال الساعة القادمة")
    
    conn.close()
    print("\n" + "="*60)


def check_bot_status():
    """فحص حالة البوت"""
    print("\n" + "="*60)
    print("🤖 فحص حالة البوت")
    print("="*60)
    
    # فحص إذا كان البوت يعمل
    print("\n1️⃣ هل البوت يعمل؟")
    print("   للتحقق، أرسل رسالة للبوت على Telegram")
    print("   إذا رد، البوت يعمل ✅")
    print("   إذا لم يرد، البوت متوقف ❌")
    
    # فحص نظام التذكيرات
    print("\n2️⃣ نظام التذكيرات:")
    
    try:
        from telegram_bot import TelegramBot
        
        # فحص وجود الدوال
        if hasattr(TelegramBot, 'check_reminders'):
            print("   ✅ دالة check_reminders موجودة")
        else:
            print("   ❌ دالة check_reminders غير موجودة")
        
        if hasattr(TelegramBot, 'setup_jobs'):
            print("   ✅ دالة setup_jobs موجودة")
        else:
            print("   ⚠️ دالة setup_jobs غير موجودة")
            
    except Exception as e:
        print(f"   ❌ خطأ في فحص telegram_bot.py: {e}")
    
    # فحص النظام البسيط
    if os.path.exists('simple_reminders.py'):
        print("\n3️⃣ نظام التذكيرات البسيط:")
        print("   ✅ simple_reminders.py موجود")
        try:
            from simple_reminders import SimpleReminderSystem
            print("   ✅ يمكن استيراده")
        except Exception as e:
            print(f"   ⚠️ خطأ في الاستيراد: {e}")
    else:
        print("\n3️⃣ نظام التذكيرات البسيط:")
        print("   ❌ simple_reminders.py غير موجود")
    
    print("\n" + "="*60)


def manual_test_reminder():
    """اختبار يدوي لإرسال تذكير"""
    print("\n" + "="*60)
    print("🧪 اختبار يدوي لإرسال تذكير")
    print("="*60)
    
    db_path = "agent_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # البحث عن تذكير فائت
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT r.id, r.appointment_id, a.user_id, a.title, a.date_time
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.sent = 0 AND r.reminder_time < ?
        ORDER BY r.reminder_time DESC
        LIMIT 1
    ''', (now,))
    
    result = cursor.fetchone()
    
    if not result:
        print("   ℹ️ لا توجد تذكيرات فائتة للاختبار")
        conn.close()
        return
    
    reminder_id, apt_id, user_id, title, apt_time = result
    
    print(f"\n📝 تذكير للاختبار:")
    print(f"   ID: {reminder_id}")
    print(f"   المستخدم: {user_id}")
    print(f"   العنوان: {title}")
    print(f"   وقت الموعد: {apt_time}")
    
    # رسالة التذكير
    message = f"""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 {title}
📅 {apt_time}

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!"""
    
    print(f"\n📨 الرسالة التي يجب إرسالها:")
    print(message)
    
    # محاولة الإرسال
    print(f"\n🔄 محاولة الإرسال...")
    
    try:
        import asyncio
        from telegram import Bot
        from config import Config
        import os
        
        token = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
        
        if token == "YOUR_TOKEN_HERE":
            print("   ❌ Token البوت غير معرّف!")
            print("   عدّل config.py أو telegram_bot.py")
        else:
            async def send_test():
                bot = Bot(token=token)
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                print("   ✅ تم إرسال التذكير!")
                
                # تحديث قاعدة البيانات
                cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
                conn.commit()
                print("   ✅ تم تحديث قاعدة البيانات")
            
            asyncio.run(send_test())
            
    except Exception as e:
        print(f"   ❌ فشل الإرسال: {e}")
    
    conn.close()
    print("\n" + "="*60)


def fix_bot_instructions():
    """تعليمات إصلاح البوت"""
    print("\n" + "="*60)
    print("🔧 كيفية تفعيل إرسال التذكيرات")
    print("="*60)
    
    print("""
الحل 1️⃣: تأكد من تشغيل البوت
──────────────────────────────
البوت يجب أن يعمل باستمرار لإرسال التذكيرات!

# تشغيل البوت:
python run.py → اختر 1

# أو:
python telegram_bot.py

⚠️ إذا أغلقت Terminal، البوت يتوقف والتذكيرات لن تُرسل!


الحل 2️⃣: استخدام النظام البسيط
──────────────────────────────
إذا لم يعمل job_queue:

# في telegram_bot.py:
from simple_reminders import SimpleReminderSystem

def __init__(self, token):
    # ... الكود الموجود
    self.reminder_system = SimpleReminderSystem(self.app)

def run(self):
    self.reminder_system.start()  # بدء التذكيرات
    self.app.run_polling(allowed_updates=Update.ALL_TYPES)


الحل 3️⃣: تشغيل البوت في الخلفية (Linux/Mac)
──────────────────────────────
# تشغيل دائم:
nohup python telegram_bot.py > bot.log 2>&1 &

# للتحقق من البوت:
ps aux | grep telegram_bot

# لإيقاف البوت:
pkill -f telegram_bot


الحل 4️⃣: استخدام screen/tmux (Linux)
──────────────────────────────
# إنشاء جلسة:
screen -S lamis_bot

# تشغيل البوت:
python telegram_bot.py

# الانفصال: Ctrl+A ثم D
# العودة: screen -r lamis_bot


الحل 5️⃣: Windows - تشغيل كخدمة
──────────────────────────────
استخدم Task Scheduler لتشغيل البوت عند بدء النظام


🔍 التحقق من أن البوت يعمل:
──────────────────────────────
1. أرسل /start للبوت
2. إذا رد، البوت يعمل ✅
3. التذكيرات ستُرسل تلقائياً كل 60 ثانية
    """)
    
    print("="*60)


def quick_fix():
    """إصلاح سريع"""
    print("\n" + "="*60)
    print("⚡ إصلاح سريع")
    print("="*60)
    
    print("""
السبب الرئيسي: البوت غير مُشغّل! 🤖❌

الحل الفوري:
────────────

1. افتح Terminal/CMD جديد

2. شغّل البوت:
   python run.py
   اختر: 1

3. اترك Terminal مفتوحاً!

4. انتظر... التذكيرات ستُرسل تلقائياً

5. تحقق من Telegram بعد دقائق


⚠️ هام جداً:
• البوت يجب أن يعمل باستمرار
• إذا أغلقت Terminal → البوت يتوقف
• إذا البوت متوقف → لا تذكيرات!


✅ للتأكد:
أرسل /start للبوت
إذا رد → يعمل ✅
إذا لم يرد → متوقف ❌
    """)
    
    print("="*60)


if __name__ == "__main__":
    print("🚀 أداة فحص وإصلاح نظام التذكيرات\n")
    
    check_reminder_status()
    check_bot_status()
    quick_fix()
    fix_bot_instructions()
    
    print("\n" + "="*60)
    
    # سؤال المستخدم
    print("\n❓ هل تريد:")
    print("1. اختبار إرسال تذكير يدوياً")
    print("2. عرض المزيد من المعلومات")
    print("3. خروج")
    
    choice = input("\nاختيارك (1-3): ").strip()
    
    if choice == '1':
        manual_test_reminder()
    elif choice == '2':
        check_reminder_status()
    
    print("\n✅ انتهى الفحص!")