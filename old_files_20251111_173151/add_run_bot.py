#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 إضافة دالة run_bot() إلى telegram_bot.py
يُضاف في نهاية الملف
"""

import os
import shutil
from datetime import datetime

def fix_telegram_bot():
    """إضافة دالة run_bot() المفقودة"""
    
    print("="*70)
    print("🔧 إصلاح telegram_bot.py - إضافة run_bot()")
    print("="*70)
    
    if not os.path.exists('telegram_bot.py'):
        print("\n❌ telegram_bot.py غير موجود!")
        return False
    
    # نسخة احتياطية
    backup_name = f"telegram_bot.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('telegram_bot.py', backup_name)
    print(f"\n✅ نسخة احتياطية: {backup_name}")
    
    # قراءة الملف
    with open('telegram_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # فحص إذا كانت run_bot موجودة
    if 'def run_bot():' in content or 'def run_bot(' in content:
        print("\n✅ run_bot() موجودة بالفعل!")
        return True
    
    print("\n🔍 إضافة دالة run_bot()...")
    
    # الكود المطلوب إضافته
    run_bot_code = '''

# ==========================================
# دالة التشغيل الرئيسية
# ==========================================

def run_bot():
    """
    تشغيل البوت - نقطة الدخول الرئيسية
    """
    import os
    from config import Config
    
    # الحصول على Token
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
    
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("="*70)
        print("❌ يجب تعيين Token البوت!")
        print("="*70)
        print("\\n💡 الحل:")
        print("  1. أنشئ ملف .env في المجلد الرئيسي")
        print("  2. أضف السطر: TELEGRAM_BOT_TOKEN=your_token_here")
        print("  3. احصل على token من: https://t.me/BotFather")
        print("="*70)
        return
    
    try:
        # إنشاء البوت
        print("="*70)
        print("🤖 Lamis Bot - المساعد الذكي")
        print("="*70)
        print("\\n🔧 جاري التحضير...")
        
        bot = TelegramBot(BOT_TOKEN)
        
        print("✅ تم إنشاء البوت")
        print("✅ جاري تحميل المعالجات...")
        
        # إعداد المعالجات
        bot._setup_handlers()
        
        print("✅ تم تحميل المعالجات")
        
        # بدء نظام التذكيرات
        print("🔔 بدء نظام التذكيرات...")
        try:
            from reminder_system import BackgroundReminderSystem
            reminder_system = BackgroundReminderSystem(bot.app, bot.agent.db.db_path)
            reminder_system.start()
            print("✅ نظام التذكيرات يعمل")
        except Exception as e:
            print(f"⚠️ تحذير: نظام التذكيرات غير متاح: {e}")
        
        # بدء البوت
        print("\\n" + "="*70)
        print("🚀 البوت يعمل الآن!")
        print("="*70)
        print("\\n💡 الأوامر المتاحة:")
        print("  /start  - بدء البوت")
        print("  /help   - المساعدة")
        print("  /today  - مواعيد اليوم")
        print("  /week   - مواعيد الأسبوع")
        print("\\n📱 افتح Telegram وابحث عن بوتك!")
        print("⏹️  اضغط Ctrl+C للإيقاف")
        print("="*70 + "\\n")
        
        # 🔥 الأهم: بدء polling
        bot.app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        print("\\n⏹️ تم إيقاف البوت بواسطة المستخدم")
        
    except Exception as e:
        print(f"\\n❌ خطأ في تشغيل البوت: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Alias لـ run_bot"""
    run_bot()


# ==========================================
# نقطة الدخول
# ==========================================
'''
    
    # البحث عن if __name__ == "__main__"
    if 'if __name__ == "__main__"' in content:
        # إضافة قبل if __name__
        parts = content.split('if __name__ == "__main__"')
        
        # تحديث if __name__ block
        new_main_block = '''if __name__ == "__main__":
    run_bot()
'''
        
        new_content = parts[0] + run_bot_code + '\n' + new_main_block
    else:
        # إضافة في النهاية
        new_content = content + run_bot_code + '''

if __name__ == "__main__":
    run_bot()
'''
    
    # حفظ
    with open('telegram_bot.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ تم إضافة run_bot() و main()")
    
    # التحقق
    with open('telegram_bot.py', 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    if 'def run_bot():' in new_content and 'run_polling' in new_content:
        print("✅ التحقق: الدوال موجودة والكود صحيح")
        return True
    else:
        print("⚠️ قد تكون هناك مشكلة - راجع الملف")
        return False


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🔧 إصلاح telegram_bot.py - إضافة run_bot()            ║
╚══════════════════════════════════════════════════════════════════╝

المشكلة المكتشفة:
  • telegram_bot.py لا يحتوي على run_bot() أو main()
  • run.py لا يستطيع استيراد الدالة

الحل:
  • إضافة run_bot() كاملة مع run_polling()
  • إضافة main() كـ alias
  • تحديث if __name__ == "__main__"
    """)
    
    try:
        success = fix_telegram_bot()
        
        if success:
            print("\n" + "="*70)
            print("🎉 تم الإصلاح بنجاح!")
            print("="*70)
            print("\n🚀 الخطوات التالية:")
            print("  1. python run.py")
            print("  أو")
            print("  2. python telegram_bot.py")
            print("\n💡 البوت الآن جاهز للعمل!")
        else:
            print("\n⚠️ قد تكون هناك مشكلة - راجع الملف يدوياً")
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()