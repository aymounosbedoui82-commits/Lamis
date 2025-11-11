#!/usr/bin/env python3
# fix_numpy_issue.py
"""
🔧 إصلاح مشكلة تعارض NumPy مع torch
"""

import subprocess
import sys

def fix_numpy():
    """إصلاح مشكلة NumPy"""
    print("="*70)
    print("🔧 إصلاح مشكلة NumPy")
    print("="*70)
    
    print("\n📦 المشكلة:")
    print("  • NumPy 2.3.4 غير متوافق مع torch الحالي")
    print("  • نحتاج لتخفيض إصدار NumPy إلى 1.x")
    
    print("\n🔄 الحل:")
    print("  • إلغاء تثبيت NumPy الحالي")
    print("  • تثبيت NumPy 1.26.4 (آخر إصدار من 1.x)")
    
    confirm = input("\n❓ هل تريد المتابعة؟ (y/n): ").lower()
    
    if confirm != 'y':
        print("❌ تم الإلغاء")
        return
    
    try:
        # إلغاء تثبيت NumPy الحالي
        print("\n🗑️ إلغاء تثبيت NumPy 2.3.4...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "uninstall", "-y", "numpy"
        ])
        print("✅ تم!")
        
        # تثبيت NumPy 1.26.4
        print("\n📥 تثبيت NumPy 1.26.4...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "numpy==1.26.4"
        ])
        print("✅ تم!")
        
        # التحقق
        print("\n🔍 التحقق من الإصدار...")
        result = subprocess.check_output([
            sys.executable, "-c", "import numpy; print(numpy.__version__)"
        ])
        version = result.decode().strip()
        print(f"✅ NumPy الآن: {version}")
        
        print("\n" + "="*70)
        print("🎉 تم إصلاح مشكلة NumPy بنجاح!")
        print("="*70)
        print("\n🚀 الخطوة التالية:")
        print("   python run.py")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        print("\n💡 حل يدوي:")
        print("   pip uninstall numpy")
        print("   pip install numpy==1.26.4")

if __name__ == "__main__":
    fix_numpy()