#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 تنظيف شامل لمشروع Lamis Bot
ينقل الملفات الزائدة إلى مجلد archive بدلاً من حذفها
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import json

# ==========================================
# تعريف الملفات
# ==========================================

# الملفات الأساسية - يجب الاحتفاظ بها
ESSENTIAL_FILES = {
    # === الملفات الرئيسية ===
    'telegram_bot.py',
    'intelligent_agent.py',
    'config.py',
    'run.py',
    
    # === قاعدة البيانات ===
    'agent_data.db',
    'setup_database.py',
    'async_database.py',
    'database_pool.py',
    'database_optimizer.py',
    
    # === نماذج ML ===
    'best_model.pth',
    'training_module.py',
    
    # === الأنظمة المساعدة ===
    'reminder_system.py',
    'time_utils.py',
    'utils.py',
    'custom_reminder_handler.py',
    
    # === التحسينات ===
    'rate_limiter.py',
    'structured_logger.py',
    'error_handler.py',
    'cache_manager.py',
    'advanced_features.py',
    
    # === التحليلات ===
    'analytics_dashboard.py',
    'visual_analytics.py',
    'smart_search.py',
    
    # === الميزات ===
    'calendar_export.py',
    'enhanced_keyboard.py',
    
    # === ملفات الإعدادات ===
    '.env',
    '.env.example',
    '.gitignore',
    'requirements.txt',
    'README.md',
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
    '*_backup_*',
    '*.backup',
    '*-Copie.py',         # نسخ
    '*_Copie.py',
    'run_v*.py',          # إصدارات قديمة
    'activate_*.py',      # ملفات التفعيل
    'add_*.py',           # ملفات الإضافة
    'organize_*.py',      # ملفات التنظيم (مثل هذا الملف نفسه!)
]

# ملفات محددة للنقل
SPECIFIC_UNWANTED = {
    'recurring_appointments.py',  # قديم - الآن في advanced_features
    'simple_reminders.py',        # قديم - الآن reminder_system
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


def get_file_info(filepath: str) -> dict:
    """الحصول على معلومات الملف"""
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'created': datetime.fromtimestamp(stat.st_ctime)
    }


def categorize_files() -> dict:
    """تصنيف جميع الملفات في المشروع"""
    categories = {
        'essential': [],
        'unwanted': [],
        'unknown': [],
        'logs': [],
        'databases': []
    }
    
    for file in os.listdir('.'):
        if not os.path.isfile(file):
            continue
        
        # تجاهل ملفات Python المخفية
        if file.startswith('__'):
            continue
        
        # الملفات الأساسية
        if file in ESSENTIAL_FILES:
            categories['essential'].append(file)
            continue
        
        # ملفات محددة للنقل
        if file in SPECIFIC_UNWANTED:
            categories['unwanted'].append(file)
            continue
        
        # أنماط الملفات الزائدة
        if matches_pattern(file, UNWANTED_PATTERNS):
            categories['unwanted'].append(file)
            continue
        
        # ملفات السجلات
        if file.endswith('.log') or file.endswith('.json'):
            if 'lamis' in file.lower() or 'bot' in file.lower():
                categories['logs'].append(file)
                continue
        
        # ملفات Python غير معروفة
        if file.endswith('.py'):
            categories['unknown'].append(file)
            continue
        
        # قواعد بيانات اختبار
        if file.endswith('.db') and file != 'agent_data.db':
            categories['databases'].append(file)
            continue
    
    return categories


def create_archive_folder() -> str:
    """إنشاء مجلد للأرشفة"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f'_archived_files_{timestamp}'
    
    Path(folder_name).mkdir(exist_ok=True)
    
    # إنشاء ملف README
    readme = f"""# ملفات مؤرشفة - Archived Files

📅 **تاريخ الأرشفة:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 محتوى هذا المجلد

هذا المجلد يحتوي على ملفات تم نقلها من المشروع الرئيسي أثناء التنظيف:

### 🗑️ أنواع الملفات المؤرشفة:
- ✅ **ملفات الإصلاح** (fix_*.py) - تم تطبيق الإصلاحات في الملفات الأساسية
- 🧪 **ملفات الاختبار** (test_*.py) - اختبارات قديمة أو متكررة
- 🔍 **ملفات الفحص** (check_*.py, debug_*.py) - أدوات تشخيص مؤقتة
- 📦 **نسخ احتياطية** (*.backup_*) - نسخ احتياطية قديمة
- 📋 **ملفات السجلات** (*.log, *.json) - سجلات قديمة
- 🗄️ **قواعد بيانات اختبار** (*.db) - قواعد بيانات مؤقتة

## ⚠️ ملاحظات مهمة

### 🔒 الأمان:
- جميع الملفات في هذا المجلد **محفوظة** ولم يتم حذفها
- يمكنك استرجاع أي ملف إذا احتجته لاحقاً
- الملفات الأساسية للمشروع **لم** تُمس

### 🗑️ الحذف الآمن:
إذا كنت متأكداً أنك لن تحتاج هذه الملفات:
```bash
# راجع المحتوى أولاً
ls -la {folder_name}/

# ثم احذف المجلد بالكامل (اختياري)
rm -rf {folder_name}/
```

### 🔙 استرجاع الملفات:
لاسترجاع ملف معين:
```bash
# انسخ الملف المطلوب للمجلد الرئيسي
cp {folder_name}/filename.py .

# أو انقله
mv {folder_name}/filename.py .
```

## 📊 الإحصائيات
سيتم إضافة الإحصائيات تلقائياً بعد اكتمال الأرشفة...
"""
    
    with open(f'{folder_name}/README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    return folder_name


def move_files(categories: dict, archive_folder: str) -> dict:
    """نقل الملفات إلى المجلد"""
    stats = {
        'moved': 0,
        'failed': 0,
        'total_size': 0,
        'files': []
    }
    
    # الملفات المراد نقلها
    files_to_move = (
        categories['unwanted'] + 
        categories['logs'] + 
        categories['databases']
    )
    
    for file in files_to_move:
        try:
            info = get_file_info(file)
            size = info['size']
            
            dest = os.path.join(archive_folder, file)
            shutil.move(file, dest)
            
            stats['moved'] += 1
            stats['total_size'] += size
            stats['files'].append({
                'name': file,
                'size': size,
                'modified': info['modified'].isoformat()
            })
            
            print(f"   ✅ {file} ({size/1024:.1f} KB)")
            
        except Exception as e:
            stats['failed'] += 1
            print(f"   ❌ {file}: {e}")
    
    return stats


def save_manifest(archive_folder: str, stats: dict, categories: dict):
    """حفظ معلومات الأرشفة"""
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'stats': {
            'moved': stats['moved'],
            'failed': stats['failed'],
            'total_size_bytes': stats['total_size'],
            'total_size_mb': stats['total_size'] / (1024 * 1024)
        },
        'categories': {
            'essential_count': len(categories['essential']),
            'unwanted_count': len(categories['unwanted']),
            'unknown_count': len(categories['unknown']),
            'logs_count': len(categories['logs']),
            'databases_count': len(categories['databases'])
        },
        'files': stats['files']
    }
    
    manifest_path = os.path.join(archive_folder, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 تم حفظ التقرير: {manifest_path}")


def print_analysis(categories: dict):
    """طباعة تحليل الملفات"""
    print("\n" + "="*70)
    print("📊 تحليل المشروع")
    print("="*70)
    
    print(f"\n✅ **الملفات الأساسية:** {len(categories['essential'])}")
    print(f"🗑️  **الملفات الزائدة:** {len(categories['unwanted'])}")
    print(f"📋 **ملفات السجلات:** {len(categories['logs'])}")
    print(f"🗄️  **قواعد بيانات اختبار:** {len(categories['databases'])}")
    print(f"❓ **ملفات غير معروفة:** {len(categories['unknown'])}")
    
    # تفاصيل الملفات الزائدة
    if categories['unwanted']:
        print(f"\n🗑️  **الملفات الزائدة ({len(categories['unwanted'])}):**")
        print("-"*70)
        for file in sorted(categories['unwanted']):
            try:
                size = os.path.getsize(file) / 1024
                print(f"   • {file:45s} ({size:6.1f} KB)")
            except:
                print(f"   • {file}")
    
    # الملفات غير المعروفة
    if categories['unknown']:
        print(f"\n❓ **ملفات Python غير معروفة ({len(categories['unknown'])}):**")
        print("-"*70)
        print("   💡 هذه ملفات .py لم يتم التعرف عليها")
        print("   💡 راجعها قبل الحذف")
        print()
        for file in sorted(categories['unknown']):
            try:
                size = os.path.getsize(file) / 1024
                print(f"   • {file:45s} ({size:6.1f} KB)")
            except:
                print(f"   • {file}")


def print_final_status():
    """طباعة حالة المشروع بعد التنظيف"""
    print("\n" + "="*70)
    print("✨ الملفات المتبقية في المشروع")
    print("="*70)
    
    py_files = sorted([f for f in os.listdir('.') if f.endswith('.py') and os.path.isfile(f)])
    db_files = sorted([f for f in os.listdir('.') if f.endswith('.db') and os.path.isfile(f)])
    
    print(f"\n📝 **ملفات Python ({len(py_files)}):**")
    for file in py_files:
        print(f"   ✅ {file}")
    
    if db_files:
        print(f"\n🗄️  **قواعد البيانات ({len(db_files)}):**")
        for file in db_files:
            size = os.path.getsize(file) / (1024 * 1024)
            print(f"   ✅ {file} ({size:.2f} MB)")


# ==========================================
# البرنامج الرئيسي
# ==========================================

def main():
    """نقطة البداية"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🧹 تنظيف شامل لمشروع Lamis Bot                         ║
╚══════════════════════════════════════════════════════════════════╝

هذا السكريبت سيقوم بـ:
  ✓ تحليل جميع الملفات في المشروع
  ✓ تحديد الملفات الزائدة (fix_*.py, test_*.py, إلخ)
  ✓ **نقلها** إلى مجلد archive (بدون حذف!)
  ✓ الاحتفاظ بالملفات الأساسية فقط
  ✓ إنشاء تقرير شامل

🔒 **ضمان الأمان:**
  • لن يتم حذف أي ملف نهائياً
  • جميع الملفات ستُنقل إلى مجلد archive
  • يمكنك استرجاع أي ملف لاحقاً
    """)
    
    # 1. التحليل
    print("="*70)
    print("🔍 المرحلة 1: تحليل الملفات...")
    print("="*70)
    
    categories = categorize_files()
    print_analysis(categories)
    
    # 2. التأكيد
    total_to_move = (
        len(categories['unwanted']) + 
        len(categories['logs']) + 
        len(categories['databases'])
    )
    
    if total_to_move == 0:
        print("\n✨ المشروع نظيف بالفعل! لا توجد ملفات زائدة.")
        return
    
    print("\n" + "="*70)
    print("❓ هل تريد المتابعة؟")
    print("="*70)
    print(f"\n📊 سيتم نقل **{total_to_move} ملف** إلى مجلد archive")
    
    if categories['unknown']:
        print(f"\n⚠️  تحذير: هناك {len(categories['unknown'])} ملف Python غير معروف")
        print("   هذه الملفات لن يتم نقلها تلقائياً")
        print("   راجعها يدوياً إذا أردت")
    
    print("\n💡 الخيارات:")
    print("   y - نعم، انقل الملفات إلى archive")
    print("   n - لا، ألغي العملية")
    print("   s - عرض القائمة فقط (بدون نقل)")
    
    choice = input("\n👉 اختيارك (y/n/s): ").strip().lower()
    
    if choice == 's':
        print("\n📋 تم عرض القائمة فقط. لم يتم نقل أي ملفات.")
        return
    
    if choice != 'y':
        print("\n❌ تم الإلغاء. لم يتم تغيير أي شيء.")
        return
    
    # 3. إنشاء مجلد الأرشفة
    print("\n" + "="*70)
    print("📦 المرحلة 2: إنشاء مجلد الأرشفة...")
    print("="*70)
    
    archive_folder = create_archive_folder()
    print(f"✅ تم إنشاء: {archive_folder}")
    
    # 4. نقل الملفات
    print("\n" + "="*70)
    print("🚚 المرحلة 3: نقل الملفات...")
    print("="*70)
    
    stats = move_files(categories, archive_folder)
    
    # 5. حفظ التقرير
    save_manifest(archive_folder, stats, categories)
    
    # 6. النتيجة النهائية
    print("\n" + "="*70)
    print("📊 ملخص العملية")
    print("="*70)
    print(f"   ✅ تم نقل: {stats['moved']} ملف")
    print(f"   ❌ فشل: {stats['failed']} ملف")
    print(f"   💾 المساحة المحررة: {stats['total_size']/1024:.1f} KB")
    print(f"   📁 المجلد: {archive_folder}")
    
    # 7. حالة المشروع
    print_final_status()
    
    # 8. الرسالة الختامية
    print("\n" + "="*70)
    print("🎉 تم تنظيف المشروع بنجاح!")
    print("="*70)
    
    print(f"""
📝 **الخطوات التالية:**

1. **اختبر البوت:**
   ```bash
   python run.py
   ```

2. **إذا كان كل شيء يعمل:**
   - يمكنك حذف مجلد {archive_folder} لاحقاً
   - أو الاحتفاظ به كنسخة احتياطية

3. **لاسترجاع ملف:**
   ```bash
   cp {archive_folder}/filename.py .
   ```

4. **لحذف المجلد نهائياً (اختياري):**
   ```bash
   rm -rf {archive_folder}
   ```

💾 **الملفات الأساسية المتبقية:** {len(categories['essential'])} ملف
📂 **الملفات المؤرشفة:** {stats['moved']} ملف
✨ **المشروع الآن منظم وجاهز!**
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