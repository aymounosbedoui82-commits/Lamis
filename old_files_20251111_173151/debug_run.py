#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐛 تشغيل مع Debugging مفصل - يكشف المشكلة بالضبط
"""

import sys
import os

print("="*70)
print("🐛 تشغيل مع Debugging - Lamis Bot")
print("="*70)

# تفعيل طباعة التفاصيل
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

print("\n📍 الخطوة 1: فحص الملفات")
print("-"*70)

if not os.path.exists('telegram_bot.py'):
    print("❌ telegram_bot.py غير موجود!")
    sys.exit(1)

print("✅ telegram_bot.py موجود")

if not os.path.exists('.env'):
    print("❌ .env غير موجود!")
    sys.exit(1)

print("✅ .env موجود")

print("\n📍 الخطوة 2: استيراد telegram_bot")
print("-"*70)

try:
    print("🔄 جاري الاستيراد...")
    import telegram_bot
    print("✅ تم استيراد telegram_bot")
except Exception as e:
    print(f"❌ فشل الاستيراد: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n📍 الخطوة 3: البحث عن دالة التشغيل")
print("-"*70)

# البحث عن دالة التشغيل
run_function = None

if hasattr(telegram_bot, 'run_bot'):
    run_function = telegram_bot.run_bot
    print("✅ وجدت run_bot()")
elif hasattr(telegram_bot, 'main'):
    run_function = telegram_bot.main
    print("✅ وجدت main()")
else:
    print("❌ لم أجد run_bot() أو main()")
    print("\n🔍 الدوال المتاحة:")
    for attr in dir(telegram_bot):
        if not attr.startswith('_'):
            print(f"  • {attr}")
    sys.exit(1)

print("\n📍 الخطوة 4: تشغيل البوت")
print("-"*70)

print("🚀 جاري بدء البوت...")
print("⏹️ اضغط Ctrl+C للإيقاف")
print("="*70 + "\n")

try:
    # تشغيل مع طباعة ما يحدث
    print(">>> استدعاء run_function()...")
    run_function()
    
    # إذا وصلنا هنا، معناه الدالة انتهت!
    print("\n⚠️⚠️⚠️ المشكلة: الدالة انتهت بدلاً من الاستمرار! ⚠️⚠️⚠️")
    print("\n💡 هذا يعني أن run_bot() أو main() لا تستدعي run_polling()")
    print("   أو تستدعيها بشكل خاطئ")

except KeyboardInterrupt:
    print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    
except Exception as e:
    print(f"\n❌ خطأ أثناء التشغيل: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 السبب المحتمل:")
    if 'TELEGRAM_BOT_TOKEN' in str(e):
        print("  • مشكلة في Token")
    elif 'Event loop' in str(e):
        print("  • مشكلة في Event Loop")
    elif 'Connection' in str(e):
        print("  • مشكلة في الاتصال بالإنترنت")
    else:
        print("  • خطأ غير متوقع")

print("\n" + "="*70)
print("📋 ملخص")
print("="*70)
print("\n💡 الخطوات التالية:")
print("  1. شغّل: python check_telegram_bot.py")
print("  2. راجع محتوى run_bot() في telegram_bot.py")
print("  3. تأكد من وجود application.run_polling() في الدالة")