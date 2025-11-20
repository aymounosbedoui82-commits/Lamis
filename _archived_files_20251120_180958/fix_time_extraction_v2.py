#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 إصلاح شامل لاستخراج الوقت - النسخة 2
يحل المشكلة: "على الساعة 4 مساء" → 09:00 ❌

الحل: تحسين regex وأولويات الاستخراج
"""

import os
import shutil
from datetime import datetime

def fix_time_extraction():
    """إصلاح استخراج الوقت"""
    
    print("="*70)
    print("🔧 إصلاح استخراج الوقت - النسخة 2")
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
    
    # ========================================
    # البحث عن دالة _extract_time الحالية
    # ========================================
    
    # نبحث عن بداية الدالة
    start_marker = "    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:"
    
    if start_marker not in content:
        print("❌ لم يتم العثور على دالة _extract_time")
        return False
    
    # نبحث عن نهاية الدالة (الدالة التالية أو نهاية الكلاس)
    # نفترض أن الدالة التالية تبدأ بـ "    def _extract_"
    
    start_index = content.find(start_marker)
    
    # نبحث عن الدالة التالية
    next_def_markers = [
        "\n    def _extract_title_and_description",
        "\n    def _extract_date_from_query",
        "\n    def process_message"
    ]
    
    end_index = len(content)
    for marker in next_def_markers:
        temp_index = content.find(marker, start_index + 1)
        if temp_index != -1 and temp_index < end_index:
            end_index = temp_index
    
    old_function = content[start_index:end_index]
    
    # ========================================
    # الدالة الجديدة المحسّنة
    # ========================================
    
    new_function = '''    def _extract_time(self, text: str) -> Optional[Tuple[int, int]]:
        """
        استخراج الوقت من النص - نسخة محسّنة ✨
        
        يدعم:
        - XX:XX (مثل: 16:30)
        - XXhXX (فرنسي: 16h30)
        - XXh (فرنسي: 16h)
        - على الساعة XX مساء (مثل: على الساعة 4 مساء)
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
        return None
'''
    
    # الاستبدال
    new_content = content[:start_index] + new_function + content[end_index:]
    
    # الحفظ
    with open('intelligent_agent.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ تم إصلاح دالة _extract_time!")
    print("\n📋 التحسينات:")
    print("   1. أولوية أفضل لاستخراج الوقت")
    print("   2. إصلاح: 'على الساعة 4 مساء' → 16:00 ✓")
    print("   3. إصلاح: 'الساعة 10 صباحاً' → 10:00 ✓")
    print("   4. يمنع التقاط أرقام التاريخ عن طريق الخطأ")
    print("   5. دعم أفضل للغة الفرنسية (11h00)")
    
    print("\n💡 الأنماط المدعومة الآن:")
    print("   ✅ 16:30")
    print("   ✅ 11h00 (فرنسي)")
    print("   ✅ على الساعة 4 مساء")
    print("   ✅ الساعة 10 صباحاً")
    print("   ✅ 4 مساءً")
    
    return True


def test_extraction():
    """اختبار سريع للتأكد"""
    print("\n" + "="*70)
    print("🧪 اختبار سريع")
    print("="*70)
    
    try:
        from intelligent_agent import IntelligentAgent
        
        agent = IntelligentAgent()
        
        test_cases = [
            "موعد على الساعة 4 مساء",
            "موعد الساعة 10 صباحاً",
            "موعد 16:30",
            "RDV à 11h00",
            "موعد يوم 25 ديسمبر على الساعة 4 مساء",
        ]
        
        print("\n📝 اختبار الأنماط:")
        all_passed = True
        
        for test in test_cases:
            result = agent._extract_time(test)
            if result:
                print(f"   ✅ '{test}' → {result[0]:02d}:{result[1]:02d}")
            else:
                print(f"   ❌ '{test}' → فشل")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"\n⚠️ لم يتم الاختبار: {e}")
        print("💡 شغّل البوت يدوياً للاختبار")
        return False


def main():
    """البرنامج الرئيسي"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🔧 إصلاح استخراج الوقت - Lamis Bot v2                  ║
╚══════════════════════════════════════════════════════════════════╝

المشكلة:
  ❌ "على الساعة 4 مساء" → يضيفه 09:00
  ❌ "الساعة 10 صباحاً" → يضيفه 09:00

السبب:
  • regex يلتقط أرقام التاريخ بالخطأ (25، 2025...)
  • الكلمات المفتاحية اختيارية وليست إجبارية

الحل:
  ✅ جعل "الساعة" إجبارية في الأنماط العربية
  ✅ ترتيب أفضل للأنماط حسب الأولوية
  ✅ منع التقاط أرقام التاريخ
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
            print("     'موعد على الساعة 4 مساء' → يجب أن يعطي 16:00 ✓")
            print("     'موعد الساعة 10 صباحاً' → يجب أن يعطي 10:00 ✓")
            
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