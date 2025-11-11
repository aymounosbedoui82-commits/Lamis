#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 إصلاح شامل لاستخراج الوقت في intelligent_agent.py
يحل المشكلة: "على الساعة 16" → 09:00 ❌

الحل: تحسين regex وأولويات الاستخراج
"""

import os
import shutil
from datetime import datetime

def fix_time_extraction():
    """إصلاح استخراج الوقت"""
    
    print("="*70)
    print("🔧 إصلاح استخراج الوقت - intelligent_agent.py")
    print("="*70)
    
    if not os.path.exists('intelligent_agent.py'):
        print("\n❌ intelligent_agent.py غير موجود!")
        print("💡 تأكد من أنك في المجلد الصحيح")
        return False
    
    # نسخة احتياطية
    backup = f"intelligent_agent.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('intelligent_agent.py', backup)
    print(f"\n✅ نسخة احتياطية: {backup}")
    
    # قراءة الملف
    with open('intelligent_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن الدالة القديمة
    old_function = '''    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        """استخراج الوقت من النص - محسّن للصيغة الفرنسية ✅"""
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
        # ✅ محسّن: يقبل "على الساعة 16" بدون am/pm
        hour_pattern = re.search(r'(?:الساعة|على الساعة|ساعة)?\\s*(\\d{1,2})\\s*(صباحا|صباحاً|مساء|مساءً|am|pm)?', text.lower())
        if hour_pattern:
            hour = int(hour_pattern.group(1))
            period = hour_pattern.group(2)
            
            # ✅ معالجة محسّنة للوقت
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
                        hour += 12
            
            if 0 <= hour <= 23:
                return (hour, 0)
        
        return None'''
    
    # الدالة الجديدة المحسّنة
    new_function = '''    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        """
        استخراج الوقت من النص - نسخة محسّنة ✨
        
        يدعم:
        - XX:XX (مثل: 16:30)
        - XXhXX (فرنسي: 16h30)
        - XXh (فرنسي: 16h)
        - على الساعة XX (مثل: على الساعة 16)
        - الساعة XX (مثل: الساعة 4 مساءً)
        - XX صباحاً/مساءً (مثل: 4 مساءً)
        """
        
        # 1️⃣ نمط XX:XX (أعلى أولوية)
        time_colon = re.search(r'(\\d{1,2})[:](\d{2})', text)
        if time_colon:
            hour = int(time_colon.group(1))
            minute = int(time_colon.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                logger.debug(f"✅ استخراج وقت (XX:XX): {hour}:{minute:02d}")
                return (hour, minute)
        
        # 2️⃣ نمط XXhXX (فرنسي مع دقائق)
        french_time_full = re.search(r'(\\d{1,2})h(\\d{2})', text.lower())
        if french_time_full:
            hour = int(french_time_full.group(1))
            minute = int(french_time_full.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                logger.debug(f"✅ استخراج وقت (XXhXX): {hour}:{minute:02d}")
                return (hour, minute)
        
        # 3️⃣ نمط XXh (فرنسي بدون دقائق)
        french_time_hour = re.search(r'(\\d{1,2})h(?!\\d)', text.lower())
        if french_time_hour:
            hour = int(french_time_hour.group(1))
            if 0 <= hour <= 23:
                logger.debug(f"✅ استخراج وقت (XXh): {hour}:00")
                return (hour, 0)
        
        # 4️⃣ نمط "على الساعة XX" أو "الساعة XX" (يجب أن تكون الكلمة موجودة!)
        # هذا يمنع التقاط أرقام التاريخ عن طريق الخطأ
        time_with_keyword = re.search(
            r'(?:على\\s+)?(?:الساعة|ساعة)\\s+(\\d{1,2})(?:\\s*(صباحا|صباحاً|مساء|مساءً|am|pm))?',
            text.lower()
        )
        if time_with_keyword:
            hour = int(time_with_keyword.group(1))
            period = time_with_keyword.group(2)
            
            # معالجة صباحاً/مساءً
            if period:
                if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                    hour += 12
                elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                    hour = 0
            
            if 0 <= hour <= 23:
                logger.debug(f"✅ استخراج وقت (الساعة XX): {hour}:00")
                return (hour, 0)
        
        # 5️⃣ نمط "XX صباحاً" أو "XX مساءً" (بدون كلمة "الساعة")
        time_with_period = re.search(
            r'\\b(\\d{1,2})\\s+(صباحا|صباحاً|مساء|مساءً|am|pm)\\b',
            text.lower()
        )
        if time_with_period:
            hour = int(time_with_period.group(1))
            period = time_with_period.group(2)
            
            # معالجة صباحاً/مساءً
            if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                hour += 12
            elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23:
                logger.debug(f"✅ استخراج وقت (XX مساءً): {hour}:00")
                return (hour, 0)
        
        # إذا لم نجد شيئاً
        logger.debug("⚠️ لم يتم استخراج الوقت")
        return None'''
    
    # التبديل
    if old_function in content:
        content = content.replace(old_function, new_function)
        
        # حفظ
        with open('intelligent_agent.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ تم إصلاح دالة _extract_time!")
        print("\n📋 التحسينات:")
        print("   1. أولوية أفضل لاستخراج الوقت")
        print("   2. إصلاح: 'على الساعة 16' → 16:00 ✓")
        print("   3. إصلاح: 'الساعة 4 مساءً' → 16:00 ✓")
        print("   4. يمنع التقاط أرقام التاريخ عن طريق الخطأ")
        print("   5. دعم أفضل للغة الفرنسية (11h00)")
        
        print("\n💡 الأنماط المدعومة الآن:")
        print("   ✅ 16:30")
        print("   ✅ 11h00 (فرنسي)")
        print("   ✅ على الساعة 16")
        print("   ✅ الساعة 4 مساءً")
        print("   ✅ 4 مساءً")
        
        return True
    else:
        print("\n⚠️ لم يتم العثور على الدالة القديمة")
        print("💡 قد تكون تم تحديثها بالفعل")
        return False


def test_extraction():
    """اختبار سريع للتأكد"""
    print("\n" + "="*70)
    print("🧪 اختبار سريع")
    print("="*70)
    
    try:
        from intelligent_agent import IntelligentAgent
        
        agent = IntelligentAgent()
        
        test_cases = [
            "موعد على الساعة 16",
            "موعد الساعة 4 مساءً",
            "موعد 16:30",
            "RDV à 11h00",
            "موعد يوم 25 ديسمبر على الساعة 16",
        ]
        
        print("\n📝 اختبار الأنماط:")
        for test in test_cases:
            result = agent._extract_time(test)
            if result:
                print(f"   ✅ '{test}' → {result[0]:02d}:{result[1]:02d}")
            else:
                print(f"   ❌ '{test}' → فشل")
        
        return True
        
    except Exception as e:
        print(f"\n⚠️ لم يتم الاختبار: {e}")
        print("💡 شغّل البوت يدوياً للاختبار")
        return False


def main():
    """البرنامج الرئيسي"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🔧 إصلاح استخراج الوقت - Lamis Bot                     ║
╚══════════════════════════════════════════════════════════════════╝

المشكلة:
  ❌ "على الساعة 16" → يضيفه 09:00
  ❌ "الساعة 4 مساءً" → يضيفه 09:00

السبب:
  • regex يلتقط أول رقم في الرسالة (رقم اليوم!)
  • يفشل في استخراج الوقت الصحيح

الحل:
  ✅ تحسين regex وأولويات الاستخراج
  ✅ جعل كلمات "الساعة" إجبارية
  ✅ ترتيب أفضل للأنماط
    """)
    
    try:
        success = fix_time_extraction()
        
        if success:
            print("\n" + "="*70)
            print("🎉 تم الإصلاح بنجاح!")
            print("="*70)
            
            # اختبار سريع
            test_extraction()
            
            print("\n🔄 الخطوات التالية:")
            print("  1. أعد تشغيل البوت:")
            print("     Ctrl+C (إيقاف)")
            print("     python run.py")
            print("\n  2. جرّب:")
            print("     'موعد على الساعة 16' → يجب أن يعطي 16:00 ✓")
            print("     'موعد الساعة 4 مساءً' → يجب أن يعطي 16:00 ✓")
            
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
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()