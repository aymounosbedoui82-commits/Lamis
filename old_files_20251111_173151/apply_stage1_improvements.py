#!/usr/bin/env python3
# apply_stage1_improvements.py
"""
سكريبت تطبيق تحسينات المرحلة 1 (الأساسيات) ⭐⭐⭐
✅ حماية Token
✅ Rate Limiting
✅ Error Handling محسّن
✅ Structured Logging
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


class Stage1Improver:
    """مطبق تحسينات المرحلة الأولى"""
    
    def __init__(self):
        self.backup_dir = None
        self.improvements_applied = []
        self.errors = []
    
    def create_backup(self):
        """إنشاء نسخة احتياطية من المشروع"""
        print("\n" + "="*70)
        print("📦 إنشاء نسخة احتياطية...")
        print("="*70)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f'backup_before_stage1_{timestamp}'
        
        try:
            Path(self.backup_dir).mkdir(exist_ok=True)
            
            # نسخ الملفات المهمة
            important_files = [
                'config.py',
                'intelligent_agent.py',
                'telegram_bot.py',
                'run.py',
                'agent_data.db',
                '.env'
            ]
            
            copied = 0
            for file in important_files:
                if os.path.exists(file):
                    shutil.copy2(file, self.backup_dir)
                    copied += 1
            
            print(f"✅ تم نسخ {copied} ملف إلى: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def check_env_file(self):
        """فحص وإنشاء ملف .env"""
        print("\n" + "="*70)
        print("🔒 التحسين 1/4: حماية Token")
        print("="*70)
        
        if not os.path.exists('.env'):
            print("⚠️ ملف .env غير موجود")
            
            token = input("\n👉 أدخل TELEGRAM_BOT_TOKEN من @BotFather: ").strip()
            
            if token:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
                    f.write(f"LOG_LEVEL=INFO\n")
                
                print("✅ تم إنشاء ملف .env")
                self.improvements_applied.append("✅ حماية Token")
                return True
            else:
                print("❌ Token غير صالح")
                self.errors.append("❌ لم يتم تعيين Token")
                return False
        else:
            print("✅ ملف .env موجود")
            self.improvements_applied.append("✅ حماية Token")
            return True
    
    def install_new_files(self):
        """تثبيت الملفات المحسّنة الجديدة"""
        print("\n" + "="*70)
        print("📦 تثبيت الملفات المحسّنة...")
        print("="*70)
        
        new_files = {
            'config_improved.py': 'config.py',
            'rate_limiter.py': 'rate_limiter.py',
            'error_handler.py': 'error_handler.py',
            'structured_logger.py': 'structured_logger.py'
        }
        
        for source, dest in new_files.items():
            if os.path.exists(source):
                # نسخة احتياطية للملف القديم
                if os.path.exists(dest) and dest != source:
                    backup_name = f"{dest}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(dest, backup_name)
                    print(f"   📦 نسخة احتياطية: {backup_name}")
                
                # نسخ الملف الجديد
                if source != dest:
                    shutil.copy2(source, dest)
                print(f"   ✅ {dest}")
            else:
                print(f"   ⚠️ {source} غير موجود")
        
        print("\n✅ تم تثبيت الملفات المحسّنة")
        self.improvements_applied.append("✅ Rate Limiting")
        self.improvements_applied.append("✅ Error Handling")
        self.improvements_applied.append("✅ Structured Logging")
    
    def update_telegram_bot(self):
        """تحديث telegram_bot.py لاستخدام التحسينات"""
        print("\n" + "="*70)
        print("🔨 تحديث telegram_bot.py...")
        print("="*70)
        
        if not os.path.exists('telegram_bot.py'):
            print("❌ telegram_bot.py غير موجود")
            return False
        
        try:
            with open('telegram_bot.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص إذا كانت التحسينات مطبقة بالفعل
            if 'rate_limiter' in content and 'error_handler' in content:
                print("✅ التحسينات مطبقة بالفعل")
                return True
            
            # إضافة الاستيرادات في بداية الملف
            new_imports = """
# ==========================================
# المرحلة 1: التحسينات الأساسية ✅
# ==========================================
from rate_limiter import rate_limit, RateLimiter
from error_handler import ErrorHandler, global_error_handler, BotError, ErrorType
from structured_logger import app_logger, metrics
from config import Config  # استخدام Config المحسّن

# Rate Limiter عام
bot_rate_limiter = RateLimiter(max_requests=30, time_window=60)
"""
            
            # إضافة الاستيرادات بعد الاستيرادات الموجودة
            import_position = content.find('from intelligent_agent import')
            if import_position != -1:
                content = content[:import_position] + new_imports + content[import_position:]
            
            # حفظ الملف المحدّث
            with open('telegram_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ تم تحديث telegram_bot.py")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحديث telegram_bot.py: {e}")
            self.errors.append(f"❌ فشل تحديث telegram_bot.py: {e}")
            return False
    
    def create_updated_run_script(self):
        """إنشاء run.py محدّث"""
        print("\n" + "="*70)
        print("🔨 تحديث run.py...")
        print("="*70)
        
        updated_run = '''#!/usr/bin/env python3
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
        print("\\n\\n👋 تم إيقاف البرنامج")
    except Exception as e:
        app_logger.critical(f"❌ خطأ غير متوقع: {e}")
'''
        
        try:
            # نسخة احتياطية من run.py القديم
            if os.path.exists('run.py'):
                backup_name = f"run.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2('run.py', backup_name)
                print(f"   📦 نسخة احتياطية: {backup_name}")
            
            # كتابة الملف الجديد
            with open('run.py', 'w', encoding='utf-8') as f:
                f.write(updated_run)
            
            print("✅ تم تحديث run.py")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحديث run.py: {e}")
            return False
    
    def show_summary(self):
        """عرض ملخص التحسينات"""
        print("\n" + "="*70)
        print("✨ ملخص تحسينات المرحلة 1 (الأساسيات)")
        print("="*70)
        
        print("\n📋 التحسينات المطبقة:")
        for improvement in self.improvements_applied:
            print(f"  {improvement}")
        
        if self.errors:
            print("\n⚠️ الأخطاء:")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n💾 النسخة الاحتياطية: {self.backup_dir}")
        
        print("\n📚 الملفات الجديدة:")
        print("  • config.py (محسّن)")
        print("  • rate_limiter.py (جديد)")
        print("  • error_handler.py (جديد)")
        print("  • structured_logger.py (جديد)")
        print("  • .env (Token محمي)")
        
        print("\n🎯 الخطوات التالية:")
        print("  1. راجع ملف .env وتأكد من صحة Token")
        print("  2. شغّل البوت: python run.py")
        print("  3. اختبر الميزات الجديدة:")
        print("     • Rate Limiting (جرّب إرسال 30+ رسالة/دقيقة)")
        print("     • Error Messages (جرّب إدخالات خاطئة)")
        print("     • Logging (راجع مجلد logs/)")
        
        print("\n🎉 المرحلة 1 اكتملت بنجاح!")
        print("📖 للمرحلة 2، راجع تقرير التحسينات")
        print("="*70)
    
    def run(self):
        """تشغيل التحسينات"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║     🚀 تطبيق تحسينات المرحلة 1 (الأساسيات) ⭐⭐⭐              ║
╚══════════════════════════════════════════════════════════════════╝

التحسينات المطلوبة:
  1. 🔒 حماية Token (dotenv)
  2. ⚡ Rate Limiting (30 طلب/دقيقة)
  3. 🛡️ Error Handling محسّن
  4. 📊 Structured Logging

⚠️ سيتم إنشاء نسخة احتياطية تلقائياً
""")
        
        confirm = input("هل تريد المتابعة؟ (y/n): ").lower()
        if confirm != 'y':
            print("❌ تم الإلغاء")
            return
        
        # التنفيذ
        success = True
        
        if not self.create_backup():
            print("⚠️ فشل إنشاء النسخة الاحتياطية. هل تريد المتابعة؟ (y/n): ")
            if input().lower() != 'y':
                return
        
        if not self.check_env_file():
            success = False
        
        self.install_new_files()
        self.update_telegram_bot()
        self.create_updated_run_script()
        
        # الملخص
        self.show_summary()
        
        if success:
            print("\n✅ التحسينات طُبّقت بنجاح!")
        else:
            print("\n⚠️ التحسينات طُبّقت مع بعض الأخطاء")


if __name__ == "__main__":
    improver = Stage1Improver()
    try:
        improver.run()
    except KeyboardInterrupt:
        print("\n\n❌ تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()