# simple_reminders.py
"""
نظام تذكيرات بسيط يعمل في خيط منفصل (thread)
✅ تم إصلاح مشكلة Event loop is closed
"""

import threading
import time
import sqlite3
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class SimpleReminderSystem:
    """نظام تذكيرات بسيط باستخدام threads"""
    
    def __init__(self, bot_app, db_path="agent_data.db"):
        self.bot_app = bot_app
        self.db_path = db_path
        self.running = False
        self.thread = None
    
    def check_reminders_sync(self):
        """فحص التذكيرات (نسخة متزامنة)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                SELECT r.id, r.appointment_id, a.user_id, a.title, a.date_time
                FROM reminders r
                JOIN appointments a ON r.appointment_id = a.id
                WHERE r.reminder_time <= ? AND r.sent = 0
            ''', (now,))
            
            reminders = cursor.fetchall()
            
            if reminders:
                logger.info(f"🔔 وجدت {len(reminders)} تذكير لإرسالها")
            
            for reminder in reminders:
                reminder_id, apt_id, user_id, title, apt_time = reminder
                
                # تنظيف التاريخ من microseconds
                if '.' in apt_time:
                    apt_time = apt_time.split('.')[0]
                
                # رسالة تذكير بثلاث لغات
                message = f"""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 {title}
📅 {apt_time}

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!"""
                
                try:
                    # ✅ الحل الأفضل: الحصول على event loop الصحيح
                    # نحاول الحصول على loop من مصادر مختلفة
                    
                    try:
                        # المحاولة 1: من bot.application
                        loop = self.bot_app._application.loop
                    except:
                        try:
                            # المحاولة 2: من updater
                            loop = self.bot_app.updater.loop
                        except:
                            # المحاولة 3: الحصول على running loop
                            try:
                                loop = asyncio.get_running_loop()
                            except:
                                # المحاولة 4: الحصول على event loop الحالي
                                loop = asyncio.get_event_loop()
                    
                    # إرسال الرسالة بشكل آمن
                    future = asyncio.run_coroutine_threadsafe(
                        self.bot_app.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='Markdown'
                        ),
                        loop
                    )
                    
                    # انتظار النتيجة (timeout 10 ثواني)
                    future.result(timeout=10)
                    
                    # تحديث حالة التذكير
                    cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
                    conn.commit()
                    logger.info(f"✅ تم إرسال تذكير للمستخدم {user_id}")
                    
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال تذكير: {e}")
                    import traceback
                    traceback.print_exc()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في فحص التذكيرات: {e}")
            import traceback
            traceback.print_exc()
    
    def reminder_loop(self):
        """حلقة فحص التذكيرات"""
        logger.info("🔔 بدء نظام التذكيرات البسيط...")
        
        while self.running:
            try:
                self.check_reminders_sync()
                time.sleep(60)  # انتظار 60 ثانية
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة التذكيرات: {e}")
                time.sleep(60)
    
    def start(self):
        """بدء نظام التذكيرات"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.reminder_loop, daemon=True)
            self.thread.start()
            logger.info("✅ تم تشغيل نظام التذكيرات")
    
    def stop(self):
        """إيقاف نظام التذكيرات"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ تم إيقاف نظام التذكيرات")


if __name__ == "__main__":
    print("هذا ملف مساعد - استخدمه من telegram_bot.py")
    print("""
✅ التحديثات:
  • تم إصلاح مشكلة Event loop is closed
  • استخدام run_coroutine_threadsafe بدلاً من new_event_loop
  • البوت الآن يعمل بشكل مستقر بعد إرسال التذكيرات
    """)