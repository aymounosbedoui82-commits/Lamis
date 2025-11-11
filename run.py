#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lamis Bot - نقطة البداية الرئيسية
المرحلة 1: التحسينات الأساسية مطبقة ✅
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


def install_missing_libraries(packages):
    """تثبيت المكتبات المفقودة"""
    for package in packages:
        try:
            logger.info(f"📦 تثبيت {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✅ تم تثبيت {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ فشل تثبيت {package}: {e}")


def check_libraries():
    """فحص المكتبات المطلوبة"""
    logger.info("🔍 فحص المكتبات...")
    
    # المكتبات الأساسية (إجبارية)
    essential = {
        'telegram': 'python-telegram-bot',
    }
    
    # المكتبات الاختيارية (للميزات المتقدمة)
    optional = {
        'torch': 'torch',
        'transformers': 'transformers',
        'numpy': 'numpy'
    }
    
    # فحص الأساسية
    missing_essential = []
    for module, package in essential.items():
        try:
            __import__(module)
            logger.info(f"✅ {module} متوفر")
        except ImportError:
            logger.warning(f"❌ {module} غير مثبت")
            missing_essential.append(package)
    
    if missing_essential:
        logger.error(f"⚠️ المكتبات الأساسية المفقودة: {', '.join(missing_essential)}")
        response = input("هل تريد تثبيتها الآن؟ (y/n): ")
        if response.lower() == 'y':
            install_missing_libraries(missing_essential)
        else:
            logger.error("❌ لا يمكن تشغيل البوت بدون المكتبات الأساسية")
            sys.exit(1)
    
    # فحص الاختيارية (مع تجاهل الأخطاء)
    missing_optional = []
    for module, package in optional.items():
        try:
            __import__(module)
            logger.info(f"✅ {module} متوفر")
        except Exception as e:
            logger.warning(f"⚠️ {module} غير متوفر (اختياري)")
            logger.debug(f"   السبب: {str(e)[:100]}")
            missing_optional.append(package)
    
    if missing_optional:
        logger.info(f"ℹ️ المكتبات الاختيارية المفقودة: {', '.join(missing_optional)}")
        logger.info("ℹ️ البوت سيعمل بدونها، لكن بميزات محدودة")
        print("\nخيارات:")
        print("  y - تثبيت المكتبات الاختيارية")
        print("  n - تخطي (البوت سيعمل بدونها)")
        response = input("اختيارك (y/n): ")
        if response.lower() == 'y':
            install_missing_libraries(missing_optional)
        else:
            logger.info("⏭️ تخطي المكتبات الاختيارية...")


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
        
        # 2. فحص المكتبات
        check_libraries()
        
        # 3. فحص الإعدادات
        if not check_config():
            logger.error("❌ يرجى إكمال الإعدادات أولاً")
            input("\nاضغط Enter للخروج...")
            sys.exit(1)
        
        # 4. تشغيل البوت
        logger.info("🚀 تشغيل البوت...")
        
        # محاولة استيراد البوت بطرق مختلفة
        try:
            # الطريقة 1: استيراد run_bot
            from telegram_bot import run_bot
            logger.info("✅ البوت يعمل الآن...")
            logger.info("📱 افتح Telegram وابحث عن بوتك للبدء")
            run_bot()
        except ImportError:
            # الطريقة 2: استيراد main
            try:
                from telegram_bot import main as bot_main
                logger.info("✅ البوت يعمل الآن...")
                logger.info("📱 افتح Telegram وابحث عن بوتك للبدء")
                bot_main()
            except ImportError:
                # الطريقة 3: تشغيل كسكريبت
                logger.info("✅ البوت يعمل الآن...")
                logger.info("📱 افتح Telegram وابحث عن بوتك للبدء")
                import telegram_bot
                # إذا كان telegram_bot يعمل مباشرة عند الاستيراد
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.critical(f"❌ خطأ غير متوقع: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        input("\nاضغط Enter للخروج...")
        sys.exit(1)


if __name__ == "__main__":
    main()