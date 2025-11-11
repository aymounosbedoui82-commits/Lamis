#!/usr/bin/env python3
# apply_fix.py
"""
سكريبت تلقائي لإصلاح مشكلة التدريب
"""

import os
import shutil
from datetime import datetime

def main():
    print("="*60)
    print("🔧 إصلاح مشكلة التدريب")
    print("="*60)
    
    # المسارات
    old_file = "training_module.py"
    new_file = "training_module_fixed.py"
    backup_file = f"training_module_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    print("\n1️⃣ فحص الملفات...")
    
    # التحقق من وجود الملف القديم
    if not os.path.exists(old_file):
        print(f"   ❌ لم يتم العثور على: {old_file}")
        return False
    
    print(f"   ✅ وجد: {old_file}")
    
    # التحقق من وجود الملف الجديد
    if not os.path.exists(new_file):
        print(f"\n   ⚠️ لم يتم العثور على: {new_file}")
        print(f"\n   📥 قم بتنزيل الملف من المخرجات")
        return False
    
    print(f"   ✅ وجد: {new_file}")
    
    # إنشاء نسخة احتياطية
    print(f"\n2️⃣ إنشاء نسخة احتياطية...")
    try:
        shutil.copy2(old_file, backup_file)
        print(f"   ✅ تم: {backup_file}")
    except Exception as e:
        print(f"   ❌ فشل: {e}")
        return False
    
    # استبدال الملف
    print(f"\n3️⃣ استبدال الملف...")
    try:
        shutil.copy2(new_file, old_file)
        print(f"   ✅ تم استبدال {old_file}")
    except Exception as e:
        print(f"   ❌ فشل: {e}")
        # استرجاع النسخة الاحتياطية
        print("   🔄 استرجاع النسخة الاحتياطية...")
        shutil.copy2(backup_file, old_file)
        return False
    
    # اختبار الاستيراد
    print(f"\n4️⃣ اختبار الإصلاح...")
    try:
        from training_module import AdaptiveLearner
        print("   ✅ الاستيراد نجح!")
        
        learner = AdaptiveLearner()
        print("   ✅ التهيئة نجحت!")
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        print("\n   🔄 استرجاع النسخة الاحتياطية...")
        shutil.copy2(backup_file, old_file)
        return False
    
    # النتيجة
    print("\n" + "="*60)
    print("✅ تم الإصلاح بنجاح!")
    print("="*60)
    
    print(f"""
💡 الخطوة التالية:

1. جرب التدريب:
   python run.py
   اختر: 2

2. إذا ظهر "لا توجد بيانات كافية":
   - شغّل البوت (الخيار 1)
   - تفاعل معه 10+ مرات
   - ارجع للتدريب

3. النسخة الاحتياطية محفوظة في:
   {backup_file}
    """)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ فشل الإصلاح!")
            print("\n📞 تواصل للحصول على المساعدة")
    except KeyboardInterrupt:
        print("\n\n👋 تم الإلغاء")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()