#!/usr/bin/env python3
# cleanup_project.py
"""
سكريبت لحذف الملفات الزائدة من المشروع
✅ يحتفظ فقط بالملفات الأساسية
"""

import os
import shutil
from datetime import datetime

# الملفات الأساسية التي يجب الاحتفاظ بها
ESSENTIAL_FILES = {
    'intelligent_agent.py',
    'telegram_bot.py',
    'config.py',
    'run.py',
    'agent_data.db',
    'best_model.pth',
    'training_module.py',
    'setup_database.py',
    'simple_reminders.py',
    'reminder_system.py',
    'time_utils.py',
    'utils.py',
    'README.md',  # إذا كان موجوداً
    '.env',       # إذا كان موجوداً
}

# الملفات التي يجب حذفها
FILES_TO_DELETE = [
    # ملفات مكررة/قديمة
    'intelligent_agent_fixed.py',
    'run_fixed.py',
    'training_module_fixed.py',
    'run_py.backup_20251023_190528',
    'trained_model.pth',  # نموذج قديم
    
    # سكريبتات الإصلاح
    'Apply_improvements.py',
    'add_specific_day_feature.py',
    'apply_fix.py',
    'fix_all.py',
    'fix_bot_conflict.py',
    'fix_date_bug.py',
    'fix_extraction.py',
    'fix_intelligent_agent.py',
    'fix_relative_time.py',
    'fix_reminders.py',
    'ix_title_truncation.py',
    'force_reset_bot.py',
    'check_database.py',
    'debug_reminders.py',
    
    # سكريبتات التنظيف
    'cleanup_all.py',
    'cleanup_test_data.py',
    'quick_cleanup.py',
    
    # ملفات الاختبار
    'test_15min_reminder.py',
    'test_final_fix.py',
    'test_full_system.py',
    'test_hour_fix.py',
    'test_intent.py',
    'test_new_feature.py',
    'test_on_time_reminder.py',
    'test_relative_time.py',
    'test_reminders.py',
    'test_specific_day.py',
    'test_time_remaining.py',
    'test_view_appointments.py',
    'full_test.py',
    
    # ملفات اختيارية
    'advanced_features.py',
    'start_lamis.py',
]

def create_backup():
    """إنشاء نسخة احتياطية كاملة قبل الحذف"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_before_cleanup_{timestamp}'
    
    print("="*70)
    print("📦 إنشاء نسخة احتياطية...")
    print("="*70)
    
    try:
        # إنشاء مجلد النسخ الاحتياطي
        os.makedirs(backup_dir, exist_ok=True)
        
        # نسخ جميع الملفات
        copied = 0
        for file in os.listdir('.'):
            if os.path.isfile(file) and file.endswith('.py'):
                shutil.copy2(file, backup_dir)
                copied += 1
        
        # نسخ قاعدة البيانات
        if os.path.exists('agent_data.db'):
            shutil.copy2('agent_data.db', backup_dir)
            copied += 1
        
        print(f"✅ تم نسخ {copied} ملف إلى: {backup_dir}")
        print()
        return backup_dir
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return None


def analyze_project():
    """تحليل الملفات الموجودة"""
    print("="*70)
    print("🔍 تحليل المشروع...")
    print("="*70)
    
    all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    essential_found = []
    deletable_found = []
    other_found = []
    
    for file in all_files:
        if file in ESSENTIAL_FILES:
            essential_found.append(file)
        elif file in FILES_TO_DELETE:
            deletable_found.append(file)
        else:
            other_found.append(file)
    
    print(f"\n📊 الإحصائيات:")
    print(f"   ✅ ملفات أساسية: {len(essential_found)}")
    print(f"   ❌ ملفات زائدة: {len(deletable_found)}")
    print(f"   ⚠️ ملفات أخرى: {len(other_found)}")
    
    if deletable_found:
        print(f"\n🗑️ الملفات التي سيتم حذفها ({len(deletable_found)}):")
        for file in sorted(deletable_found):
            size = os.path.getsize(file) / 1024  # KB
            print(f"   • {file:40s} ({size:.1f} KB)")
    
    if other_found:
        print(f"\n⚠️ ملفات أخرى (لن تُحذف):")
        for file in sorted(other_found):
            print(f"   • {file}")
    
    print()
    return deletable_found


def delete_files(files_to_delete, dry_run=True):
    """حذف الملفات"""
    print("="*70)
    if dry_run:
        print("🔍 وضع المحاكاة (لن يتم الحذف فعلياً)")
    else:
        print("🗑️ حذف الملفات...")
    print("="*70)
    
    deleted = 0
    total_size = 0
    errors = []
    
    for file in files_to_delete:
        if not os.path.exists(file):
            print(f"   ⏭️ {file} (غير موجود)")
            continue
        
        try:
            size = os.path.getsize(file)
            total_size += size
            
            if not dry_run:
                os.remove(file)
                print(f"   ✅ {file}")
            else:
                print(f"   🔍 {file} ({size/1024:.1f} KB)")
            
            deleted += 1
            
        except Exception as e:
            errors.append((file, str(e)))
            print(f"   ❌ {file}: {e}")
    
    print()
    print("="*70)
    if dry_run:
        print(f"📊 سيتم حذف: {deleted} ملف (~{total_size/1024:.1f} KB)")
    else:
        print(f"✅ تم حذف: {deleted} ملف (~{total_size/1024:.1f} KB)")
    print("="*70)
    
    if errors:
        print(f"\n⚠️ أخطاء ({len(errors)}):")
        for file, error in errors:
            print(f"   • {file}: {error}")
    
    return deleted, total_size


def main():
    """البرنامج الرئيسي"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🧹 تنظيف مشروع Lamis Bot - المساعد الذكي             ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 1. تحليل
    deletable = analyze_project()
    
    if not deletable:
        print("\n✨ المشروع نظيف بالفعل! لا توجد ملفات زائدة.")
        return
    
    # 2. خيارات
    print("\n❓ ماذا تريد أن تفعل؟")
    print("   1. محاكاة الحذف (عرض فقط)")
    print("   2. حذف فعلي (مع نسخة احتياطية)")
    print("   3. إلغاء")
    
    choice = input("\n👉 اختيارك (1-3): ").strip()
    
    if choice == '1':
        # محاكاة
        delete_files(deletable, dry_run=True)
        print("\n💡 لم يتم حذف أي شيء. لتنفيذ الحذف، اختر الخيار 2")
        
    elif choice == '2':
        # تأكيد
        confirm = input("\n⚠️ هل أنت متأكد من الحذف؟ (اكتب 'yes' للتأكيد): ").strip().lower()
        
        if confirm != 'yes':
            print("\n❌ تم الإلغاء")
            return
        
        # نسخة احتياطية
        backup_dir = create_backup()
        
        if not backup_dir:
            print("\n❌ فشل إنشاء النسخة الاحتياطية! تم الإلغاء.")
            return
        
        # حذف
        deleted, size = delete_files(deletable, dry_run=False)
        
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                          ✅ تم التنظيف!                          ║
╚══════════════════════════════════════════════════════════════════╝

📊 النتيجة:
   • الملفات المحذوفة: {deleted}
   • المساحة المحررة: {size/1024:.1f} KB
   • النسخة الاحتياطية: {backup_dir}

💡 الملفات المتبقية (الأساسية فقط):
""")
        
        for file in sorted(os.listdir('.')):
            if os.path.isfile(file) and file.endswith('.py'):
                print(f"   ✅ {file}")
        
        print(f"""
🎉 المشروع الآن نظيف ومنظم!

💾 لاسترجاع الملفات:
   نسخها من: {backup_dir}
        """)
        
    else:
        print("\n❌ تم الإلغاء")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()