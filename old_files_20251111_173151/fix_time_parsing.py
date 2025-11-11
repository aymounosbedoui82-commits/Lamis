#!/usr/bin/env python3
# fix_time_parsing.py
"""
🔧 إصلاح فهم الوقت بدون ":"
مثال: "الساعة 16" → 16:00
"""

import os
import shutil
from datetime import datetime

def fix_time_parsing():
    """تحسين فهم الوقت في intelligent_agent.py"""
    
    print("="*70)
    print("🔧 تحسين فهم الوقت")
    print("="*70)
    
    if not os.path.exists('intelligent_agent.py'):
        print("\n❌ intelligent_agent.py غير موجود!")
        return False
    
    # نسخة احتياطية
    backup = f"intelligent_agent.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('intelligent_agent.py', backup)
    print(f"\n✅ نسخة احتياطية: {backup}")
    
    # قراءة الملف
    with open('intelligent_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة _extract_time
    old_pattern = '''        # نمط "الساعة X" أو "X صباحاً" أو "X مساءً"
        hour_pattern = re.search(r'(\\d{1,2})\\s*(صباحا|صباحاً|مساء|مساءً|am|pm)', text.lower())'''
    
    new_pattern = '''        # نمط "الساعة X" أو "X صباحاً" أو "X مساءً"
        # ✅ محسّن: يقبل "على الساعة 16" بدون am/pm
        hour_pattern = re.search(r'(?:الساعة|على الساعة|ساعة)?\\s*(\\d{1,2})\\s*(صباحا|صباحاً|مساء|مساءً|am|pm)?', text.lower())'''
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # أيضاً تحديث معالجة period
        old_period_handling = '''            if period:
                if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                    hour += 12
                elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                    hour = 0
                elif period == 'pm' and hour == 12:
                    hour = 12'''
        
        new_period_handling = '''            # ✅ معالجة محسّنة للوقت
            if period:
                if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                    hour += 12
                elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                    hour = 0
                elif period == 'pm' and hour == 12:
                    hour = 12
            else:
                # إذا لم يكن هناك period والساعة بين 1-11، نفترض أنه مساءً
                # (في الغالب المواعيد تكون بعد الظهر)
                if 1 <= hour <= 11:
                    # إذا كان الوقت الحالي صباحاً والساعة صغيرة، نفترض مساءً
                    from datetime import datetime
                    current_hour = datetime.now().hour
                    if current_hour >= 12 or hour < 8:
                        hour += 12'''
        
        content = content.replace(old_period_handling, new_period_handling)
        
        # حفظ
        with open('intelligent_agent.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ تم تحسين فهم الوقت!")
        print("\n💡 الآن يفهم:")
        print("  • 'على الساعة 16' → 16:00 ✓")
        print("  • 'الساعة 3' → 15:00 (يفترض مساءً)")
        print("  • 'الساعة 3 مساءً' → 15:00")
        print("  • 'الساعة 16:00' → 16:00")
        
        return True
    else:
        print("\n⚠️ لم يتم العثور على النمط المطلوب")
        print("💡 قد يكون تم تحديثه بالفعل")
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              🔧 تحسين فهم الوقت                                  ║
╚══════════════════════════════════════════════════════════════════╝

المشكلة:
  "موعد على الساعة 16" → يضيفه 09:00 ❌

الحل:
  تحسين regex لفهم الأرقام بدون ":"
  
    """)
    
    try:
        success = fix_time_parsing()
        
        if success:
            print("\n" + "="*70)
            print("🎉 تم التحسين!")
            print("="*70)
            print("\n🔄 أعد تشغيل البوت:")
            print("  Ctrl+C لإيقاف البوت الحالي")
            print("  python run.py")
        else:
            print("\n⚠️ لم يتم التحسين - راجع يدوياً")
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()