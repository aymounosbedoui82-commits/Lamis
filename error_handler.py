# error_handler.py
"""
نظام معالجة الأخطاء المحسّن
✅ يوفر رسائل خطأ واضحة ومفيدة بثلاث لغات
✅ يسجل الأخطاء بشكل منظم للمراجعة
"""

import logging
import traceback
from typing import Optional
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class ErrorType:
    """أنواع الأخطاء المختلفة"""
    INVALID_DATE = "invalid_date"
    NO_APPOINTMENTS = "no_appointments"
    DATABASE_ERROR = "database_error"
    RATE_LIMIT = "rate_limit"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    GENERAL_ERROR = "general_error"


class BotError(Exception):
    """خطأ مخصص للبوت"""
    
    def __init__(self, error_type: str, message: str, original_error: Optional[Exception] = None):
        """
        Args:
            error_type: نوع الخطأ
            message: رسالة الخطأ
            original_error: الخطأ الأصلي (إن وجد)
        """
        self.error_type = error_type
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class ErrorMessages:
    """رسائل الخطأ بثلاث لغات"""
    
    MESSAGES = {
        ErrorType.INVALID_DATE: {
            'ar': """❌ **التاريخ غير صالح**

💡 جرب أحد الأشكال التالية:
• "غداً الساعة 3"
• "يوم الخميس 10:30"
• "2025-11-05 15:00"
• "بعد ساعتين"

📝 مثال: "موعد مع الطبيب غداً الساعة 2"
""",
            'fr': """❌ **Date invalide**

💡 Essayez l'un de ces formats:
• "demain à 15h"
• "jeudi à 10h30"
• "2025-11-05 15:00"
• "dans 2 heures"

📝 Exemple: "RDV médecin demain à 14h"
""",
            'en': """❌ **Invalid date**

💡 Try one of these formats:
• "tomorrow at 3pm"
• "Thursday at 10:30"
• "2025-11-05 15:00"
• "in 2 hours"

📝 Example: "Doctor appointment tomorrow at 2pm"
"""
        },
        
        ErrorType.NO_APPOINTMENTS: {
            'ar': """📭 **لا توجد مواعيد**

💡 لإضافة موعد جديد:
• اكتب: "موعد مع الطبيب غداً الساعة 3"
• أو: "RDV demain à 15h"

✨ سأذكرك به في الوقت المناسب!
""",
            'fr': """📭 **Aucun rendez-vous**

💡 Pour ajouter un nouveau RDV:
• Écrivez: "RDV médecin demain à 15h"
• Ou: "موعد غداً الساعة 3"

✨ Je vous rappellerai au bon moment!
""",
            'en': """📭 **No appointments**

💡 To add a new appointment:
• Type: "Doctor appointment tomorrow at 3pm"
• Or: "موعد غداً الساعة 3"

✨ I'll remind you at the right time!
"""
        },
        
        ErrorType.DATABASE_ERROR: {
            'ar': """⚠️ **خطأ في قاعدة البيانات**

🔄 جرب مرة أخرى من فضلك
📞 إذا استمرت المشكلة، تواصل مع الدعم

💡 بياناتك آمنة ولم تُفقد
""",
            'fr': """⚠️ **Erreur de base de données**

🔄 Veuillez réessayer
📞 Si le problème persiste, contactez le support

💡 Vos données sont en sécurité
""",
            'en': """⚠️ **Database error**

🔄 Please try again
📞 If the problem persists, contact support

💡 Your data is safe
"""
        },
        
        ErrorType.RATE_LIMIT: {
            'ar': """⏰ **الكثير من الطلبات!**

🛑 انتظر قليلاً ثم حاول مرة أخرى
⏱️ الحد المسموح: 30 طلب/دقيقة

💡 هذا للحفاظ على أداء البوت للجميع
""",
            'fr': """⏰ **Trop de requêtes!**

🛑 Attendez un peu puis réessayez
⏱️ Limite: 30 requêtes/minute

💡 C'est pour maintenir les performances pour tous
""",
            'en': """⏰ **Too many requests!**

🛑 Wait a moment then try again
⏱️ Limit: 30 requests/minute

💡 This keeps the bot fast for everyone
"""
        },
        
        ErrorType.GENERAL_ERROR: {
            'ar': """❌ **حدث خطأ غير متوقع**

🔄 حاول مرة أخرى
📞 إذا استمر الخطأ، أرسل رسالة للدعم

💡 سنعمل على إصلاحه في أقرب وقت
""",
            'fr': """❌ **Une erreur inattendue s'est produite**

🔄 Réessayez
📞 Si l'erreur persiste, contactez le support

💡 Nous travaillerons à la résoudre rapidement
""",
            'en': """❌ **An unexpected error occurred**

🔄 Try again
📞 If the error persists, contact support

💡 We'll work to fix it soon
"""
        }
    }
    
    @classmethod
    def get_message(cls, error_type: str, language: str = 'ar') -> str:
        """
        الحصول على رسالة الخطأ
        
        Args:
            error_type: نوع الخطأ
            language: اللغة (ar/fr/en)
            
        Returns:
            str: رسالة الخطأ
        """
        messages = cls.MESSAGES.get(error_type, cls.MESSAGES[ErrorType.GENERAL_ERROR])
        return messages.get(language, messages['ar'])


class ErrorHandler:
    """معالج الأخطاء المركزي"""
    
    @staticmethod
    async def handle_error(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        language: str = 'ar'
    ):
        """
        معالجة الأخطاء بشكل موحد
        
        Args:
            update: التحديث من Telegram
            context: السياق
            error: الخطأ
            language: لغة الرسالة
        """
        # تحديد نوع الخطأ
        if isinstance(error, BotError):
            error_type = error.error_type
            error_msg = error.message
        else:
            error_type = ErrorType.GENERAL_ERROR
            error_msg = str(error)
        
        # تسجيل الخطأ
        logger.error(
            f"❌ Error Type: {error_type}\n"
            f"   User: {update.effective_user.id if update.effective_user else 'Unknown'}\n"
            f"   Message: {error_msg}\n"
            f"   Traceback: {traceback.format_exc()}"
        )
        
        # إرسال رسالة للمستخدم
        try:
            user_message = ErrorMessages.get_message(error_type, language)
            
            if update.message:
                await update.message.reply_text(
                    user_message,
                    parse_mode='Markdown'
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    user_message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"❌ فشل إرسال رسالة الخطأ: {e}")
    
    @staticmethod
    def log_error(
        error_type: str,
        message: str,
        user_id: Optional[int] = None,
        extra_data: Optional[dict] = None
    ):
        """
        تسجيل خطأ بتنسيق منظم
        
        Args:
            error_type: نوع الخطأ
            message: رسالة الخطأ
            user_id: معرف المستخدم (اختياري)
            extra_data: بيانات إضافية (اختياري)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'user_id': user_id,
            'extra_data': extra_data or {}
        }
        
        logger.error(f"📝 Error Log: {log_entry}")


# ==========================================
# Global Error Handler for Telegram Bot
# ==========================================

async def global_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالج الأخطاء العام للبوت
    يتم تسجيله في Application
    """
    error = context.error
    
    # تجاهل بعض الأخطاء غير المهمة
    ignored_errors = [
        "Chat not found",
        "Message is not modified",
        "Query is too old",
        "Conflict: terminated by other"
    ]
    
    error_str = str(error)
    for ignored in ignored_errors:
        if ignored in error_str:
            logger.warning(f"⚠️ تجاهل خطأ غير مهم: {ignored}")
            return
    
    # معالجة الأخطاء المهمة
    logger.error(
        f"❌ Global Error Handler:\n"
        f"   Error: {error}\n"
        f"   Type: {type(error).__name__}\n"
        f"   Update: {update}\n"
        f"   Traceback:\n{traceback.format_exc()}"
    )
    
    # محاولة الرد على المستخدم
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ حدث خطأ. حاول مرة أخرى أو اتصل بالدعم.\n"
                "❌ Une erreur est survenue. Réessayez ou contactez le support.\n"
                "❌ An error occurred. Try again or contact support."
            )
    except:
        pass


# ==========================================
# Context Manager للأخطاء
# ==========================================

class safe_operation:
    """
    Context manager لمعالجة الأخطاء بشكل آمن
    
    Usage:
        with safe_operation("add_appointment", user_id=123):
            # code here
            pass
    """
    
    def __init__(self, operation_name: str, user_id: Optional[int] = None):
        self.operation_name = operation_name
        self.user_id = user_id
    
    def __enter__(self):
        logger.info(f"▶️ بدء عملية: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            ErrorHandler.log_error(
                error_type=ErrorType.GENERAL_ERROR,
                message=f"خطأ في {self.operation_name}: {exc_val}",
                user_id=self.user_id,
                extra_data={'traceback': traceback.format_exc()}
            )
            return False  # لا تمنع انتشار الخطأ
        
        logger.info(f"✅ نجحت عملية: {self.operation_name}")
        return True


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار Error Handler")
    print("="*70)
    
    # اختبار الرسائل
    print("\n📝 رسائل الخطأ:\n")
    
    for error_type in [ErrorType.INVALID_DATE, ErrorType.NO_APPOINTMENTS, ErrorType.DATABASE_ERROR]:
        print(f"نوع الخطأ: {error_type}")
        print("-" * 50)
        message = ErrorMessages.get_message(error_type, 'ar')
        print(message)
        print()
    
    # اختبار safe_operation
    print("="*70)
    print("🧪 اختبار safe_operation")
    print("="*70)
    
    with safe_operation("test_operation", user_id=123):
        print("✅ العملية تعمل بنجاح")
    
    print("\n" + "="*70)
    print("✅ الاختبار اكتمل!")