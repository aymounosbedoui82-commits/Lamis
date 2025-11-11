# debug_reminders.py
"""
تشخيص دقيق لمشكلة عدم إرسال التذكيرات
"""

import sqlite3
from datetime import datetime
import asyncio
import os

def check_overdue_reminders():
    """فحص التذكيرات المتأخرة"""
    print("="*60)
    print("🔍 فحص التذكيرات المتأخرة")
    print("="*60)
    
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT r.id, r.reminder_time, r.sent, a.title, a.user_id, a.date_time
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.reminder_time < ?
        ORDER BY r.reminder_time DESC
    ''', (now_str,))
    
    reminders = cursor.fetchall()
    
    print(f"\n📊 إجمالي التذكيرات المتأخرة: {len(reminders)}")
    
    pending = [r for r in reminders if r[2] == 0]
    sent = [r for r in reminders if r[2] == 1]
    
    print(f"   ❌ لم تُرسل: {len(pending)}")
    print(f"   ✅ تم إرسالها: {len(sent)}")
    
    if pending:
        print(f"\n⚠️ تذكيرات كان يجب إرسالها:")
        for r in pending[:5]:  # أول 5
            rid, rtime, sent_status, title, user_id, apt_time = r
            try:
                # محاولة قراءة التاريخ مع microseconds
                if '.' in rtime:
                    rtime_dt = datetime.strptime(rtime.split('.')[0], '%Y-%m-%d %H:%M:%S')
                else:
                    rtime_dt = datetime.strptime(rtime, '%Y-%m-%d %H:%M:%S')
                
                diff = (now - rtime_dt).total_seconds() / 60
                print(f"   • ID {rid}: {title}")
                print(f"     كان يجب إرسالها قبل {int(diff)} دقيقة")
                print(f"     للمستخدم: {user_id}")
            except Exception as e:
                print(f"   • ID {rid}: {title} (خطأ في قراءة التاريخ)")
    
    conn.close()
    print("\n" + "="*60)
    return pending


def test_bot_connection():
    """اختبار اتصال البوت"""
    print("\n" + "="*60)
    print("🤖 اختبار اتصال البوت")
    print("="*60)
    
    try:
        from config import Config
        token = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
        
        if token == "YOUR_TOKEN_HERE":
            print("\n❌ Token البوت غير معرّف!")
            print("   الحل: عدّل telegram_bot.py أو config.py")
            return False
        
        print(f"\n✅ Token موجود: {token[:10]}...")
        
        # اختبار الاتصال
        from telegram import Bot
        
        async def test():
            bot = Bot(token=token)
            me = await bot.get_me()
            print(f"✅ البوت متصل: @{me.username}")
            return True
        
        result = asyncio.run(test())
        return result
        
    except Exception as e:
        print(f"\n❌ خطأ في الاتصال: {e}")
        return False


def check_reminder_function():
    """فحص دالة التذكيرات في البوت"""
    print("\n" + "="*60)
    print("🔧 فحص دالة التذكيرات")
    print("="*60)
    
    try:
        # فحص telegram_bot.py
        with open('telegram_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # فحص وجود check_reminders
        if 'def check_reminders' in content:
            print("✅ دالة check_reminders موجودة")
        else:
            print("❌ دالة check_reminders غير موجودة!")
            return False
        
        # فحص وجود setup_jobs أو reminder_system
        if 'def setup_jobs' in content or 'SimpleReminderSystem' in content:
            print("✅ نظام التذكيرات موجود")
        else:
            print("❌ نظام تفعيل التذكيرات غير موجود!")
            print("   المشكلة: دالة check_reminders موجودة لكن غير مُفعّلة!")
            return False
        
        # فحص الاستدعاء في run()
        if 'setup_jobs()' in content or 'reminder_system.start()' in content:
            print("✅ التذكيرات مُفعّلة في run()")
        else:
            print("⚠️ التذكيرات قد لا تكون مُفعّلة في run()")
            print("   تحقق من وجود: self.setup_jobs() أو self.reminder_system.start()")
        
        return True
        
    except FileNotFoundError:
        print("❌ ملف telegram_bot.py غير موجود!")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False


def manual_send_reminder():
    """إرسال تذكير يدوياً للاختبار"""
    print("\n" + "="*60)
    print("📤 إرسال تذكير يدوياً")
    print("="*60)
    
    conn = sqlite3.connect('agent_data.db')
    cursor = conn.cursor()
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # أخذ تذكير واحد متأخر
    cursor.execute('''
        SELECT r.id, r.appointment_id, a.user_id, a.title, a.date_time
        FROM reminders r
        JOIN appointments a ON r.appointment_id = a.id
        WHERE r.sent = 0 AND r.reminder_time < ?
        ORDER BY r.reminder_time DESC
        LIMIT 1
    ''', (now_str,))
    
    result = cursor.fetchone()
    
    if not result:
        print("ℹ️ لا توجد تذكيرات متأخرة")
        conn.close()
        return
    
    reminder_id, apt_id, user_id, title, apt_time = result
    
    # تنظيف التاريخ من microseconds
    if '.' in apt_time:
        apt_time = apt_time.split('.')[0]
    
    print(f"\n📝 التذكير:")
    print(f"   ID: {reminder_id}")
    print(f"   المستخدم: {user_id}")
    print(f"   العنوان: {title}")
    print(f"   الموعد: {apt_time}")
    
    message = f"""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 {title}
📅 {apt_time}

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!"""
    
    print(f"\n📨 الرسالة:")
    print(message)
    
    try:
        from telegram import Bot
        from config import Config
        
        token = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
        
        if token == "YOUR_TOKEN_HERE":
            print("\n❌ Token البوت غير معرّف!")
            conn.close()
            return
        
        async def send():
            bot = Bot(token=token)
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # تحديث قاعدة البيانات
            cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
            conn.commit()
            
            return True
        
        print(f"\n🔄 جاري الإرسال...")
        result = asyncio.run(send())
        
        if result:
            print("✅ تم إرسال التذكير بنجاح!")
            print("📱 تحقق من Telegram الآن!")
        
    except Exception as e:
        print(f"\n❌ فشل الإرسال: {e}")
        print(f"\nتفاصيل:")
        import traceback
        traceback.print_exc()
    
    conn.close()
    print("\n" + "="*60)


def show_telegram_bot_logs():
    """عرض سجلات البوت إن وجدت"""
    print("\n" + "="*60)
    print("📋 سجلات البوت")
    print("="*60)
    
    if os.path.exists('bot.log'):
        print("\n✅ ملف السجل موجود (bot.log):")
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print("آخر 20 سطر:")
            for line in lines[-20:]:
                print(f"   {line.strip()}")
    else:
        print("\nℹ️ لا يوجد ملف سجل")
        print("   هذا طبيعي إذا كنت تشغل البوت من Terminal")


def provide_solution():
    """تقديم الحل بناءً على التشخيص"""
    print("\n" + "="*60)
    print("💡 الحل المقترح")
    print("="*60)
    
    print("""
بناءً على التشخيص، المشكلة على الأرجح واحدة من:

1️⃣ نظام التذكيرات غير مُفعّل في telegram_bot.py
────────────────────────────────────────────────

الحل:
في ملف telegram_bot.py، تأكد من وجود:

def run(self):
    logger.info("Starting bot...")
    
    # 🔔 أضف هذا السطر:
    try:
        self.setup_jobs()
    except:
        pass
    
    self.app.run_polling(allowed_updates=Update.ALL_TYPES)


2️⃣ job_queue لا يعمل
────────────────────────────────────────────────

الحل: استخدم النظام البسيط

# في telegram_bot.py
from simple_reminders import SimpleReminderSystem

def __init__(self, token):
    # ... الكود الموجود
    self.reminder_system = SimpleReminderSystem(self.app)

def run(self):
    logger.info("Starting bot...")
    self.reminder_system.start()  # 🔔 هذا مهم!
    self.app.run_polling(allowed_updates=Update.ALL_TYPES)


3️⃣ الفحص كل دقيقة طويل جداً
────────────────────────────────────────────────

الحل: قلل المدة إلى 10 ثوان للاختبار

# في simple_reminders.py أو telegram_bot.py
time.sleep(10)  # بدلاً من 60


4️⃣ خطأ في المسار أو الاستيراد
────────────────────────────────────────────────

تحقق من:
- simple_reminders.py موجود في نفس المجلد
- لا يوجد أخطاء استيراد
    """)
    
    print("="*60)


def interactive_fix():
    """إصلاح تفاعلي"""
    print("\n" + "="*60)
    print("🔧 وضع الإصلاح التفاعلي")
    print("="*60)
    
    print("\n1. هل البوت يعمل الآن؟")
    bot_running = input("   (y/n): ").lower() == 'y'
    
    if not bot_running:
        print("\n❌ يجب تشغيل البوت أولاً!")
        print("   python run.py → اختر 1")
        return
    
    print("\n2. هل ترى رسالة 'تم تشغيل نظام التذكيرات' عند التشغيل؟")
    reminder_enabled = input("   (y/n): ").lower() == 'y'
    
    if not reminder_enabled:
        print("\n❌ نظام التذكيرات غير مُفعّل!")
        print("   راجع الحل رقم 1 أو 2 أعلاه")
        return
    
    print("\n3. هل مر أكثر من دقيقة على تشغيل البوت؟")
    time_passed = input("   (y/n): ").lower() == 'y'
    
    if not time_passed:
        print("\nℹ️ انتظر دقيقة كاملة")
        print("   النظام يفحص كل 60 ثانية")
        return
    
    print("\n🤔 إذا كل شيء صحيح ولا يعمل، دعنا نختبر يدوياً...")
    test = input("   إرسال تذكير يدوياً الآن؟ (y/n): ").lower() == 'y'
    
    if test:
        manual_send_reminder()


if __name__ == "__main__":
    print("🔍 أداة تشخيص مشكلة التذكيرات\n")
    
    # التشخيص الشامل
    pending = check_overdue_reminders()
    bot_ok = test_bot_connection()
    func_ok = check_reminder_function()
    
    if pending and bot_ok and func_ok:
        print("\n" + "="*60)
        print("⚠️ التشخيص: كل شيء يبدو صحيحاً!")
        print("="*60)
        print("\nلكن التذكيرات لم تُرسل... دعنا نختبر يدوياً")
        
        test = input("\nإرسال تذكير يدوياً الآن؟ (y/n): ").lower()
        if test == 'y':
            manual_send_reminder()
    
    # الحلول
    provide_solution()
    
    # الإصلاح التفاعلي
    print("\n" + "="*60)
    fix = input("هل تريد الدخول لوضع الإصلاح التفاعلي؟ (y/n): ").lower()
    if fix == 'y':
        interactive_fix()
    
    print("\n✅ انتهى التشخيص!")