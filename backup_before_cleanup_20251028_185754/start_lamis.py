#!/usr/bin/env python3
# start_lamis.py
"""
سكريبت تشغيل البوت Lamis بدون simple_reminders
يستخدم job_queue المدمج في telegram_bot.py
"""

import os
import sys

def main():
    print("="*60)
    print("🤖 Lamis - المساعد الذكي")
    print("="*60)
    
    # التحقق من Token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        try:
            from config import Config
            token = Config.TELEGRAM_BOT_TOKEN
        except:
            print("❌ لم يتم العثور على config.py")
            sys.exit(1)
    
    if token == "YOUR_TOKEN_HERE" or not token:
        print("\n❌ خطأ: Token البوت غير معرّف!")
        print("\n📝 الحل:")
        print("1. افتح ملف config.py")
        print("2. استبدل YOUR_TOKEN_HERE بـ token البوت من @BotFather")
        print("3. أو اضبط متغير البيئة: TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    
    print(f"\n✅ Token: {token[:10]}...")
    
    # استيراد وتشغيل البوت
    try:
        from telegram_bot import TelegramBot
        
        print("🔧 تهيئة البوت...")
        bot = TelegramBot(token)
        
        print("\n" + "="*60)
        print("🚀 تشغيل...")
        print("="*60 + "\n")
        
        bot.run()
        
    except ImportError as e:
        print(f"\n❌ خطأ في الاستيراد: {e}")
        print("\n📋 تأكد من وجود الملفات:")
        print("  • telegram_bot.py")
        print("  • intelligent_agent.py")
        print("  • config.py")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البوت")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()