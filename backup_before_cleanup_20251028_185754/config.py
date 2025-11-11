# config.py
import os
from typing import Dict

class Config:
    """إعدادات المشروع"""
    
    # إعدادات Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")
    
    # إعدادات قاعدة البيانات
    DATABASE_PATH = "agent_data.db"
    
    # إعدادات النموذج
    MODEL_NAME = "bert-base-multilingual-cased"
    MODEL_PATH = "trained_model.pth"
    
    # إعدادات التدريب
    LEARNING_RATE = 0.001
    BATCH_SIZE = 16
    EPOCHS = 10
    VALIDATION_SPLIT = 0.2
    
    # إعدادات التعلم المستمر
    MIN_INTERACTIONS_FOR_TRAINING = 50
    AUTO_TRAIN_INTERVAL_DAYS = 7
    
    # إعدادات التذكيرات
    REMINDER_CHECK_INTERVAL = 60  # ثانية
    DEFAULT_REMINDERS = [
        {"hours_before": 24, "message_ar": "تذكير: لديك موعد غداً"},
        {"hours_before": 1, "message_ar": "تذكير: موعدك بعد ساعة"}
    ]
    
    # اللغات المدعومة
    SUPPORTED_LANGUAGES = {
        'ar': {
            'name': 'العربية',
            'code': 'ar',
            'rtl': True
        },
        'fr': {
            'name': 'Français',
            'code': 'fr',
            'rtl': False
        },
        'en': {
            'name': 'English',
            'code': 'en',
            'rtl': False
        }
    }
    
    # قوالب الرسائل
    MESSAGES = {
        'ar': {
            'welcome': "مرحباً! أنا مساعدك الذكي 🤖",
            'appointment_added': "✅ تم إضافة الموعد بنجاح!",
            'appointment_cancelled': "🗑️ تم إلغاء الموعد",
            'no_appointments': "📭 لا توجد مواعيد",
            'error': "❌ حدث خطأ، حاول مرة أخرى"
        },
        'fr': {
            'welcome': "Bonjour! Je suis votre assistant intelligent 🤖",
            'appointment_added': "✅ Rendez-vous ajouté avec succès!",
            'appointment_cancelled': "🗑️ Rendez-vous annulé",
            'no_appointments': "📭 Aucun rendez-vous",
            'error': "❌ Une erreur s'est produite"
        },
        'en': {
            'welcome': "Hello! I'm your intelligent assistant 🤖",
            'appointment_added': "✅ Appointment added successfully!",
            'appointment_cancelled': "🗑️ Appointment cancelled",
            'no_appointments': "📭 No appointments",
            'error': "❌ An error occurred"
        }
    }
    
    # تصنيفات النوايا
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
    
    # أولويات المواعيد
    PRIORITY_LEVELS = {
        1: {'name_ar': 'عاجل', 'name_en': 'Urgent', 'emoji': '🔴'},
        2: {'name_ar': 'متوسط', 'name_en': 'Medium', 'emoji': '🟡'},
        3: {'name_ar': 'منخفض', 'name_en': 'Low', 'emoji': '🟢'}
    }
    
    @classmethod
    def get_message(cls, language: str, key: str) -> str:
        """الحصول على رسالة بلغة معينة"""
        return cls.MESSAGES.get(language, cls.MESSAGES['en']).get(key, "")
    
    @classmethod
    def validate_config(cls) -> bool:
        """التحقق من صحة الإعدادات"""
        if cls.TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
            print("⚠️ تحذير: يجب تعيين TELEGRAM_BOT_TOKEN")
            return False
        return True


if __name__ == "__main__":
    # اختبار الإعدادات
    if Config.validate_config():
        print("✅ الإعدادات صحيحة")
    else:
        print("❌ يرجى مراجعة الإعدادات")
    
    print(f"\nاللغات المدعومة:")
    for lang_code, lang_info in Config.SUPPORTED_LANGUAGES.items():
        print(f"  • {lang_info['name']} ({lang_code})")