#!/usr/bin/env python3
# full_test.py
"""
اختبار شامل لكامل النظام
"""

import sqlite3
from datetime import datetime, timedelta
import os

def test_full_system():
    """اختبار شامل"""
    print("="*60)
    print("🧪 اختبار شامل للنظام")
    print("="*60)
    
    try:
        from intelligent_agent import IntelligentAgent
        
        agent = IntelligentAgent()
        
        # 1. اختبار موعد بعد ساعتين (يجب أن ينشئ تذكيرين: 1 ساعة + 15 دقيقة)
        print("\n" + "-"*60)
        print("📝 اختبار 1: موعد بعد ساعتين")
        print("-"*60)
        
        future1 = datetime.now() + timedelta(hours=2)
        apt1 = agent.db.add_appointment(
            user_id=99999,
            title="اختبار - موعد بعد ساعتين",
            description="",
            date_time=future1
        )
        
        conn = sqlite3.connect(agent.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM reminders WHERE appointment_id = ?', (apt1,))
        count1 = cursor.fetchone()[0]
        
        expected1 = 2  # 1 ساعة + 15 دقيقة
        if count1 == expected1:
            print(f"✅ نجح! {count1} تذكير (متوقع: {expected1})")
        else:
            print(f"⚠️ {count1} تذكير (متوقع: {expected1})")
        
        # 2. اختبار موعد بعد 30 دقيقة (يجب أن ينشئ تذكير واحد: 15 دقيقة)
        print("\n" + "-"*60)
        print("📝 اختبار 2: موعد بعد 30 دقيقة")
        print("-"*60)
        
        future2 = datetime.now() + timedelta(minutes=30)
        apt2 = agent.db.add_appointment(
            user_id=99999,
            title="اختبار - موعد بعد 30 دقيقة",
            description="",
            date_time=future2
        )
        
        cursor.execute('SELECT COUNT(*) FROM reminders WHERE appointment_id = ?', (apt2,))
        count2 = cursor.fetchone()[0]
        
        expected2 = 1  # 15 دقيقة فقط
        if count2 == expected2:
            print(f"✅ نجح! {count2} تذكير (متوقع: {expected2})")
        else:
            print(f"⚠️ {count2} تذكير (متوقع: {expected2})")
        
        # 3. اختبار موعد بعد 30 ساعة (يجب أن ينشئ 3 تذكيرات: 24 ساعة + 1 ساعة + 15 دقيقة)
        print("\n" + "-"*60)
        print("📝 اختبار 3: موعد بعد 30 ساعة")
        print("-"*60)
        
        future3 = datetime.now() + timedelta(hours=30)
        apt3 = agent.db.add_appointment(
            user_id=99999,
            title="اختبار - موعد بعد 30 ساعة",
            description="",
            date_time=future3
        )
        
        cursor.execute('SELECT COUNT(*) FROM reminders WHERE appointment_id = ?', (apt3,))
        count3 = cursor.fetchone()[0]
        
        expected3 = 3  # 24 ساعة + 1 ساعة + 15 دقيقة
        if count3 == expected3:
            print(f"✅ نجح! {count3} تذكير (متوقع: {expected3})")
        else:
            print(f"⚠️ {count3} تذكير (متوقع: {expected3})")
        
        # 4. اختبار موعد بعد 10 دقائق (يجب ألا ينشئ تذكيرات)
        print("\n" + "-"*60)
        print("📝 اختبار 4: موعد بعد 10 دقائق")
        print("-"*60)
        
        future4 = datetime.now() + timedelta(minutes=10)
        apt4 = agent.db.add_appointment(
            user_id=99999,
            title="اختبار - موعد بعد 10 دقائق",
            description="",
            date_time=future4
        )
        
        cursor.execute('SELECT COUNT(*) FROM reminders WHERE appointment_id = ?', (apt4,))
        count4 = cursor.fetchone()[0]
        
        expected4 = 0  # قريب جداً
        if count4 == expected4:
            print(f"✅ نجح! {count4} تذكير (متوقع: {expected4})")
        else:
            print(f"⚠️ {count4} تذكير (متوقع: {expected4})")
        
        conn.close()
        
        # النتيجة النهائية
        print("\n" + "="*60)
        print("📊 النتيجة النهائية")
        print("="*60)
        
        total_tests = 4
        passed = sum([
            count1 == expected1,
            count2 == expected2,
            count3 == expected3,
            count4 == expected4
        ])
        
        print(f"\n✅ نجح: {passed}/{total_tests}")
        
        if passed == total_tests:
            print("\n🎉 ممتاز! النظام يعمل بشكل صحيح!")
            print("\n💡 الخطوة التالية:")
            print("   python telegram_bot.py")
        else:
            print(f"\n⚠️ فشل: {total_tests - passed}/{total_tests}")
            print("\n🔧 يجب مراجعة دالة add_appointment")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_full_system()