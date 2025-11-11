# reminder_system.py - نسخة محدثة ✅
"""
نظام تذكيرات بديل - يعمل بدون job_queue
✅ محدّث: دعم التذكير عند وقت الموعد
"""

import threading
import time
import sqlite3
from datetime import datetime
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

class BackgroundReminderSystem:
    """نظام تذكيرات يعمل في الخلفية - محدّث"""
    
    def __init__(self, bot_application, db_path="agent_data.db"):
        self.bot = bot_application.bot
        self.db_path = db_path
        self.running = False
        self.thread = None
        self._loop = None
        
    def _get_event_loop(self):
        """الحصول على event loop البوت"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                try:
                    self._loop = asyncio.get_event_loop()
                except:
                    self._loop = asyncio.new_event_loop()
                    
        return self._loop
    
    def check_and_send_reminders(self):
        """✅ فحص وإرسال التذكيرات - مع دعم التذكير عند الموعد"""
        try:
            # استيراد دالة حساب الوقت المتبقي
            try:
                from time_utils import get_time_remaining_message
                has_time_utils = True
            except ImportError:
                has_time_utils = False
                logger.warning("⚠️ time_utils.py غير موجود")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # البحث عن تذكيرات يجب إرسالها (مع نوعها)
            cursor.execute('''
                SELECT r.id, r.appointment_id, a.user_id, a.title, a.date_time, r.custom_message
                FROM reminders r
                JOIN appointments a ON r.appointment_id = a.id
                WHERE r.reminder_time <= ? AND r.sent = 0
            ''', (now,))
            
            reminders = cursor.fetchall()
            
            if reminders:
                logger.info(f"🔔 وجدت {len(reminders)} تذكير لإرسالها")
                print(f"🔔 إرسال {len(reminders)} تذكير...")
            
            for reminder in reminders:
                reminder_id, apt_id, user_id, title, apt_time, custom_msg = reminder
                
                # تنظيف التاريخ
                if '.' in apt_time:
                    apt_time = apt_time.split('.')[0]
                
                # تحديد نوع التذكير
                reminder_type = "advance"
                if custom_msg and "type:" in custom_msg:
                    reminder_type = custom_msg.split("type:")[1].strip()
                
                # ✨ رسالة مختلفة حسب نوع التذكير
                if reminder_type == "now":
                    # 🚨 تذكير عند الموعد
                    message = f"""🚨 **حان وقت الموعد! | C'est l'heure! | It's time!** 🚨

📋 **{title}**
📅 {apt_time}

⏰ **موعدك الآن!**
⏰ **Votre RDV maintenant!**
⏰ **Your appointment is NOW!**

🏃‍♂️ لا تتأخر! | Ne soyez pas en retard! | Don't be late!"""
                else:
                    # 🔔 تذكير عادي
                    time_remaining_msg = ""
                    if has_time_utils:
                        try:
                            apt_datetime = datetime.strptime(apt_time, '%Y-%m-%d %H:%M:%S')
                            time_remaining_msg = "\n\n" + get_time_remaining_message(apt_datetime)
                        except Exception as e:
                            logger.warning(f"خطأ في حساب الوقت: {e}")
                    
                    message = f"""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 {title}
📅 {apt_time}{time_remaining_msg}

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!"""
                
                # إرسال الرسالة
                success = self._send_message_sync(user_id, message)
                
                if success:
                    cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
                    conn.commit()
                    
                    emoji = "🚨" if reminder_type == "now" else "✅"
                    logger.info(f"{emoji} تم إرسال تذكير ({reminder_type}) للمستخدم {user_id}")
                    print(f"{emoji} تذكير #{reminder_id} → تم الإرسال ({reminder_type})")
                else:
                    logger.error(f"❌ فشل إرسال تذكير #{reminder_id}")
                    print(f"❌ تذكير #{reminder_id} → فشل")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في فحص التذكيرات: {e}")
            print(f"❌ خطأ: {e}")
    
    def _send_message_sync(self, chat_id: int, text: str) -> bool:
        """إرسال رسالة بشكل متزامن من thread منفصل"""
        try:
            async def send():
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown'
                )
            
            try:
                loop = self._get_event_loop()
                
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(send(), loop)
                    future.result(timeout=10)
                else:
                    loop.run_until_complete(send())
                
                return True
                
            except Exception as e:
                logger.error(f"خطأ في الطريقة 1: {e}")
                
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(send())
                    new_loop.close()
                    return True
                except Exception as e2:
                    logger.error(f"خطأ في الطريقة 2: {e2}")
                    return False
                    
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة: {e}")
            return False
    
    def reminder_loop(self):
        """حلقة فحص التذكيرات"""
        logger.info("🔔 بدء نظام التذكيرات في الخلفية...")
        print("🔔 نظام التذكيرات يعمل...")
        
        while self.running:
            try:
                self.check_and_send_reminders()
                time.sleep(60)
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة التذكيرات: {e}")
                time.sleep(60)
    
    def start(self):
        """بدء نظام التذكيرات"""
        if not self.running:
            self.running = True
            
            try:
                self._loop = asyncio.get_running_loop()
                logger.info("✅ تم الحصول على event loop")
            except:
                logger.warning("⚠️ لم يتم العثور على running loop")
            
            self.thread = threading.Thread(
                target=self.reminder_loop,
                daemon=True,
                name="ReminderThread"
            )
            self.thread.start()
            
            logger.info("✅ تم تشغيل نظام التذكيرات")
            print("✅ نظام التذكيرات مفعّل (background thread)")
    
    def stop(self):
        """إيقاف نظام التذكيرات"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ تم إيقاف نظام التذكيرات")