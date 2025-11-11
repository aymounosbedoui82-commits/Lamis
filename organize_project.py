#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗂️ تنظيف وترتيب ملفات المشروع
ينقل الملفات الزائدة إلى مجلد منفصل
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# ==========================================
# تعريف الملفات
# ==========================================

# الملفات الأساسية - يجب الاحتفاظ بها
ESSENTIAL_FILES = {
    # الملفات الرئيسية
    'telegram_bot.py',
    'intelligent_agent.py',
    'config.py',
    'run.py',
    
    # قاعدة البيانات
    'agent_data.db',
    'best_model.pth',
    
    # الأنظمة المساعدة
    'reminder_system.py',
    'time_utils.py',
    'utils.py',
    'training_module.py',
    'setup_database.py',
    
    # التحسينات (المرحلة 2)
    'rate_limiter.py',
    'structured_logger.py',
    'error_handler.py',
    'cache_manager.py',
    'database_pool.py',
    'advanced_features.py',
    'analytics_dashboard.py',
    'enhanced_keyboard.py',
    'custom_reminder_handler.py',
    
    # ملفات الإعدادات
    '.env',
    '.env.example',
    '.gitignore',
    'requirements.txt',
    'README.md',
    
    # السكريبتات المفيدة
    'diagnose_bot.py',  # السكريبت الجديد
}

# أنماط الملفات الزائدة
UNWANTED_PATTERNS = [
    'fix_*.py',           # ملفات الإصلاح
    'test_*.py',          # ملفات الاختبار
    'check_*.py',         # ملفات الفحص
    'debug_*.py',         # ملفات التشخيص
    'Apply_*.py',         # ملفات التطبيق
    'apply_*.py',
    'Cleanup_*.py',       # ملفات التنظيف
    'cleanup_*.py',
    'quick_*.py',         # إصلاحات سريعة
    'full_test*.py',      # اختبارات
    '*.backup_*',         # نسخ احتياطية
    '*_-_Copie.py',       # نسخ
    'run_v*.py',          # إصدارات قديمة
    'activate_*.py',      # ملفات التفعيل
    'add_*.py',           # ملفات الإضافة
]

# ملفات محددة للنقل
SPECIFIC_UNWANTED = {
    'recurring_appointments.py',  # قديم - الآن في advanced_features
    'simple_reminders.py',        # قديم - الآن reminder_system
    'run_v2.py',                  # نسخة قديمة
    'test_features.db',           # قاعدة بيانات اختبار
    'test_pool.db',               # قاعدة بيانات اختبار
}

# ==========================================
# دوال مساعدة
# ==========================================

def matches_pattern(filename: str, patterns: list) -> bool:
    """فحص إذا كان الملف يطابق أحد الأنماط"""
    import fnmatch
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False

def get_file_category(filename: str) -> str:
    """تحديد فئة الملف"""
    if filename in ESSENTIAL_FILES:
        return 'essential'
    
    if filename in SPECIFIC_UNWANTED:
        return 'unwanted'
    
    if matches_pattern(filename, UNWANTED_PATTERNS):
        return 'unwanted'
    
    # فحص الامتدادات
    if filename.endswith('.pyc') or filename.endswith('.pyo'):
        return 'unwanted'
    
    if filename.endswith('.log') or filename.endswith('.json'):
        if filename.startswith('lamis_bot'):
            return 'log'
        return 'unwanted'
    
    return 'unknown'

def analyze_project():
    """تحليل ملفات المشروع"""
    print("="*70)
    print("🔍 تحليل ملفات المشروع...")
    print("="*70)
    
    categories = {
        'essential': [],
        'unwanted': [],
        'unknown': [],
        'log': []
    }
    
    # فحص جميع ملفات .py
    for file in os.listdir('.'):
        if os.path.isfile(file):
            category = get_file_category(file)
            categories[category].append(file)
    
    # عرض النتائج
    print(f"\n📊 النتائج:")
    print(f"   ✅ ملفات أساسية: {len(categories['essential'])}")
    print(f"   🗑️  ملفات زائدة: {len(categories['unwanted'])}")
    print(f"   📋 ملفات سجلات: {len(categories['log'])}")
    print(f"   ❓ ملفات غير معروفة: {len(categories['unknown'])}")
    
    return categories

def show_files(categories):
    """عرض تفاصيل الملفات"""
    print("\n" + "="*70)
    print("📋 تفاصيل الملفات")
    print("="*70)
    
    # الملفات الزائدة
    if categories['unwanted']:
        print(f"\n🗑️  الملفات الزائدة ({len(categories['unwanted'])}):")
        print("-"*70)
        for file in sorted(categories['unwanted']):
            size = os.path.getsize(file) / 1024  # KB
            print(f"   • {file:50s} ({size:6.1f} KB)")
    
    # ملفات السجلات
    if categories['log']:
        print(f"\n📋 ملفات السجلات ({len(categories['log'])}):")
        print("-"*70)
        for file in sorted(categories['log']):
            size = os.path.getsize(file) / 1024  # KB
            print(f"   • {file:50s} ({size:6.1f} KB)")
    
    # الملفات غير المعروفة
    if categories['unknown']:
        print(f"\n❓ ملفات غير معروفة ({len(categories['unknown'])}):")
        print("-"*70)
        for file in sorted(categories['unknown']):
            size = os.path.getsize(file) / 1024  # KB
            print(f"   • {file:50s} ({size:6.1f} KB)")
        print("\n💡 هذه الملفات لن يتم نقلها تلقائياً")

def create_archive_folder():
    """إنشاء مجلد للأرشفة"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f'old_files_{timestamp}'
    
    # إنشاء المجلد
    Path(folder_name).mkdir(exist_ok=True)
    
    # إنشاء ملف README داخل المجلد
    readme_content = f"""# ملفات قديمة - Old Files

تاريخ الأرشفة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 محتوى هذا المجلد

هذا المجلد يحتوي على ملفات قديمة تم نقلها من المشروع الرئيسي:

- ✅ ملفات الإصلاح (fix_*.py)
- 🧪 ملفات الاختبار (test_*.py)
- 🔍 ملفات الفحص (check_*.py)
- 🐛 ملفات التشخيص (debug_*.py)
- 📦 نسخ احتياطية قديمة
- 📋 ملفات السجلات القديمة

## ⚠️ ملاحظة

يمكنك حذف هذا المجلد بالكامل إذا كنت متأكداً أنك لا تحتاج هذه الملفات.
أو الاحتفاظ به كنسخة احتياطية.

## 🔙 استرجاع الملفات

إذا احتجت استرجاع ملف معين:
1. افتح هذا المجلد
2. انسخ الملف المطلوب
3. الصقه في المجلد الرئيسي للمشروع
"""
    
    readme_path = os.path.join(folder_name, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return folder_name

def move_files(categories, folder_name):
    """نقل الملفات إلى المجلد"""
    print("\n" + "="*70)
    print(f"📦 نقل الملفات إلى: {folder_name}")
    print("="*70)
    
    moved = 0
    failed = 0
    total_size = 0
    
    # نقل الملفات الزائدة
    files_to_move = categories['unwanted'] + categories['log']
    
    for file in files_to_move:
        try:
            size = os.path.getsize(file)
            total_size += size
            
            dest = os.path.join(folder_name, file)
            shutil.move(file, dest)
            
            print(f"   ✅ {file}")
            moved += 1
            
        except Exception as e:
            print(f"   ❌ {file}: {e}")
            failed += 1
    
    # الملخص
    print("\n" + "="*70)
    print("📊 ملخص العملية")
    print("="*70)
    print(f"   ✅ تم النقل: {moved} ملف")
    print(f"   ❌ فشل: {failed} ملف")
    print(f"   💾 المساحة المحررة: {total_size/1024:.1f} KB")
    print(f"   📁 المجلد: {folder_name}")
    
    return moved, failed

def show_remaining_files():
    """عرض الملفات المتبقية"""
    print("\n" + "="*70)
    print("✨ الملفات المتبقية في المشروع")
    print("="*70)
    
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and os.path.isfile(f)]
    py_files.sort()
    
    print(f"\n📝 ملفات Python ({len(py_files)}):")
    for file in py_files:
        print(f"   ✅ {file}")
    
    # قواعد البيانات
    db_files = [f for f in os.listdir('.') if f.endswith('.db') and os.path.isfile(f)]
    if db_files:
        print(f"\n🗄️  قواعد البيانات ({len(db_files)}):")
        for file in db_files:
            print(f"   ✅ {file}")

# ==========================================
# البرنامج الرئيسي
# ==========================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🗂️  تنظيف وترتيب مشروع Lamis Bot                       ║
╚══════════════════════════════════════════════════════════════════╝

هذا السكريبت سيقوم بـ:
  ✓ تحليل جميع الملفات
  ✓ تحديد الملفات الزائدة
  ✓ نقلها إلى مجلد منفصل
  ✓ الاحتفاظ بالملفات الأساسية فقط

💡 الملفات الأساسية التي سيتم الاحتفاظ بها:
  • telegram_bot.py
  • intelligent_agent.py
  • config.py
  • run.py
  • reminder_system.py
  • و الملفات المهمة الأخرى...

🗑️  الملفات التي سيتم نقلها:
  • ملفات الإصلاح (fix_*.py)
  • ملفات الاختبار (test_*.py)
  • ملفات الفحص (check_*.py)
  • النسخ الاحتياطية القديمة
  • ملفات السجلات القديمة
    """)
    
    # 1. التحليل
    categories = analyze_project()
    
    # 2. عرض التفاصيل
    show_files(categories)
    
    # 3. التأكيد
    if not categories['unwanted'] and not categories['log']:
        print("\n✨ المشروع نظيف بالفعل! لا توجد ملفات زائدة.")
        return
    
    total_to_move = len(categories['unwanted']) + len(categories['log'])
    
    print("\n" + "="*70)
    print("❓ هل تريد نقل الملفات الزائدة؟")
    print("="*70)
    print(f"\n📊 سيتم نقل {total_to_move} ملف إلى مجلد منفصل")
    print("\n💡 الخيارات:")
    print("   y - نعم، انقل الملفات")
    print("   n - لا، ألغي العملية")
    print("   s - عرض قائمة الملفات فقط (بدون نقل)")
    
    choice = input("\n👉 اختيارك (y/n/s): ").strip().lower()
    
    if choice == 's':
        print("\n📋 تم عرض القائمة فقط. لم يتم نقل أي ملفات.")
        return
    
    if choice != 'y':
        print("\n❌ تم الإلغاء. لم يتم تغيير أي شيء.")
        return
    
    # 4. إنشاء مجلد الأرشفة
    folder_name = create_archive_folder()
    print(f"\n✅ تم إنشاء مجلد: {folder_name}")
    
    # 5. نقل الملفات
    moved, failed = move_files(categories, folder_name)
    
    # 6. عرض الملفات المتبقية
    show_remaining_files()
    
    # 7. النتيجة النهائية
    print("\n" + "="*70)
    print("🎉 تم تنظيف المشروع بنجاح!")
    print("="*70)
    
    print(f"""
✅ ملخص العملية:
  • تم نقل {moved} ملف
  • المجلد: {folder_name}
  • المشروع الآن منظم ونظيف!

💡 الخطوات التالية:
  1. تأكد من أن البوت يعمل: python diagnose_bot.py
  2. شغّل البوت: python run.py
  3. إذا كان كل شيء يعمل، يمكنك حذف مجلد {folder_name}

📦 لاسترجاع ملف معين:
  1. افتح مجلد {folder_name}
  2. انسخ الملف المطلوب
  3. الصقه في المجلد الرئيسي
    """)
    
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()