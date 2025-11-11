# run.py - Fixed Version ✅
"""
سكريبت التشغيل الشامل للمساعد الذكي
يقوم بفحص المتطلبات وإعداد البيئة وتشغيل البوت
"""

import sys
import os
import subprocess

def check_python_version():
    """التحقق من إصدار Python"""
    print("🔍 فحص إصدار Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ يتطلب Python 3.8 أو أحدث. الإصدار الحالي: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """التحقق من المكتبات المطلوبة"""
    print("\n🔍 فحص المكتبات المطلوبة...")
    
    required = {
        'torch': 'torch',
        'transformers': 'transformers',
        'telegram': 'python-telegram-bot',
        'numpy': 'numpy'
    }
    
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} غير مثبت")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ المكتبات المفقودة: {', '.join(missing)}")
        install = input("هل تريد تثبيتها الآن؟ (y/n): ").lower()
        if install == 'y':
            install_dependencies(missing)
            return True
        return False
    
    return True


def install_dependencies(packages):
    """تثبيت المكتبات المفقودة"""
    print("\n📦 تثبيت المكتبات...")
    for package in packages:
        try:
            print(f"  ⏳ تثبيت {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ تم تثبيت {package}")
        except subprocess.CalledProcessError:
            print(f"  ❌ فشل تثبيت {package}")


def check_database():
    """التحقق من وجود قاعدة البيانات"""
    print("\n🔍 فحص قاعدة البيانات...")
    if os.path.exists("agent_data.db"):
        print("  ✅ قاعدة البيانات موجودة")
        return True
    else:
        print("  ⚠️ قاعدة البيانات غير موجودة")
        create = input("هل تريد إنشاءها الآن؟ (y/n): ").lower()
        if create == 'y':
            try:
                from setup_database import create_database
                create_database()
                return True
            except Exception as e:
                print(f"  ❌ خطأ في إنشاء قاعدة البيانات: {e}")
                return False
        return False


def check_config():
    """التحقق من إعدادات البوت"""
    print("\n🔍 فحص الإعدادات...")
    
    try:
        from config import Config
        
        if Config.TELEGRAM_BOT_TOKEN == "YOUR_TOKEN_HERE":
            print("  ⚠️ لم يتم تعيين Token البوت")
            token = input("أدخل Token البوت من @BotFather: ").strip()
            
            if token:
                # حفظ Token في ملف .env
                with open('.env', 'w') as f:
                    f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
                print("  ✅ تم حفظ Token")
                
                # تحديث المتغير
                os.environ['TELEGRAM_BOT_TOKEN'] = token
                return True
            else:
                print("  ❌ Token غير صالح")
                return False
        else:
            print("  ✅ Token موجود")
            return True
            
    except ImportError:
        print("  ❌ ملف config.py غير موجود")
        return False


def show_menu():
    """عرض قائمة الخيارات"""
    print("\n" + "="*60)
    print("🤖 المساعد الذكي - قائمة التشغيل")
    print("="*60)
    print("\n1. تشغيل البوت 🚀")
    print("2. تدريب النموذج 🧠")
    print("3. إعداد قاعدة البيانات 🗄️")
    print("4. اختبار المكونات 🧪")
    print("5. عرض الإحصائيات 📊")
    print("6. خروج 👋")
    
    return input("\n👉 اختر رقم (1-6): ").strip()


def run_bot():
    """تشغيل البوت"""
    print("\n🚀 تشغيل البوت...")
    try:
        from telegram_bot import TelegramBot
        from config import Config
        
        token = os.getenv('TELEGRAM_BOT_TOKEN', Config.TELEGRAM_BOT_TOKEN)
        
        if token == "YOUR_TOKEN_HERE":
            print("❌ يجب تعيين Token البوت أولاً")
            return
        
        bot = TelegramBot(token)
        print("✅ البوت يعمل الآن...")
        print("📱 افتح Telegram وابحث عن بوتك للبدء")
        print("⏹️ اضغط Ctrl+C للإيقاف\n")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")


def train_model():
    """تدريب النموذج - Fixed Version ✅"""
    print("\n🧠 تدريب النموذج...")
    try:
        from training_module import AdaptiveLearner
        
        # ✅ FIX: تمرير db_path بدلاً من agent object
        db_path = "agent_data.db"
        learner = AdaptiveLearner(db_path=db_path)
        
        epochs = int(input("عدد الـ epochs (افتراضي 10): ") or "10")
        batch_size = int(input("حجم الـ batch (افتراضي 16): ") or "16")
        
        print(f"\n⏳ بدء التدريب ({epochs} epochs)...")
        success = learner.train(epochs=epochs, batch_size=batch_size)
        
        if success:
            save = input("\nهل تريد حفظ النموذج؟ (y/n): ").lower()
            if save == 'y':
                learner.save_model("trained_model.pth")
                print("✅ تم حفظ النموذج")
        
    except Exception as e:
        print(f"❌ خطأ في التدريب: {e}")
        import traceback
        traceback.print_exc()


def setup_database_menu():
    """إعداد قاعدة البيانات"""
    print("\n🗄️ إعداد قاعدة البيانات...")
    try:
        from setup_database import create_database, verify_database, backup_database
        
        print("\n1. إنشاء قاعدة بيانات جديدة")
        print("2. التحقق من قاعدة البيانات")
        print("3. إنشاء نسخة احتياطية")
        
        choice = input("\nاختر (1-3): ").strip()
        
        if choice == '1':
            create_database()
        elif choice == '2':
            verify_database()
        elif choice == '3':
            backup_database()
            
    except Exception as e:
        print(f"❌ خطأ: {e}")


def test_components():
    """اختبار المكونات"""
    print("\n🧪 اختبار المكونات...")
    
    tests = []
    
    # اختبار intelligent_agent
    print("\n  ⏳ اختبار الوكيل الذكي...")
    try:
        from intelligent_agent import IntelligentAgent
        agent = IntelligentAgent()
        
        # اختبار كشف اللغة
        assert agent.detect_language("مرحبا") == "ar"
        assert agent.detect_language("Hello") == "en"
        assert agent.detect_language("Bonjour") == "fr"
        
        print("    ✅ كشف اللغة")
        tests.append(True)
    except Exception as e:
        print(f"    ❌ فشل: {e}")
        tests.append(False)
    
    # اختبار قاعدة البيانات
    print("\n  ⏳ اختبار قاعدة البيانات...")
    try:
        from intelligent_agent import Database
        db = Database()
        
        print("    ✅ قاعدة البيانات")
        tests.append(True)
    except Exception as e:
        print(f"    ❌ فشل: {e}")
        tests.append(False)
    
    # النتيجة النهائية
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 النتيجة: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("✅ جميع المكونات تعمل بشكل صحيح!")
    else:
        print("⚠️ بعض المكونات بها مشاكل")


def show_statistics():
    """عرض الإحصائيات"""
    print("\n📊 عرض الإحصائيات...")
    try:
        import sqlite3
        
        db_path = "agent_data.db"
        
        if not os.path.exists(db_path):
            print("❌ قاعدة البيانات غير موجودة")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إحصائيات المواعيد
        cursor.execute('SELECT COUNT(*) FROM appointments')
        total_appointments = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM reminders')
        total_reminders = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM interactions')
        total_interactions = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("📈 إحصائيات النظام")
        print("="*60)
        print(f"\n📅 المواعيد: {total_appointments}")
        print(f"🔔 التذكيرات: {total_reminders}")
        print(f"💬 التفاعلات: {total_interactions}")
        
        # آخر 5 مواعيد
        cursor.execute('''
            SELECT title, date_time 
            FROM appointments 
            ORDER BY id DESC 
            LIMIT 5
        ''')
        
        recent = cursor.fetchall()
        if recent:
            print("\n📋 آخر المواعيد:")
            for title, date_time in recent:
                print(f"   • {title} - {date_time}")
        
        conn.close()
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ خطأ: {e}")


def main():
    """البرنامج الرئيسي"""
    print("="*60)
    print("🤖 مرحباً بك في المساعد الذكي")
    print("="*60)
    
    # فحص المتطلبات الأساسية
    if not check_python_version():
        return
    
    if not check_dependencies():
        print("\n⚠️ يرجى تثبيت المكتبات المطلوبة أولاً")
        return
    
    if not check_database():
        print("\n⚠️ يرجى إنشاء قاعدة البيانات أولاً")
    
    if not check_config():
        print("\n⚠️ يرجى تكوين البوت أولاً")
    
    # القائمة الرئيسية
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_bot()
        elif choice == '2':
            train_model()
        elif choice == '3':
            setup_database_menu()
        elif choice == '4':
            test_components()
        elif choice == '5':
            show_statistics()
        elif choice == '6':
            print("\n👋 شكراً لاستخدام المساعد الذكي!")
            break
        else:
            print("❌ خيار غير صحيح")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البرنامج")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")