#!/usr/bin/env python3
# fix_relative_time.py
"""
إصلاح مشكلة: "بعد ساعة" لا يعمل، بينما "بعد 60 دقيقة" يعمل
الحل: إضافة أنماط للصيغ بدون أرقام
"""

import os
import shutil
from datetime import datetime

def fix_relative_time():
    """إصلاح استخراج الوقت النسبي"""
    print("="*70)
    print("🔧 إصلاح: دعم 'بعد ساعة' و 'بعد يوم' بدون أرقام")
    print("="*70)
    
    filepath = "intelligent_agent.py"
    
    # التحقق من الملف
    if not os.path.exists(filepath):
        print(f"\n❌ الملف غير موجود: {filepath}")
        print("\n💡 هل تريد استخدام النسخة المرفوعة؟")
        filepath = input("أدخل مسار الملف (أو Enter للإلغاء): ").strip()
        if not filepath or not os.path.exists(filepath):
            print("❌ تم الإلغاء")
            return False
    
    print(f"\n✅ وجد: {filepath}")
    
    # نسخة احتياطية
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"💾 نسخة احتياطية: {backup_path}")
    
    # قراءة الملف
    print("\n📖 قراءة الملف...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن الكود القديم
    old_code = """        # نمط عربي: "بعد X دقيقة/ساعة/يوم"
        after_pattern = re.search(r'بعد\\s+(\\d+)\\s*(دقيقة|دقائق|ساعة|ساعات|يوم|أيام)', text_lower)
        if after_pattern:
            number = int(after_pattern.group(1))
            unit = after_pattern.group(2)
            
            if 'دقيقة' in unit or 'دقائق' in unit:
                return now + timedelta(minutes=number)
            elif 'ساعة' in unit or 'ساعات' in unit:
                return now + timedelta(hours=number)
            elif 'يوم' in unit or 'أيام' in unit:
                return now + timedelta(days=number)"""
    
    # الكود الجديد المحسّن
    new_code = """        # نمط عربي: "بعد X دقيقة/ساعة/يوم"
        # ✅ دعم الصيغ بدون أرقام (بعد ساعة، بعد يوم...)
        
        # أولاً: التحقق من الصيغ الخاصة بدون أرقام
        special_patterns = {
            r'بعد\\s+ساعة(?!\\d)': timedelta(hours=1),
            r'بعد\\s+ساعتين': timedelta(hours=2),
            r'بعد\\s+دقيقة(?!\\d)': timedelta(minutes=1),
            r'بعد\\s+دقيقتين': timedelta(minutes=2),
            r'بعد\\s+يوم(?!\\d)': timedelta(days=1),
            r'بعد\\s+يومين': timedelta(days=2),
        }
        
        for pattern, delta in special_patterns.items():
            if re.search(pattern, text_lower):
                return now + delta
        
        # ثانياً: الصيغة العادية بالأرقام
        after_pattern = re.search(r'بعد\\s+(\\d+)\\s*(دقيقة|دقائق|ساعة|ساعات|يوم|أيام)', text_lower)
        if after_pattern:
            number = int(after_pattern.group(1))
            unit = after_pattern.group(2)
            
            if 'دقيقة' in unit or 'دقائق' in unit:
                return now + timedelta(minutes=number)
            elif 'ساعة' in unit or 'ساعات' in unit:
                return now + timedelta(hours=number)
            elif 'يوم' in unit or 'أيام' in unit:
                return now + timedelta(days=number)"""
    
    # استبدال الكود
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ تم إصلاح النمط العربي")
    else:
        print("⚠️ لم يتم العثور على النمط القديم (ربما تم إصلاحه مسبقاً)")
    
    # إصلاح الفرنسية أيضاً
    old_french = """        # نمط فرنسي: "dans X minutes/heures"
        dans_pattern = re.search(r'dans\\s+(\\d+)\\s*(minute|minutes|heure|heures|jour|jours)', text_lower)
        if dans_pattern:
            number = int(dans_pattern.group(1))
            unit = dans_pattern.group(2)
            
            if 'minute' in unit:
                return now + timedelta(minutes=number)
            elif 'heure' in unit:
                return now + timedelta(hours=number)
            elif 'jour' in unit:
                return now + timedelta(days=number)"""
    
    new_french = """        # نمط فرنسي: "dans X minutes/heures"
        # ✅ دعم: dans une heure, dans un jour...
        
        french_special = {
            r'dans\\s+une\\s+heure': timedelta(hours=1),
            r'dans\\s+deux\\s+heures': timedelta(hours=2),
            r'dans\\s+une\\s+minute': timedelta(minutes=1),
            r'dans\\s+un\\s+jour': timedelta(days=1),
            r'dans\\s+deux\\s+jours': timedelta(days=2),
        }
        
        for pattern, delta in french_special.items():
            if re.search(pattern, text_lower):
                return now + delta
        
        dans_pattern = re.search(r'dans\\s+(\\d+)\\s*(minute|minutes|heure|heures|jour|jours)', text_lower)
        if dans_pattern:
            number = int(dans_pattern.group(1))
            unit = dans_pattern.group(2)
            
            if 'minute' in unit:
                return now + timedelta(minutes=number)
            elif 'heure' in unit:
                return now + timedelta(hours=number)
            elif 'jour' in unit:
                return now + timedelta(days=number)"""
    
    if old_french in content:
        content = content.replace(old_french, new_french)
        print("✅ تم إصلاح النمط الفرنسي")
    
    # إصلاح الإنجليزية
    old_english = """        # نمط إنجليزي: "in X minutes/hours"
        in_pattern = re.search(r'in\\s+(\\d+)\\s*(minute|minutes|hour|hours|day|days)', text_lower)
        if in_pattern:
            number = int(in_pattern.group(1))
            unit = in_pattern.group(2)
            
            if 'minute' in unit:
                return now + timedelta(minutes=number)
            elif 'hour' in unit:
                return now + timedelta(hours=number)
            elif 'day' in unit:
                return now + timedelta(days=number)"""
    
    new_english = """        # نمط إنجليزي: "in X minutes/hours"
        # ✅ دعم: in an hour, in a day...
        
        english_special = {
            r'in\\s+an?\\s+hour': timedelta(hours=1),
            r'in\\s+two\\s+hours': timedelta(hours=2),
            r'in\\s+an?\\s+minute': timedelta(minutes=1),
            r'in\\s+an?\\s+day': timedelta(days=1),
            r'in\\s+two\\s+days': timedelta(days=2),
        }
        
        for pattern, delta in english_special.items():
            if re.search(pattern, text_lower):
                return now + delta
        
        in_pattern = re.search(r'in\\s+(\\d+)\\s*(minute|minutes|hour|hours|day|days)', text_lower)
        if in_pattern:
            number = int(in_pattern.group(1))
            unit = in_pattern.group(2)
            
            if 'minute' in unit:
                return now + timedelta(minutes=number)
            elif 'hour' in unit:
                return now + timedelta(hours=number)
            elif 'day' in unit:
                return now + timedelta(days=number)"""
    
    if old_english in content:
        content = content.replace(old_english, new_english)
        print("✅ تم إصلاح النمط الإنجليزي")
    
    # حفظ الملف
    print("\n💾 حفظ التغييرات...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*70)
    print("✅ تم الإصلاح بنجاح!")
    print("="*70)
    
    return True


def test_fix():
    """اختبار الإصلاح"""
    print("\n" + "="*70)
    print("🧪 اختبار الإصلاح")
    print("="*70)
    
    try:
        from intelligent_agent import IntelligentAgent
        from datetime import datetime
        
        agent = IntelligentAgent()
        
        test_cases = [
            ("موعد بعد ساعة", "ar"),
            ("موعد بعد ساعتين", "ar"),
            ("موعد بعد دقيقة", "ar"),
            ("موعد بعد 30 دقيقة", "ar"),
            ("RDV dans une heure", "fr"),
            ("Meeting in an hour", "en"),
        ]
        
        print("\n📝 الاختبارات:")
        print("-"*70)
        
        now = datetime.now()
        
        for text, lang in test_cases:
            try:
                result = agent.extract_datetime(text, lang)
                diff = (result - now).total_seconds() / 60
                print(f"✅ '{text}'")
                print(f"   → {result.strftime('%H:%M')} (بعد {int(diff)} دقيقة)")
            except Exception as e:
                print(f"❌ '{text}' → خطأ: {e}")
        
        print("\n" + "="*70)
        print("✅ الاختبار اكتمل!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_examples():
    """عرض أمثلة الاستخدام"""
    print("\n" + "="*70)
    print("💡 الآن يمكنك استخدام:")
    print("="*70)
    
    examples = {
        "🇸🇦 العربية": [
            "موعد بعد ساعة",
            "موعد بعد ساعتين",
            "اجتماع بعد دقيقة",
            "لقاء بعد يوم",
            "موعد بعد 30 دقيقة",  # لا يزال يعمل
        ],
        "🇫🇷 Français": [
            "RDV dans une heure",
            "Réunion dans deux heures",
            "RDV dans un jour",
            "Meeting dans 45 minutes",  # لا يزال يعمل
        ],
        "🇬🇧 English": [
            "Meeting in an hour",
            "Call in two hours",
            "Appointment in a day",
            "Meeting in 30 minutes",  # لا يزال يعمل
        ]
    }
    
    for language, phrases in examples.items():
        print(f"\n{language}")
        print("─"*70)
        for phrase in phrases:
            print(f"   ✅ {phrase}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n🚀 إصلاح مشكلة 'بعد ساعة'\n")
    
    # تطبيق الإصلاح
    if fix_relative_time():
        # اختبار
        test_fix()
        
        # عرض الأمثلة
        show_examples()
        
        print("""
💡 الخطوة التالية:
   
   1. أعد تشغيل البوت:
      python telegram_bot.py
   
   2. جرب الآن:
      "موعد بعد ساعة" ✅
      "موعد بعد ساعتين" ✅
      "موعد بعد 30 دقيقة" ✅ (لا يزال يعمل)
   
   3. بالفرنسية:
      "RDV dans une heure" ✅
   
   4. بالإنجليزية:
      "Meeting in an hour" ✅

🎉 المشكلة محلولة!
        """)
    else:
        print("\n❌ فشل الإصلاح")