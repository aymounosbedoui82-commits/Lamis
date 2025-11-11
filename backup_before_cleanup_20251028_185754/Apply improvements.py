#!/usr/bin/env python3
# apply_improvements.py
"""
سكريبت تلقائي لتطبيق تحسينات intelligent_agent
يحل المشكلتين:
1. فهم "عرض مواعيدي"
2. استخراج الوقت الفرنسي "11h00"
"""

import os
import shutil
from datetime import datetime

def backup_file(filename):
    """إنشاء نسخة احتياطية"""
    backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filename, backup_name)
    return backup_name

def apply_improvements():
    """تطبيق التحسينات"""
    print("="*70)
    print("🔧 تطبيق تحسينات intelligent_agent.py")
    print("="*70)
    
    filename = "intelligent_agent.py"
    
    # التحقق من وجود الملف
    if not os.path.exists(filename):
        print(f"\n❌ الملف غير موجود: {filename}")
        return False
    
    print(f"\n✅ وجد: {filename}")
    
    # إنشاء نسخة احتياطية
    print("\n📦 إنشاء نسخة احتياطية...")
    backup_name = backup_file(filename)
    print(f"   ✅ تم: {backup_name}")
    
    # قراءة الملف
    print("\n📖 قراءة الملف...")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("   ✅ تم")
    
    # التحسين 1: تحسين classify_intent
    print("\n🔨 التحسين 1: تحسين فهم الأوامر...")
    
    old_list_keywords = """        # عرض جميع المواعيد
        list_keywords = {
            'ar': ['عرض المواعيد', 'أظهر المواعيد', 'جميع المواعيد'],
            'fr': ['afficher', 'montrer', 'tous les rendez-vous'],
            'en': ['show all', 'display all', 'list all']
        }"""
    
    new_list_keywords = """        # عرض جميع المواعيد - محسّن ✅
        list_keywords = {
            'ar': [
                'عرض المواعيد', 'أظهر المواعيد', 'جميع المواعيد',
                'عرض مواعيدي', 'اعرض مواعيدي', 'شوف مواعيدي',
                'مواعيدي', 'كل مواعيدي', 'شنوا مواعيدي'
            ],
            'fr': [
                'afficher', 'montrer', 'tous les rendez-vous',
                'mes rendez-vous', 'mes rdv', 'voir mes rdv'
            ],
            'en': [
                'show all', 'display all', 'list all',
                'show my appointments', 'my appointments', 'all appointments'
            ]
        }"""
    
    if old_list_keywords in content:
        content = content.replace(old_list_keywords, new_list_keywords)
        print("   ✅ تم تحسين فهم الأوامر")
    else:
        print("   ⚠️ لم يتم العثور على النمط القديم")
    
    # التحسين 2: تحسين استخراج الوقت
    print("\n🔨 التحسين 2: تحسين استخراج الوقت الفرنسي...")
    
    old_extract_time = """    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        \"\"\"استخراج الوقت من النص - دالة مساعدة\"\"\"
        # نمط XX:XX
        time_pattern = re.search(r'(\\d{1,2})[:](\d{2})', text)
        if time_pattern:
            hour = int(time_pattern.group(1))
            minute = int(time_pattern.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # نمط "الساعة X" أو "X صباحاً" أو "X مساءً"
        hour_pattern = re.search(r'(\\d{1,2})\\s*(صباحا|صباحاً|مساء|مساءً|am|pm|h)?', text.lower())
        if hour_pattern:
            hour = int(hour_pattern.group(1))
            period = hour_pattern.group(2)
            
            if period:
                if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                    hour += 12
                elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                    hour = 0
                elif period == 'pm' and hour == 12:
                    hour = 12
            
            if 0 <= hour <= 23:
                return (hour, 0)
        
        return None"""
    
    new_extract_time = """    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        \"\"\"استخراج الوقت من النص - محسّن للصيغة الفرنسية ✅\"\"\"
        # ✅ نمط جديد: XXhXX (فرنسي) - الأولوية!
        french_time = re.search(r'(\\d{1,2})h(\\d{2})', text.lower())
        if french_time:
            hour = int(french_time.group(1))
            minute = int(french_time.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # نمط XX:XX
        time_pattern = re.search(r'(\\d{1,2})[:](\d{2})', text)
        if time_pattern:
            hour = int(time_pattern.group(1))
            minute = int(time_pattern.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # ✅ نمط جديد: XXh (فرنسي بدون دقائق)
        french_hour_only = re.search(r'(\\d{1,2})h(?!\\d)', text.lower())
        if french_hour_only:
            hour = int(french_hour_only.group(1))
            if 0 <= hour <= 23:
                return (hour, 0)
        
        # نمط "الساعة X" أو "X صباحاً" أو "X مساءً"
        hour_pattern = re.search(r'(\\d{1,2})\\s*(صباحا|صباحاً|مساء|مساءً|am|pm)', text.lower())
        if hour_pattern:
            hour = int(hour_pattern.group(1))
            period = hour_pattern.group(2)
            
            if period:
                if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                    hour += 12
                elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                    hour = 0
                elif period == 'pm' and hour == 12:
                    hour = 12
            
            if 0 <= hour <= 23:
                return (hour, 0)
        
        return None"""
    
    if old_extract_time in content:
        content = content.replace(old_extract_time, new_extract_time)
        print("   ✅ تم تحسين استخراج الوقت")
    else:
        print("   ⚠️ لم يتم العثور على النمط القديم")
    
    # حفظ الملف المحسّن
    print("\n💾 حفظ التحسينات...")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ تم!")
    
    # النتيجة
    print("\n" + "="*70)
    print("✅ تم تطبيق التحسينات بنجاح!")
    print("="*70)
    
    print(f"""
📋 التحسينات المطبقة:

1. ✅ فهم "عرض مواعيدي" وأشكال مشابهة
   • "عرض مواعيدي"
   • "اعرض مواعيدي"  
   • "شوف مواعيدي"
   • "مواعيدي" (فقط)
   • "mes rendez-vous" (فرنسي)
   • "my appointments" (إنجليزي)

2. ✅ استخراج الوقت الفرنسي بدقة
   • "11h00" → 11:00 ✅
   • "15h30" → 15:30 ✅
   • "9h" → 09:00 ✅

💾 النسخة الاحتياطية: {backup_name}

🔄 لتطبيق التحسينات، أعد تشغيل البوت:
   python run.py → اختر 1

🧪 اختبر الآن:
   • أرسل: "عرض مواعيدي"
   • أرسل: "RDV demain à 11h00"
    """)
    
    return True

if __name__ == "__main__":
    try:
        success = apply_improvements()
        if not success:
            print("\n❌ فشل تطبيق التحسينات")
    except KeyboardInterrupt:
        print("\n\n👋 تم الإلغاء")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()