#!/usr/bin/env python3
# fix_all.py
"""
سكريبت شامل لإصلاح جميع المشاكل دفعة واحدة
"""

import os
import shutil
from datetime import datetime

def main():
    print("="*70)
    print("🔧 إصلاح شامل - جميع المشاكل")
    print("="*70)
    
    fixes_needed = [
        {
            'name': 'training_module.py',
            'old': 'training_module.py',
            'new': 'training_module_fixed.py',
            'description': 'نظام التدريب'
        },
        {
            'name': 'run.py',
            'old': 'run.py',
            'new': 'run_fixed.py',
            'description': 'سكريبت التشغيل'
        }
    ]
    
    total_fixed = 0
    total_failed = 0
    
    for fix in fixes_needed:
        print(f"\n{'─'*70}")
        print(f"📝 إصلاح: {fix['description']}")
        print(f"{'─'*70}")
        
        old_file = fix['old']
        new_file = fix['new']
        
        # التحقق من وجود الملف القديم
        if not os.path.exists(old_file):
            print(f"   ℹ️ الملف غير موجود: {old_file}")
            print(f"   ⏭️ تخطي...")
            continue
        
        print(f"   ✅ وجد: {old_file}")
        
        # التحقق من وجود الملف الجديد
        if not os.path.exists(new_file):
            print(f"   ❌ الملف الجديد غير موجود: {new_file}")
            print(f"   📥 قم بتنزيله من المخرجات أولاً")
            total_failed += 1
            continue
        
        print(f"   ✅ وجد: {new_file}")
        
        # إنشاء نسخة احتياطية
        backup_name = f"{old_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(old_file, backup_name)
            print(f"   💾 نسخة احتياطية: {backup_name}")
        except Exception as e:
            print(f"   ⚠️ فشل النسخ الاحتياطي: {e}")
        
        # استبدال الملف
        try:
            shutil.copy2(new_file, old_file)
            print(f"   ✅ تم الاستبدال!")
            total_fixed += 1
        except Exception as e:
            print(f"   ❌ فشل: {e}")
            total_failed += 1
    
    # النتيجة النهائية
    print("\n" + "="*70)
    print("📊 النتيجة:")
    print("="*70)
    print(f"   ✅ نجح: {total_fixed}")
    print(f"   ❌ فشل: {total_failed}")
    
    if total_failed == 0 and total_fixed > 0:
        print("\n🎉 تم إصلاح جميع المشاكل بنجاح!")
        
        # اختبار الإصلاحات
        print("\n" + "─"*70)
        print("🧪 اختبار الإصلاحات...")
        print("─"*70)
        
        try:
            print("\n1️⃣ اختبار training_module...")
            from training_module import AdaptiveLearner
            learner = AdaptiveLearner()
            print("   ✅ يعمل بشكل صحيح!")
        except Exception as e:
            print(f"   ⚠️ خطأ: {e}")
        
        try:
            print("\n2️⃣ اختبار run...")
            # لا نحتاج لاستيراد run.py، فقط التأكد من وجوده
            if os.path.exists('run.py'):
                print("   ✅ الملف موجود!")
        except Exception as e:
            print(f"   ⚠️ خطأ: {e}")
        
        print("\n" + "="*70)
        print("💡 الخطوة التالية:")
        print("="*70)
        print("""
1. شغّل البوت أولاً:
   python run.py → اختر 1

2. تفاعل معه على Telegram (10+ رسائل):
   "موعد غداً الساعة 3"
   "عرض مواعيدي"
   "مواعيدي اليوم"
   ... إلخ

3. ارجع للتدريب:
   python run.py → اختر 2

🎉 استمتع بالبوت الذكي!
        """)
    
    elif total_failed > 0:
        print("\n⚠️ بعض الإصلاحات فشلت!")
        print("\n💡 تأكد من:")
        print("   1. تنزيل جميع الملفات المُصلحة")
        print("   2. وضعها في مجلد المشروع")
        print("   3. إعادة تشغيل السكريبت")
    
    else:
        print("\n❌ لم يتم العثور على ملفات للإصلاح!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم الإلغاء")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()