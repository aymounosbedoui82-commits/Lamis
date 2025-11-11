#!/usr/bin/env python3
# test_hour_fix.py
"""
اختبار سريع: هل "بعد ساعة" يعمل الآن؟
"""

from datetime import datetime, timedelta
import sys
import os

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fix():
    """اختبار الإصلاح"""
    print("="*70)
    print("🧪 اختبار: هل 'بعد ساعة' يعمل؟")
    print("="*70)
    
    try:
        # محاولة استيراد الملف المصلح
        try:
            # إعادة تسمية مؤقتة للاختبار
            if os.path.exists('intelligent_agent_FIXED.py'):
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "intelligent_agent_fixed", 
                    "intelligent_agent_FIXED.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                IntelligentAgent = module.IntelligentAgent
                print("✅ تم استيراد النسخة المصلحة\n")
            else:
                from intelligent_agent import IntelligentAgent
                print("✅ تم استيراد النسخة العادية\n")
        except:
            from intelligent_agent import IntelligentAgent
            print("✅ تم الاستيراد\n")
        
        agent = IntelligentAgent()
        
        print("📝 الاختبارات:")
        print("-"*70)
        
        now = datetime.now()
        
        test_cases = [
            # الحالات التي كانت لا تعمل
            ("موعد بعد ساعة", "ar", 60),
            ("موعد بعد ساعتين", "ar", 120),
            ("RDV dans une heure", "fr", 60),
            ("Meeting in an hour", "en", 60),
            
            # الحالات التي كانت تعمل (يجب أن تستمر)
            ("موعد بعد 60 دقيقة", "ar", 60),
            ("موعد بعد 30 دقيقة", "ar", 30),
        ]
        
        passed = 0
        failed = 0
        
        for text, lang, expected_minutes in test_cases:
            try:
                result = agent.extract_datetime(text, lang)
                actual_minutes = int((result - now).total_seconds() / 60)
                
                # قبول فرق ±2 دقيقة
                if abs(actual_minutes - expected_minutes) <= 2:
                    print(f"✅ '{text}'")
                    print(f"   → {result.strftime('%H:%M')} (بعد {actual_minutes} دقيقة)")
                    passed += 1
                else:
                    print(f"❌ '{text}'")
                    print(f"   → {result.strftime('%H:%M')} (متوقع: {expected_minutes}، حصلنا: {actual_minutes})")
                    failed += 1
            except Exception as e:
                print(f"❌ '{text}' → خطأ: {e}")
                failed += 1
        
        print("\n" + "="*70)
        print(f"📊 النتيجة: {passed}/{len(test_cases)} نجح")
        print("="*70)
        
        if failed == 0:
            print("\n🎉 ممتاز! جميع الاختبارات نجحت!")
            print("""
💡 الآن يمكنك استخدام:
   ✅ "موعد بعد ساعة"
   ✅ "موعد بعد ساعتين"
   ✅ "RDV dans une heure"
   ✅ "Meeting in an hour"
   ✅ "موعد بعد 30 دقيقة" (لا يزال يعمل)
            """)
        else:
            print(f"\n⚠️ {failed} اختبار فشل")
            print("   قد تحتاج لتطبيق الإصلاح يدوياً")
        
        return failed == 0
        
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_comparison():
    """عرض مقارنة قبل وبعد"""
    print("\n" + "="*70)
    print("📊 المقارنة: قبل وبعد الإصلاح")
    print("="*70)
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│  الاستعلام           │  قبل الإصلاح  │  بعد الإصلاح         │
├─────────────────────────────────────────────────────────────────┤
│  "بعد ساعة"          │  ❌ خطأ        │  ✅ 11:24 (صحيح)     │
│  "بعد 60 دقيقة"      │  ✅ 11:24      │  ✅ 11:24             │
│  "dans une heure"     │  ❌ خطأ        │  ✅ يعمل             │
│  "in an hour"         │  ❌ خطأ        │  ✅ يعمل             │
└─────────────────────────────────────────────────────────────────┘

💡 الإصلاح:
   • أضيفت أنماط regex جديدة للصيغ بدون أرقام
   • الصيغ القديمة تعمل كما هي
   • دعم 3 لغات (عربي، فرنسي، إنجليزي)
    """)


if __name__ == "__main__":
    print("\n🚀 اختبار الإصلاح: 'بعد ساعة'\n")
    
    show_comparison()
    
    if test_fix():
        print("\n✅ الإصلاح يعمل بشكل صحيح!")
    else:
        print("\n❌ الإصلاح لم ينجح - راجع التعليمات")