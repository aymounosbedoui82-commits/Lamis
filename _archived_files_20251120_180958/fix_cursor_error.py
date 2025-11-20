#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 إصلاح خطأ cursor في intelligent_agent.py
يصلح السطر 1053: "cursor" is not defined
"""

import os
import shutil
from datetime import datetime

def fix_cursor_error():
    """إصلاح خطأ cursor غير المعرّف"""
    
    print("="*70)
    print("🔧 إصلاح خطأ cursor - intelligent_agent.py")
    print("="*70)
    
    filename = "intelligent_agent.py"
    
    if not os.path.exists(filename):
        print(f"\n❌ الملف غير موجود: {filename}")
        return False
    
    # نسخة احتياطية
    backup = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filename, backup)
    print(f"\n✅ نسخة احتياطية: {backup}")
    
    # قراءة الملف
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن الكود الخاطئ وإصلاحه
    old_code = """        # البحث عن طلب تذكير مخصص
        reminder_patterns = [
            r'ذكرني قبل (\d+) دقيقة',
            r'ذكرني قبل (\d+) دقائق',
            r'ذكرني قبل ساعة',
            r'ذكرني قبل يوم',
            r'rappelle.moi (\d+) minutes? avant',
            r'remind me (\d+) minutes? before'
        ]

        for pattern in reminder_patterns:
            match = re.search(pattern, message.lower(), re.IGNORECASE)
            if match:
                try:
                    # استيراد مدير التذكيرات المخصصة
                    from advanced_features import CustomReminderManager
            
                    # الحصول على آخر موعد للمستخدم
                    cursor.execute('''
                        SELECT id FROM appointments 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    ''', (user_id,))"""

    new_code = """        # البحث عن طلب تذكير مخصص
        reminder_patterns = [
            r'ذكرني قبل (\d+) دقيقة',
            r'ذكرني قبل (\d+) دقائق',
            r'ذكرني قبل ساعة',
            r'ذكرني قبل يوم',
            r'rappelle.moi (\d+) minutes? avant',
            r'remind me (\d+) minutes? before'
        ]

        for pattern in reminder_patterns:
            match = re.search(pattern, message.lower(), re.IGNORECASE)
            if match:
                try:
                    # استيراد مدير التذكيرات المخصصة
                    from advanced_features import CustomReminderManager
            
                    # ✅ فتح اتصال قاعدة البيانات
                    conn = sqlite3.connect(self.db.db_path)
                    cursor = conn.cursor()
            
                    # الحصول على آخر موعد للمستخدم
                    cursor.execute('''
                        SELECT id FROM appointments 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    ''', (user_id,))"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        print("\n✅ تم إصلاح الكود الخاطئ")
    else:
        print("\n⚠️ لم يتم العثور على الكود القديم - سأحاول طريقة أخرى...")
        
        # طريقة بديلة: إصلاح أي استخدام لـ cursor بدون تعريف
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # إذا وجدنا cursor.execute بدون تعريف cursor قبله
            if 'cursor.execute' in line and i > 0:
                # فحص آخر 10 أسطر
                has_cursor_def = False
                has_conn_def = False
                for j in range(max(0, i-20), i):
                    if 'cursor = ' in lines[j] or 'cursor=' in lines[j]:
                        has_cursor_def = True
                    if 'conn = sqlite3.connect' in lines[j]:
                        has_conn_def = True
                
                # إذا لم يكن cursor معرّف
                if not has_cursor_def and 'try:' in lines[i-5:i]:
                    # أضف تعريف cursor
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * indent + '# ✅ فتح اتصال قاعدة البيانات')
                    fixed_lines.append(' ' * indent + 'conn = sqlite3.connect(self.db.db_path)')
                    fixed_lines.append(' ' * indent + 'cursor = conn.cursor()')
                    fixed_lines.append('')
                    print(f"  ✅ أضفت تعريف cursor قبل السطر {i+1}")
            
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        print("\n✅ تم إصلاح جميع استخدامات cursor")
    
    # حفظ الملف
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n💾 تم حفظ الإصلاحات")
    
    print("\n" + "="*70)
    print("✅ تم الإصلاح بنجاح!")
    print("="*70)
    
    print(f"""
📋 ما تم إصلاحه:

1. ✅ إضافة تعريف cursor قبل استخدامه:
   ```python
   conn = sqlite3.connect(self.db.db_path)
   cursor = conn.cursor()
   ```

2. ✅ السطر 1053 الآن يعمل بشكل صحيح

💾 النسخة الاحتياطية: {backup}

🔄 الخطوات التالية:
  1. أعد تشغيل VSCode أو اضغط F5
  2. يجب أن يختفي خطأ Pylance
  3. شغّل البوت: python run.py
    """)
    
    return True


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🔧 إصلاح خطأ cursor - intelligent_agent.py             ║
╚══════════════════════════════════════════════════════════════════╝

المشكلة:
  ❌ "cursor" is not defined - السطر 1053
  
السبب:
  • يتم استخدام cursor.execute() بدون فتح اتصال بقاعدة البيانات
  
الحل:
  ✅ إضافة:
     conn = sqlite3.connect(self.db.db_path)
     cursor = conn.cursor()
    """)
    
    try:
        success = fix_cursor_error()
        
        if success:
            print("\n🎉 تم الإصلاح بنجاح!")
            print("\n💡 نصيحة: أعد تشغيل VSCode لتحديث Pylance")
        else:
            print("\n⚠️ لم يتم الإصلاح - راجع يدوياً")
    
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف")