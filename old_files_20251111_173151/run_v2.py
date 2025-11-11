#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lamis Bot - نقطة البداية المحسّنة (v2)
✅ يكشف المشكلة بوضوح
"""

import sys
import os
import subprocess
from pathlib import Path

# إضافة المجلد الحالي للمسار
sys.path.insert(0, str(Path(__file__).parent))

# استيراد Logger
from structured_logger import StructuredLogger

# إنشاء Logger
logger = StructuredLogger("LamisBot")


def check_python_version():
    """فحص إصدار Python"""
    logger.info("🔍 فحص إصدار Python...")
    
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ مطلوب")
        sys.exit(1)
    
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    logger.info(f"✅ Python {version}")


def check_config():
    """فحص ملف الإعدادات"""
    if not os.path.exists('.env'):
        logger.warning("⚠️ ملف .env غير موجود")
        logger.info("💡 استخدام .env.example كنموذج")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("✅ تم إنشاء .env")
            logger.warning("⚠️ يرجى تعديل .env وإضافة TELEGRAM_BOT_TOKEN")
            return False
    
    # فحص BOT_TOKEN
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'YOUR_BOT_TOKEN_HERE' in content or not content.strip():
                logger.error("❌ يرجى إضافة TELEGRAM_BOT_TOKEN في ملف .env")
                return False
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة .env: {e}")
        return False
    
    logger.info("✅ الإعدادات صحيحة")
    return True


def main():
    """نقطة البداية الرئيسية"""
    print("="*70)
    print("🤖 مرحباً بك في Lamis Bot - المساعد الذكي")
    print("✨ المرحلة 1: التحسينات الأساسية مطبقة")
    print("="*70)
    
    try:
        # 1. فحص Python
        check_python_version()
        
        # 2. فحص الإعدادات
        if not check_config():
            logger.error("❌ يرجى إكمال الإعدادات أولاً")
            input("\nاضغط Enter للخروج...")
            sys.exit(1)
        
        # 3. تشغيل البوت
        logger.info("🚀 تشغيل البوت...")
        
        # ✅ التحسين: نضيف تفاصيل أكثر
        try:
            logger.info("📦 جاري استيراد telegram_bot...")
            from telegram_bot import run_bot
            
            logger.info("✅ تم استيراد telegram_bot.run_bot()")
            logger.info("=" * 70)
            logger.info("🚀 البوت يعمل الآن - افتح Telegram")
            logger.info("⏹️ اضغط Ctrl+C للإيقاف")
            logger.info("=" * 70)
            
            # 🔥 هنا المشكلة المحتملة:
            # إذا run_bot() لا تحتوي على run_polling()
            # فإنها ستنتهي فوراً
            
            print()  # سطر فارغ قبل بدء البوت
            
            # استدعاء run_bot
            run_bot()
            
            # ⚠️ إذا وصلنا هنا، معناه run_bot() انتهت!
            logger.warning("⚠️ run_bot() انتهت بدلاً من الاستمرار")
            logger.warning("💡 تأكد من أن run_bot() تحتوي على application.run_polling()")
            
        except ImportError as e:
            logger.error(f"❌ فشل استيراد run_bot: {e}")
            
            # محاولة main
            try:
                logger.info("🔄 محاولة استيراد main...")
                from telegram_bot import main as bot_main
                
                logger.info("✅ تم استيراد telegram_bot.main()")
                logger.info("=" * 70)
                logger.info("🚀 البوت يعمل الآن - افتح Telegram")
                logger.info("⏹️ اضغط Ctrl+C للإيقاف")
                logger.info("=" * 70)
                
                print()
                bot_main()
                
                # إذا وصلنا هنا
                logger.warning("⚠️ main() انتهت بدلاً من الاستمرار")
                
            except ImportError as e2:
                logger.error(f"❌ فشل استيراد main: {e2}")
                logger.error("💡 تأكد من وجود run_bot() أو main() في telegram_bot.py")
                
                print("\n" + "="*70)
                print("🔧 خيارات الإصلاح:")
                print("="*70)
                print("\n1. شغّل التشخيص:")
                print("   python check_telegram_bot.py")
                print("\n2. أو شغّل مباشرة:")
                print("   python telegram_bot.py")
                print("\n3. أو استخدم الـ debugger:")
                print("   python debug_run.py")
                
                input("\nاضغط Enter للخروج...")
                sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
        
    except Exception as e:
        logger.critical(f"❌ خطأ غير متوقع: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        
        print("\n" + "="*70)
        print("🐛 معلومات التشخيص:")
        print("="*70)
        traceback.print_exc()
        
        input("\nاضغط Enter للخروج...")
        sys.exit(1)


if __name__ == "__main__":
    main()