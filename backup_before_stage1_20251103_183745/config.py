# config.py - Enhanced Version ✅
"""
إعدادات المشروع المحسّنة
✅ التحسينات:
- حماية Token باستخدام dotenv
- Rate Limiting
- Error Handling محسّن
- Structured Logging
"""

import os
from typing import Dict
from dotenv import load_dotenv
import logging

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class Config:
    """إعدادات المشروع - النسخة المحسّنة ✨"""
    
    # ==========================================
    # 1. التحسين الأمني: حماية Token 🔒
    # ==========================================
    
    @staticmethod
    def get_telegram_token() -> str:
        """
        الحصول على Token بشكل آمن
        
        Returns:
            str: Telegram Bot Token
            
        Raises:
            ValueError: إذا لم يتم العثور على Token
        """
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not token or token == "YOUR_TOKEN_HERE":
            raise ValueError(
                "❌ TELEGRAM_BOT_TOKEN غير موجود!\n"
                "يرجى:\n"
                "1. إنشاء ملف .env في المجلد الرئيسي\n"
                "2. إضافة: TELEGRAM_BOT_TOKEN=your_token_here\n"
                "3. الحصول على Token من @BotFather على Telegram"
            )
        
        return token
    
    TELEGRAM_BOT_TOKEN = get_telegram_token.__func__()  # تحميل عند الاستيراد
    
    # ==========================================
    # 2. Rate Limiting ⚡
    # ==========================================
    
    # الحد الأقصى للطلبات في الدقيقة لكل مستخدم
    RATE_LIMIT_MAX_REQUESTS = 30
    RATE_LIMIT_TIME_WINDOW = 60  # ثانية
    
    # الحد الأقصى لطول الرسالة
    MAX_MESSAGE_LENGTH = 4096
    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    
    # ==========================================
    # إعدادات قاعدة البيانات
    # ==========================================
    
    DATABASE_PATH = "agent_data.db"
    
    # استخدام Connection Pool
    DATABASE_POOL_SIZE = 5
    DATABASE_TIMEOUT = 30
    
    # ==========================================
    # إعدادات النموذج
    # ==========================================
    
    MODEL_NAME = "bert-base-multilingual-cased"
    MODEL_PATH = "best_model.pth"
    
    # ==========================================
    # إعدادات التدريب
    # ==========================================
    
    LEARNING_RATE = 0.001
    BATCH_SIZE = 16
    EPOCHS = 10
    VALIDATION_SPLIT = 0.2
    
    # ==========================================
    # إعدادات التعلم المستمر
    # ==========================================
    
    MIN_INTERACTIONS_FOR_TRAINING = 50
    AUTO_TRAIN_INTERVAL_DAYS = 7
    
    # ==========================================
    # إعدادات التذكيرات
    # ==========================================
    
    REMINDER_CHECK_INTERVAL = 60  # ثانية
    
    # التذكيرات الافتراضية (بالساعات قبل الموعد)
    DEFAULT_REMINDER_HOURS = [24, 1, 0.25]  # 24 ساعة، 1 ساعة، 15 دقيقة
    
    # ==========================================
    # اللغات المدعومة
    # ==========================================
    
    SUPPORTED_LANGUAGES = {
        'ar': {
            'name': 'العربية',
            'name_english': 'Arabic',
            'code': 'ar',
            'rtl': True,
            'flag': '🇸🇦'
        },
        'fr': {
            'name': 'Français',
            'name_english': 'French',
            'code': 'fr',
            'rtl': False,
            'flag': '🇫🇷'
        },
        'en': {
            'name': 'English',
            'name_english': 'English',
            'code': 'en',
            'rtl': False,
            'flag': '🇬🇧'
        }
    }
    
    # ==========================================
    # 3. رسائل الخطأ المحسّنة 🎨
    # ==========================================
    
    ERROR_MESSAGES = {
        'ar': {
            'invalid_date': '❌ التاريخ غير صالح. حاول مثلاً: "غداً الساعة 3"',
            'no_appointments': '📭 لا توجد مواعيد. أضف موعداً جديداً! 😊',
            'database_error': '⚠️ خطأ في قاعدة البيانات. حاول مرة أخرى!',
            'rate_limit': '⏰ الكثير من الطلبات! انتظر قليلاً من فضلك.',
            'general_error': '❌ حدث خطأ. حاول مرة أخرى أو تواصل مع الدعم.'
        },
        'fr': {
            'invalid_date': '❌ Date invalide. Essayez par exemple: "demain à 15h"',
            'no_appointments': '📭 Aucun rendez-vous. Ajoutez-en un! 😊',
            'database_error': '⚠️ Erreur de base de données. Réessayez!',
            'rate_limit': '⏰ Trop de requêtes! Attendez un peu s\'il vous plaît.',
            'general_error': '❌ Une erreur s\'est produite. Réessayez ou contactez le support.'
        },
        'en': {
            'invalid_date': '❌ Invalid date. Try for example: "tomorrow at 3pm"',
            'no_appointments': '📭 No appointments. Add a new one! 😊',
            'database_error': '⚠️ Database error. Please try again!',
            'rate_limit': '⏰ Too many requests! Please wait a moment.',
            'general_error': '❌ An error occurred. Try again or contact support.'
        }
    }
    
    # ==========================================
    # قوالب الرسائل
    # ==========================================
    
    MESSAGES = {
        'ar': {
            'welcome': """مرحباً! أنا مساعدك الذكي 🤖
أساعدك في إدارة مواعيدك بذكاء!

💡 جرب:
• "موعد غداً الساعة 3"
• "عرض مواعيدي"
• "مواعيد اليوم"
""",
            'appointment_added': '✅ تم إضافة الموعد بنجاح!',
            'appointment_cancelled': '🗑️ تم إلغاء الموعد',
            'no_appointments': '📭 لا توجد مواعيد',
            'error': '❌ حدث خطأ، حاول مرة أخرى'
        },
        'fr': {
            'welcome': """Bonjour! Je suis votre assistant intelligent 🤖
Je vous aide à gérer vos rendez-vous intelligemment!

💡 Essayez:
• "RDV demain à 15h"
• "Afficher mes RDV"
• "RDV aujourd'hui"
""",
            'appointment_added': '✅ Rendez-vous ajouté avec succès!',
            'appointment_cancelled': '🗑️ Rendez-vous annulé',
            'no_appointments': '📭 Aucun rendez-vous',
            'error': '❌ Une erreur s\'est produite'
        },
        'en': {
            'welcome': """Hello! I'm your intelligent assistant 🤖
I help you manage your appointments smartly!

💡 Try:
• "Appointment tomorrow at 3pm"
• "Show my appointments"
• "Today's appointments"
""",
            'appointment_added': '✅ Appointment added successfully!',
            'appointment_cancelled': '🗑️ Appointment cancelled',
            'no_appointments': '📭 No appointments',
            'error': '❌ An error occurred'
        }
    }
    
    # ==========================================
    # تصنيفات النوايا
    # ==========================================
    
    INTENT_LABELS = [
        'add_appointment',
        'list_appointments',
        'cancel_appointment',
        'modify_appointment',
        'greeting',
        'thanks',
        'help',
        'check_schedule',
        'set_reminder',
        'general_query'
    ]
    
    # ==========================================
    # أولويات المواعيد
    # ==========================================
    
    PRIORITY_LEVELS = {
        1: {'name_ar': 'عاجل', 'name_fr': 'Urgent', 'name_en': 'Urgent', 'emoji': '🔴'},
        2: {'name_ar': 'متوسط', 'name_fr': 'Moyen', 'name_en': 'Medium', 'emoji': '🟡'},
        3: {'name_ar': 'منخفض', 'name_fr': 'Faible', 'name_en': 'Low', 'emoji': '🟢'}
    }
    
    # ==========================================
    # 4. إعدادات Logging المحسّن 📊
    # ==========================================
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE = "lamis_bot.log"
    
    # حجم ملف Log قبل التدوير (10 MB)
    LOG_MAX_BYTES = 10 * 1024 * 1024
    LOG_BACKUP_COUNT = 5
    
    @classmethod
    def get_message(cls, language: str, key: str) -> str:
        """
        الحصول على رسالة بلغة معينة
        
        Args:
            language: كود اللغة (ar/fr/en)
            key: مفتاح الرسالة
            
        Returns:
            str: الرسالة المطلوبة
        """
        return cls.MESSAGES.get(language, cls.MESSAGES['en']).get(key, "")
    
    @classmethod
    def get_error_message(cls, language: str, error_type: str) -> str:
        """
        الحصول على رسالة خطأ بلغة معينة
        
        Args:
            language: كود اللغة (ar/fr/en)
            error_type: نوع الخطأ
            
        Returns:
            str: رسالة الخطأ
        """
        return cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en']).get(
            error_type, 
            cls.ERROR_MESSAGES[language]['general_error']
        )
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        التحقق من صحة الإعدادات
        
        Returns:
            bool: True إذا كانت الإعدادات صحيحة
        """
        try:
            # التحقق من Token
            if cls.TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
                print("⚠️ تحذير: يجب تعيين TELEGRAM_BOT_TOKEN")
                return False
            
            # التحقق من قاعدة البيانات
            if not cls.DATABASE_PATH:
                print("⚠️ تحذير: DATABASE_PATH غير محدد")
                return False
            
            print("✅ الإعدادات صحيحة")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في التحقق من الإعدادات: {e}")
            return False


# ==========================================
# إعداد Logger المحسّن
# ==========================================

def setup_logging():
    """إعداد نظام Logging محسّن مع تدوير الملفات"""
    from logging.handlers import RotatingFileHandler
    
    # إنشاء logger
    logger = logging.getLogger("LamisBot")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # تنسيق الرسائل
    formatter = logging.Formatter(
        Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    # معالج Console (للشاشة)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # معالج File (للملف) مع التدوير
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # إضافة المعالجات
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# ==========================================
# اختبار الإعدادات عند التشغيل
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🔍 اختبار إعدادات المشروع")
    print("="*70)
    
    # التحقق من الإعدادات
    if Config.validate_config():
        print("\n✅ جميع الإعدادات صحيحة!")
    else:
        print("\n❌ يرجى مراجعة الإعدادات")
    
    # عرض اللغات المدعومة
    print(f"\n📚 اللغات المدعومة:")
    for lang_code, lang_info in Config.SUPPORTED_LANGUAGES.items():
        print(f"  {lang_info['flag']} {lang_info['name']} ({lang_code})")
    
    # عرض إعدادات Rate Limiting
    print(f"\n⚡ Rate Limiting:")
    print(f"  • الحد الأقصى: {Config.RATE_LIMIT_MAX_REQUESTS} طلب/{Config.RATE_LIMIT_TIME_WINDOW}ث")
    
    # عرض إعدادات التذكيرات
    print(f"\n🔔 التذكيرات الافتراضية:")
    for hours in Config.DEFAULT_REMINDER_HOURS:
        if hours >= 1:
            print(f"  • {int(hours)} ساعة قبل الموعد")
        else:
            print(f"  • {int(hours * 60)} دقيقة قبل الموعد")
    
    print("\n" + "="*70)