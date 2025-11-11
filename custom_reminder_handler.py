"""
Custom Reminder Handler - معالج التذكيرات المخصصة
استيراده في telegram_bot.py
"""

import re
import sqlite3
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_custom_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالج التذكيرات المخصصة
    يتعرف على أوامر مثل: "ذكرني قبل 30 دقيقة"
    """
    
    if not update.message or not update.message.text:
        return
    
    message = update.message.text
    user_id = update.effective_user.id
    
    # أنماط التذكير
    patterns = [
        (r'ذكرني قبل (\d+) دقيقة', 'minutes'),
        (r'ذكرني قبل (\d+) دقائق', 'minutes'),
        (r'ذكرني قبل ساعة', 'hour'),
        (r'ذكرني قبل يوم', 'day'),
        (r'rappelle.moi (\d+) minutes? avant', 'minutes'),
        (r'remind me (\d+) minutes? before', 'minutes')
    ]
    
    matched = False
    minutes_before = 0
    
    for pattern, type_ in patterns:
        match = re.search(pattern, message.lower(), re.IGNORECASE)
        if match:
            matched = True
            if type_ == 'minutes':
                minutes_before = int(match.group(1))
            elif type_ == 'hour':
                minutes_before = 60
            elif type_ == 'day':
                minutes_before = 1440
            break
    
    if not matched:
        return  # ليس طلب تذكير - دع المعالج العادي يتولاه
    
    try:
        # الحصول على آخر موعد للمستخدم
        conn = sqlite3.connect('agent_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM appointments 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        
        last_appointment = cursor.fetchone()
        
        if not last_appointment:
            await update.message.reply_text(
                "⚠️ لا يوجد موعد حديث لإضافة تذكير له\n"
                "أضف موعداً أولاً ثم أضف التذكير\n\n"
                "⚠️ Aucun RDV récent\n"
                "Ajoutez d'abord un RDV\n\n"
                "⚠️ No recent appointment\n"
                "Add an appointment first"
            )
            conn.close()
            return
        
        appointment_id = last_appointment[0]
        conn.close()
        
        # إضافة التذكير المخصص
        try:
            from advanced_features import CustomReminderManager
            
            reminder_mgr = CustomReminderManager('agent_data.db')
            reminder_id = reminder_mgr.add_custom_reminder(
                appointment_id=appointment_id,
                minutes_before=minutes_before,
                custom_message=f"تذكير: لديك موعد بعد {minutes_before} دقيقة"
            )
            
            await update.message.reply_text(
                f"✅ تم إضافة التذكير!\n"
                f"🔔 سأذكرك قبل {minutes_before} دقيقة من الموعد #{appointment_id}\n\n"
                f"✅ Rappel ajouté!\n"
                f"🔔 Je vous rappellerai {minutes_before} minutes avant le RDV\n\n"
                f"✅ Reminder added!\n"
                f"🔔 I'll remind you {minutes_before} minutes before the appointment"
            )
            
            logger.info(f"تم إضافة تذكير مخصص: {minutes_before} دقيقة قبل موعد #{appointment_id}")
            
        except ImportError as e:
            logger.warning(f"ميزة التذكيرات المخصصة غير متاحة: {e}")
            await update.message.reply_text(
                "⚠️ ميزة التذكيرات المخصصة غير متاحة حالياً\n"
                "⚠️ Feature not available\n"
                "⚠️ Fonctionnalité non disponible"
            )
        
    except Exception as e:
        logger.error(f"خطأ في إضافة تذكير مخصص: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ في إضافة التذكير\n"
            "❌ Error adding reminder\n"
            "❌ Erreur lors de l'ajout du rappel"
        )


# دالة مساعدة لتسجيل الـ handler
def register_custom_reminder_handler(app):
    """
    تسجيل الـ handler في التطبيق
    
    Usage في telegram_bot.py:
        from custom_reminder_handler import register_custom_reminder_handler
        register_custom_reminder_handler(app)
    """
    from telegram.ext import MessageHandler, filters
    
    # إضافة handler قبل المعالج العادي
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_custom_reminder
        ),
        group=0  # المجموعة 0 تُعالج أولاً
    )
    
    logger.info("✅ تم تسجيل handler التذكيرات المخصصة")