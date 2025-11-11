# telegram_bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ContextTypes
)

# ==========================================
# المرحلة 1: التحسينات الأساسية ✅
# ==========================================
from rate_limiter import rate_limit, RateLimiter
from error_handler import ErrorHandler, global_error_handler, BotError, ErrorType
from structured_logger import app_logger, metrics
from config import Config  # استخدام Config المحسّن

# Rate Limiter عام
bot_rate_limiter = RateLimiter(max_requests=30, time_window=60)
from intelligent_agent import IntelligentAgent
from datetime import datetime, timedelta
import sqlite3

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"Exception: {context.error}")
    
    # تجاهل أخطاء Chat not found
    if "Chat not found" in str(context.error):
        logger.warning("تجاهل خطأ Chat not found")
        return
    
    # تجاهل أخطاء Conflict
    if "Conflict" in str(context.error):
        logger.warning("تجاهل خطأ Conflict")
        return

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.agent = IntelligentAgent()
        
        # إنشاء Application مع job_queue مفعّل
        self.app = Application.builder().token(token).build()
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """إعداد معالجات الأوامر والرسائل"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("appointments", self.appointments_command))
        self.app.add_handler(CommandHandler("today", self.today_command))
        self.app.add_handler(CommandHandler("week", self.week_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
        # ✅ إضافة معالج الأخطاء
        self.app.add_error_handler(error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية - رد بثلاث لغات"""
        user = update.effective_user
        
        keyboard = [
            [
                InlineKeyboardButton("📅 مواعيدي | Mes RDV | My Appointments", callback_data='appointments'),
            ],
            [
                InlineKeyboardButton("📊 اليوم | Aujourd'hui | Today", callback_data='today'),
                InlineKeyboardButton("📆 الأسبوع | Semaine | Week", callback_data='week')
            ],
            [
                InlineKeyboardButton("ℹ️ مساعدة | Aide | Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"""مرحباً {user.first_name}! 👋
Bonjour {user.first_name}! 👋
Hello {user.first_name}! 👋

أنا مساعدك الذكي المتطور 🤖
Je suis votre assistant intelligent 🤖
I'm your advanced intelligent assistant 🤖

أستطيع | Je peux | I can:
✅ تنظيم مواعيدك | Organiser vos RDV | Organize appointments
✅ التذكير بالمواعيد | Vous rappeler | Send reminders
✅ فهم 3 لغات | Comprendre 3 langues | Understand 3 languages
✅ التعلم من تفاعلاتك | Apprendre | Learn from interactions

ماذا تريد؟ | Que voulez-vous? | What would you like?"""
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة - متعدد اللغات"""
        help_text = """
🇸🇦 **العربية:**
• اكتب رسالة طبيعية: "موعد غداً الساعة 3"
• /appointments - عرض جميع المواعيد
• /today - مواعيد اليوم
• /week - مواعيد الأسبوع

🇫🇷 **Français:**
• Écrivez naturellement: "RDV demain à 15h"
• /appointments - Tous les rendez-vous
• /today - RDV d'aujourd'hui
• /week - RDV de la semaine

🇬🇧 **English:**
• Write naturally: "Appointment tomorrow at 3pm"
• /appointments - All appointments
• /today - Today's appointments
• /week - This week's appointments

💡 **أمثلة | Exemples | Examples:**
• "موعد مع الطبيب غداً الساعة 10"
• "RDV avec le dentiste demain à 14h"
• "Meeting with client tomorrow at 3pm"
        """
        
        if update.message:
            await update.message.reply_text(help_text, parse_mode='Markdown')
        else:
            await update.callback_query.message.reply_text(help_text, parse_mode='Markdown')
    
    async def appointments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض جميع المواعيد - بثلاث لغات"""
        user_id = update.effective_user.id
        appointments = self.agent.db.get_appointments(user_id)
        
        if not appointments:
            no_apt_msg = """📭 لا توجد مواعيد حالياً
📭 Aucun rendez-vous pour le moment
📭 No appointments at the moment"""
            message = no_apt_msg
        else:
            header = """📋 **مواعيدك | Vos rendez-vous | Your appointments:**

"""
            message = header
            
            for apt in appointments:
                priority_emoji = "🔴" if apt['priority'] == 1 else "🟡" if apt['priority'] == 2 else "🟢"
                apt_date = datetime.strptime(apt['date_time'], '%Y-%m-%d %H:%M:%S')
                
                message += f"{priority_emoji} **{apt['title']}**\n"
                message += f"📅 {apt_date.strftime('%d/%m/%Y %H:%M')}\n"
                if apt['description']:
                    message += f"📝 {apt['description'][:50]}...\n"
                message += "\n"
        
        if update.message:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.callback_query.message.reply_text(message, parse_mode='Markdown')
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مواعيد اليوم - بثلاث لغات"""
        user_id = update.effective_user.id
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59)
        
        appointments = self.agent.db.get_appointments(
            user_id, 
            today_start.strftime('%Y-%m-%d %H:%M:%S'),
            today_end.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        header = f"""📅 **مواعيد اليوم | Aujourd'hui | Today**
**{datetime.now().strftime('%d/%m/%Y')}**

"""
        
        message = header
        
        if not appointments:
            no_apt = """✨ لا توجد مواعيد لليوم
✨ Aucun RDV aujourd'hui
✨ No appointments today"""
            message += no_apt
        else:
            for apt in appointments:
                apt_date = datetime.strptime(apt['date_time'], '%Y-%m-%d %H:%M:%S')
                message += f"🕐 **{apt_date.strftime('%H:%M')}** - {apt['title']}\n"
        
        if update.message:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.callback_query.message.reply_text(message, parse_mode='Markdown')
    
    async def week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مواعيد الأسبوع - بثلاث لغات"""
        user_id = update.effective_user.id
        week_start = datetime.now().replace(hour=0, minute=0, second=0)
        week_end = week_start + timedelta(days=7)
        
        appointments = self.agent.db.get_appointments(
            user_id,
            week_start.strftime('%Y-%m-%d %H:%M:%S'),
            week_end.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        header = """📆 **مواعيد الأسبوع | Cette semaine | This week:**

"""
        
        message = header
        
        if not appointments:
            no_apt = """✨ لا توجد مواعيد هذا الأسبوع
✨ Aucun RDV cette semaine
✨ No appointments this week"""
            message += no_apt
        else:
            current_day = None
            for apt in appointments:
                apt_date = datetime.strptime(apt['date_time'], '%Y-%m-%d %H:%M:%S')
                day_str = apt_date.strftime('%A %d/%m')
                
                if day_str != current_day:
                    message += f"\n**{day_str}**\n"
                    current_day = day_str
                
                message += f"  🕐 {apt_date.strftime('%H:%M')} - {apt['title']}\n"
        
        if update.message:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.callback_query.message.reply_text(message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # إظهار أن البوت يكتب
        await update.message.chat.send_action("typing")
        
        # معالجة الرسالة بواسطة الوكيل الذكي
        response = self.agent.process_message(user_id, message_text)
        
        # إرسال الرد
        await update.message.reply_text(response)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة ضغطات الأزرار"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'appointments':
            await self.appointments_command(update, context)
        elif query.data == 'today':
            await self.today_command(update, context)
        elif query.data == 'week':
            await self.week_command(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)
    
    async def check_reminders(self, context: ContextTypes.DEFAULT_TYPE):
        """✅ فحص التذكيرات وإرسالها - محدّث مع تذكير عند الموعد"""
        try:
            # استيراد دالة حساب الوقت المتبقي
            try:
                from time_utils import get_time_remaining_message
                has_time_utils = True
            except ImportError:
                has_time_utils = False
        
            conn = sqlite3.connect(self.agent.db.db_path)
            cursor = conn.cursor()
        
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
            # جلب التذكيرات مع نوعها (custom_message)
            cursor.execute('''
                SELECT r.id, r.appointment_id, a.user_id, a.title, a.date_time, r.custom_message
                FROM reminders r
                JOIN appointments a ON r.appointment_id = a.id
                WHERE r.reminder_time <= ? AND r.sent = 0
            ''', (now,))
        
            reminders = cursor.fetchall()
        
            if reminders:
                logger.info(f"🔔 وجدت {len(reminders)} تذكير لإرسالها")
        
            for reminder in reminders:
                reminder_id, apt_id, user_id, title, apt_time, custom_msg = reminder
            
                # تنظيف التاريخ
                if '.' in apt_time:
                    apt_time = apt_time.split('.')[0]
            
                # تحديد نوع التذكير
                reminder_type = "advance"  # افتراضي
                if custom_msg and "type:" in custom_msg:
                    reminder_type = custom_msg.split("type:")[1].strip()
            
                # ✨ رسالة مختلفة حسب نوع التذكير
                if reminder_type == "now":
                    # 🚨 تذكير عند الموعد - رسالة إلحاحية!
                    message = f"""🚨 **حان وقت الموعد! | C'est l'heure! | It's time!** 🚨

    📋 **{title}**
    📅 {apt_time}

    ⏰ **موعدك الآن!**
    ⏰ **Votre RDV maintenant!**
    ⏰ **Your appointment is NOW!**

    🏃‍♂️ لا تتأخر! | Ne soyez pas en retard! | Don't be late!"""
                else:
                    # 🔔 تذكير عادي (قبل الموعد)
                    # حساب الوقت المتبقي
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
            
                try:
                    await context.bot.send_message(
                    chat_id=user_id, 
                    text=message, 
                    parse_mode='Markdown'
                    )
                
                    cursor.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
                    conn.commit()
                
                    emoji = "🚨" if reminder_type == "now" else "✅"
                    logger.info(f"{emoji} تم إرسال تذكير ({reminder_type}) للمستخدم {user_id}")
                
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال تذكير: {e}")
        
            conn.close()
        
        except Exception as e:
            logger.error(f"❌ خطأ في فحص التذكيرات: {e}")
    
    def setup_jobs(self):
        """إعداد المهام الدورية (التذكيرات)"""
        try:
            # المحاولة 1: استخدام job_queue المدمج
            if self.app.job_queue is not None:
                self.app.job_queue.run_repeating(
                    self.check_reminders, 
                    interval=60,
                    first=10
                )
                logger.info("✅ تم تفعيل نظام التذكيرات (job_queue)")
                print("✅ نظام التذكيرات مفعّل (job_queue)")
                return True
            else:
                # المحاولة 2: استخدام النظام البديل
                logger.warning("⚠️ job_queue غير متوفر - استخدام النظام البديل")
                print("⚠️ job_queue غير متاح - استخدام النظام البديل...")
                
                try:
                    from reminder_system import BackgroundReminderSystem
                    
                    self.reminder_system = BackgroundReminderSystem(self.app, self.agent.db.db_path)
                    self.reminder_system.start()
                    
                    logger.info("✅ تم تفعيل النظام البديل")
                    print("✅ نظام التذكيرات مفعّل (background thread)")
                    return True
                    
                except ImportError:
                    logger.error("❌ reminder_system.py غير موجود")
                    print("❌ لم يتم العثور على reminder_system.py")
                    print("\n📝 الحل:")
                    print("   pip install 'python-telegram-bot[job-queue]'")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد التذكيرات: {e}")
            print(f"❌ فشل تفعيل التذكيرات: {e}")
            return False
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل البوت...")
        print("\n" + "="*60)
        print("🤖 البوت Lamis - تشغيل")
        print("="*60)
        
        # تفعيل نظام التذكيرات
        print("\n🔔 تفعيل نظام التذكيرات...")
        reminders_ok = self.setup_jobs()
        
        if reminders_ok:
            print("   ✅ التذكيرات ستُفحص كل 60 ثانية")
        else:
            print("   ⚠️ التذكيرات لن تعمل")
        
        # تشغيل البوت
        print("\n✅ البوت جاهز!")
        print("📱 افتح Telegram وأرسل: /start")
        print("⏹️  اضغط Ctrl+C للإيقاف")
        print("="*60 + "\n")
        
        logger.info("✅ البوت يعمل الآن")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import os
    from config import Config
    
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ يجب تعيين Token البوت!")
        print("عدّل config.py أو أضف TELEGRAM_BOT_TOKEN في متغيرات البيئة")
    else:
        bot = TelegramBot(BOT_TOKEN)
        bot.run()