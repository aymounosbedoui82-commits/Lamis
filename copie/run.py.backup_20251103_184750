#!/usr/bin/env python3
# run.py - Enhanced Version ✅
"""
سكريبت التشغيل الشامل للمساعد الذكي - نسخة محسّنة
✅ المرحلة 1: التحسينات الأساسية مطبقة
"""

import sys
import os

# ==========================================
# المرحلة 1: استخدام المكونات المحسّنة ✅
# ==========================================
from config import Config
from structured_logger import app_logger, metrics
from error_handler import ErrorHandler

def check_python_version():
    """التحقق من إصدار Python"""
    app_logger.info("🔍 فحص إصدار Python...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        app_logger.error(f"❌ يتطلب Python 3.8+. الحالي: {version.major}.{version.minor}")
        return False
    
    app_logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """التحقق من المكتبات المطلوبة"""
    app_logger.info("🔍 فحص المكتبات...")
    
    required = {
        'torch': 'torch',
        'transformers': 'transformers',
        'telegram': 'python-telegram-bot',
        'numpy': 'numpy',
        'dotenv': 'python-dotenv'  # جديد ✅
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            app_logger.debug(f"✅ {package}")
        except ImportError:
            app_logger.warning(f"❌ {package} غير مثبت")
            missing.append(package)
    
    if missing:
        app_logger.error(f"⚠️ المكتبات المفقودة: {', '.join(missing)}")
        install = input("هل تريد تثبيتها الآن؟ (y/n): ").lower()
        if install == 'y':
            import subprocess
            for package in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            return True
        return False
    
    return True

def run_bot():
    """تشغيل البوت"""
    app_logger.info("🚀 تشغيل البوت...")
    
    try:
        # استخدام Token من Config المحسّن
        token = Config.TELEGRAM_BOT_TOKEN
        
        from telegram_bot import TelegramBot
        
        bot = TelegramBot(token)
        app_logger.info("✅ البوت يعمل الآن...")
        app_logger.info("📱 افتح Telegram وابحث عن بوتك للبدء")
        
        bot.run()
        
    except ValueError as e:
        app_logger.error(f"❌ خطأ في Token: {e}")
    except KeyboardInterrupt:
        app_logger.info("👋 تم إيقاف البوت")
        metrics.print_metrics()
    except Exception as e:
        app_logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        ErrorHandler.log_error(
            error_type="bot_start_error",
            message=str(e)
        )

def main():
    """البرنامج الرئيسي"""
    print("="*70)
    print("🤖 مرحباً بك في Lamis Bot - المساعد الذكي")
    print("✨ المرحلة 1: التحسينات الأساسية مطبقة")
    print("="*70)
    
    # فحص المتطلبات
    if not check_python_version():
        return
    
    if not check_dependencies():
        app_logger.error("⚠️ يرجى تثبيت المكتبات المطلوبة أولاً")
        return
    
    # التحقق من الإعدادات
    if not Config.validate_config():
        app_logger.error("⚠️ يرجى تكوين البوت أولاً")
        return
    
    # تشغيل البوت
    run_bot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البرنامج")
    except Exception as e:
        app_logger.critical(f"❌ خطأ غير متوقع: {e}")
