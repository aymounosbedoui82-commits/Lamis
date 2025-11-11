#!/usr/bin/env python3
# check_telegram_bot.py
"""
🔍 فحص telegram_bot.py لاكتشاف المشكلة
"""

import os
import re

def check_telegram_bot():
    """فحص شامل لـ telegram_bot.py"""
    
    print("="*70)
    print("🔍 فحص telegram_bot.py")
    print("="*70)
    
    if not os.path.exists('telegram_bot.py'):
        print("\n❌ telegram_bot.py غير موجود!")
        print("\n💡 الحل:")
        print("   1. تأكد من أنك في المجلد الصحيح")
        print("   2. أو أخبرني لأنشئ telegram_bot.py جديد")
        return False
    
    print("\n✅ telegram_bot.py موجود")
    
    # قراءة المحتوى
    with open('telegram_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"📊 عدد الأسطر: {len(lines):,}")
    
    # فحص الدوال المهمة
    print("\n🔍 فحص الدوال الأساسية:")
    
    checks = {
        'def run_bot': 'دالة run_bot()',
        'def main': 'دالة main()',
        'Application.builder()': 'بناء Application',
        '.run_polling()': 'بدء Polling',
        'async def start': 'معالج /start',
        'async def help': 'معالج /help',
    }
    
    found = {}
    for pattern, name in checks.items():
        if pattern in content:
            # إيجاد رقم السطر
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    print(f"  ✅ {name:30s} (السطر {i})")
                    found[pattern] = i
                    break
        else:
            print(f"  ❌ {name:30s} (غير موجود)")
            found[pattern] = None
    
    # فحص نقطة الدخول
    print("\n🚪 فحص نقطة الدخول:")
    
    if 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content:
        print("  ✅ if __name__ == '__main__' موجود")
        
        # ماذا يحدث في main؟
        main_block_start = None
        for i, line in enumerate(lines):
            if '__name__' in line and '__main__' in line:
                main_block_start = i
                break
        
        if main_block_start:
            print("\n  📋 محتوى main block:")
            for i in range(main_block_start, min(main_block_start + 10, len(lines))):
                line = lines[i].strip()
                if line:
                    print(f"     {i+1}: {line[:60]}")
    else:
        print("  ⚠️ if __name__ == '__main__' غير موجود")
    
    # فحص run_bot بالتفصيل
    if found.get('def run_bot'):
        print("\n🔍 فحص دالة run_bot():")
        
        run_bot_start = found['def run_bot']
        
        # عرض محتوى الدالة
        print("\n  📋 محتوى run_bot():")
        in_function = False
        indent_level = 0
        
        for i in range(run_bot_start - 1, min(run_bot_start + 30, len(lines))):
            line = lines[i]
            
            if 'def run_bot' in line:
                in_function = True
                indent_level = len(line) - len(line.lstrip())
                print(f"     {i+1}: {line.strip()[:70]}")
                continue
            
            if in_function:
                current_indent = len(line) - len(line.lstrip())
                
                # إذا عدنا لنفس مستوى indent أو أقل، انتهت الدالة
                if line.strip() and current_indent <= indent_level:
                    break
                
                if line.strip():
                    print(f"     {i+1}: {line.strip()[:70]}")
    
    # البحث عن مشاكل شائعة
    print("\n⚠️ فحص المشاكل الشائعة:")
    
    problems = []
    
    if found.get('.run_polling()') is None:
        problems.append("❌ لا يوجد استدعاء لـ .run_polling()")
    
    if found.get('Application.builder()') is None:
        problems.append("❌ لا يوجد Application.builder()")
    
    if found.get('def run_bot') is None and found.get('def main') is None:
        problems.append("❌ لا توجد دالة run_bot() أو main()")
    
    if problems:
        for p in problems:
            print(f"  {p}")
    else:
        print("  ✅ لا توجد مشاكل واضحة")
    
    # التوصيات
    print("\n" + "="*70)
    print("💡 التوصيات:")
    print("="*70)
    
    if found.get('def run_bot') and found.get('.run_polling()'):
        print("\n✅ telegram_bot.py يبدو صحيحاً")
        print("\n🔍 المشكلة قد تكون في:")
        print("  1. run.py لا يستدعي run_bot() بشكل صحيح")
        print("  2. استثناء يحدث بصمت")
        print("\n💡 جرب:")
        print("  python telegram_bot.py  (تشغيل مباشر)")
    else:
        print("\n⚠️ telegram_bot.py يحتاج لإصلاح")
        print("\n💡 الحل:")
        print("  أرسل ملف telegram_bot.py للمراجعة")
        print("  أو دعني أنشئ نسخة جديدة")
    
    return True

if __name__ == "__main__":
    try:
        check_telegram_bot()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()