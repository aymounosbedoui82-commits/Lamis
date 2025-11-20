#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 تشخيص سريع لـ Lamis Bot
يفحص جميع المكونات الأساسية
"""

import os
import sys
from pathlib import Path

def check_files():
    """فحص الملفات الأساسية"""
    print("="*70)
    print("📁 فحص الملفات الأساسية")
    print("="*70)
    
    essential_files = [
        'intelligent_agent.py',
        'telegram_bot.py',
        'config.py',
        'run.py',
        'reminder_system.py',
        'agent_data.db',
    ]
    
    all_ok = True
    for file in essential_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file:30s} ({size:,} bytes)")
        else:
            print(f"  ❌ {file:30s} (غير موجود)")
            all_ok = False
    
    return all_ok


def test_imports():
    """اختبار الاستيرادات"""
    print("\n" + "="*70)
    print("📦 اختبار الاستيرادات")
    print("="*70)
    
    imports_to_test = [
        ('telegram', 'python-telegram-bot'),
        ('intelligent_agent', 'ملف المشروع'),
        ('config', 'ملف المشروع'),
        ('reminder_system', 'ملف المشروع'),
    ]
    
    all_ok = True
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module:30s} ({description})")
        except ImportError as e:
            print(f"  ❌ {module:30s} - {str(e)[:40]}...")
            all_ok = False
    
    return all_ok


def test_database():
    """اختبار قاعدة البيانات"""
    print("\n" + "="*70)
    print("🗄️ اختبار قاعدة البيانات")
    print("="*70)
    
    if not os.path.exists('agent_data.db'):
        print("  ❌ قاعدة البيانات غير موجودة")
        print("  💡 شغّل: python setup_database.py")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect('agent_data.db')
        cursor = conn.cursor()
        
        tables = ['appointments', 'interactions', 'reminders']
        all_ok = True
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table:20s} ({count} سجل)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ خطأ: {e}")
        return False


def test_time_extraction():
    """اختبار استخراج الوقت"""
    print("\n" + "="*70)
    print("⏰ اختبار استخراج الوقت")
    print("="*70)
    
    try:
        from intelligent_agent import IntelligentAgent
        agent = IntelligentAgent()
        
        tests = [
            ("موعد على الساعة 16", 16, 0),
            ("موعد 16:30", 16, 30),
            ("RDV à 11h00", 11, 0),
        ]
        
        passed = 0
        for text, exp_h, exp_m in tests:
            result = agent._extract_time(text)
            if result and result[0] == exp_h and result[1] == exp_m:
                print(f"  ✅ '{text}' → {result[0]:02d}:{result[1]:02d}")
                passed += 1
            else:
                actual = f"{result[0]:02d}:{result[1]:02d}" if result else "None"
                print(f"  ❌ '{text}' → {actual} (متوقع: {exp_h:02d}:{exp_m:02d})")
        
        return passed == len(tests)
        
    except Exception as e:
        print(f"  ❌ خطأ: {e}")
        return False


def test_bot_token():
    """فحص Token البوت"""
    print("\n" + "="*70)
    print("🔑 فحص Token البوت")
    print("="*70)
    
    if not os.path.exists('.env'):
        print("  ❌ ملف .env غير موجود")
        print("  💡 أنشئ ملف .env وأضف: TELEGRAM_BOT_TOKEN=your_token")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'TELEGRAM_BOT_TOKEN' not in content:
            print("  ❌ TELEGRAM_BOT_TOKEN غير موجود في .env")
            return False
        elif 'YOUR_BOT_TOKEN_HERE' in content:
            print("  ❌ Token لم يتم تعيينه بعد")
            print("  💡 عدّل .env وأضف token من @BotFather")
            return False
        else:
            print("  ✅ Token موجود في .env")
            return True


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🔍 تشخيص سريع - Lamis Bot                              ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        'ملفات': check_files(),
        'استيرادات': test_imports(),
        'قاعدة البيانات': test_database(),
        'Token': test_bot_token(),
        'استخراج الوقت': test_time_extraction(),
    }
    
    # النتيجة النهائية
    print("\n" + "="*70)
    print("📊 ملخص التشخيص")
    print("="*70)
    
    for check, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"  {emoji} {check}")
    
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "="*70)
    print(f"النتيجة: {passed}/{total} فحص نجح ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ممتاز! البوت جاهز للتشغيل!")
        print("💡 شغّل البوت: python run.py")
    elif passed >= 3:
        print("\n✅ جيد! معظم المكونات تعمل")
        print("💡 راجع الأخطاء أعلاه وأصلحها")
    else:
        print("\n⚠️ تحذير: عدة مشاكل يجب حلها")
        print("💡 راجع الأخطاء أعلاه واحداً تلو الآخر")
    
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ تم الإيقاف")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()