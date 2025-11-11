#!/usr/bin/env python3
# quick_fix_calendar.py
"""
⚡ إصلاح سريع: إضافة أمر /calendar لـ telegram_bot.py
"""

def apply_calendar_fix():
    """إضافة /calendar إلى telegram_bot.py"""
    
    print("="*70)
    print("⚡ إصلاح سريع: إضافة /calendar")
    print("="*70)
    
    import os
    
    if not os.path.exists('telegram_bot.py'):
        print("\n❌ telegram_bot.py غير موجود في المجلد الحالي")
        print("💡 شغّل السكريبت من مجلد المشروع")
        return False
    
    print("\n📖 قراءة telegram_bot.py...")
    with open('telegram_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # فحص إذا كان /calendar موجود بالفعل
    if 'CommandHandler("calendar"' in content or "CommandHandler('calendar'" in content:
        print("\n✅ أمر /calendar موجود بالفعل!")
        return True
    
    # إضافة /calendar كـ alias لـ /week
    print("\n🔧 إضافة /calendar...")
    
    # البحث عن السطر الذي يحتوي على CommandHandler("week"
    old_line = 'self.app.add_handler(CommandHandler("week", self.week_command))'
    
    if old_line in content:
        # إضافة السطر الجديد بعده
        new_line = old_line + '\n        self.app.add_handler(CommandHandler("calendar", self.week_command))  # Alias for /week'
        content = content.replace(old_line, new_line)
        
        # حفظ الملف
        print("💾 حفظ التعديلات...")
        with open('telegram_bot.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ تم إضافة /calendar بنجاح!")
        print("📝 /calendar الآن يعمل مثل /week")
        print("\n🔄 أعد تشغيل البوت لتطبيق التغييرات:")
        print("   python run.py")
        return True
    else:
        print("\n⚠️ لم يتم العثور على السطر المناسب")
        print("💡 سأضيف الكود يدوياً...")
        
        # إضافة في نهاية _setup_handlers
        search_pattern = "self.app.add_handler(CallbackQueryHandler(self.button_callback))"
        if search_pattern in content:
            insert_before = search_pattern
            new_handler = "        self.app.add_handler(CommandHandler(\"calendar\", self.week_command))  # Show calendar\n        "
            content = content.replace(insert_before, new_handler + insert_before)
            
            with open('telegram_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("\n✅ تم الإضافة بنجاح!")
            return True
        else:
            print("\n❌ فشل الإضافة التلقائية")
            print("\n📝 يرجى إضافة هذا السطر يدوياً في _setup_handlers:")
            print('   self.app.add_handler(CommandHandler("calendar", self.week_command))')
            return False


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              ⚡ إصلاح سريع: إضافة /calendar                      ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        apply_calendar_fix()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()