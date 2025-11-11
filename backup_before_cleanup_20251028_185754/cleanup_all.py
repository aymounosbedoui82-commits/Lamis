#!/usr/bin/env python3
# cleanup_all.py
"""
تنظيف شامل لقاعدة البيانات من البيانات التجريبية
"""

import sqlite3
import os

def cleanup_database():
    """حذف جميع البيانات التجريبية"""
    print("="*60)
    print("🧹 تنظيف قاعدة البيانات")
    print("="*60)
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. عرض الإحصائيات قبل الحذف
    print("\n📊 الإحصائيات قبل التنظيف:")
    
    cursor.execute('SELECT COUNT(*) FROM appointments')
    apt_count = cursor.fetchone()[0]
    print(f"   • المواعيد: {apt_count}")
    
    cursor.execute('SELECT COUNT(*) FROM reminders')
    rem_count = cursor.fetchone()[0]
    print(f"   • التذكيرات: {rem_count}")
    
    cursor.execute('SELECT COUNT(*) FROM interactions')
    int_count = cursor.fetchone()[0]
    print(f"   • التفاعلات: {int_count}")
    
    # 2. حذف البيانات التجريبية
    print("\n🗑️  حذف البيانات التجريبية...")
    
    # حذف مواعيد المستخدمين التجريبيين
    test_user_ids = [1, 777, 888, 999, 99999, 5200130110]
    
    for user_id in test_user_ids:
        cursor.execute('DELETE FROM appointments WHERE user_id = ?', (user_id,))
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"   ✅ حذف {deleted} موعد للمستخدم {user_id}")
    
    # حذف التذكيرات اليتيمة
    cursor.execute('''
        DELETE FROM reminders 
        WHERE appointment_id NOT IN (SELECT id FROM appointments)
    ''')
    orphan = cursor.rowcount
    if orphan > 0:
        print(f"   🧹 حذف {orphan} تذكير يتيم")
    
    # حذف التفاعلات التجريبية
    for user_id in test_user_ids:
        cursor.execute('DELETE FROM interactions WHERE user_id = ?', (user_id,))
    
    conn.commit()
    
    # 3. عرض الإحصائيات بعد الحذف
    print("\n📊 الإحصائيات بعد التنظيف:")
    
    cursor.execute('SELECT COUNT(*) FROM appointments')
    apt_count_after = cursor.fetchone()[0]
    print(f"   • المواعيد: {apt_count_after}")
    
    cursor.execute('SELECT COUNT(*) FROM reminders')
    rem_count_after = cursor.fetchone()[0]
    print(f"   • التذكيرات: {rem_count_after}")
    
    cursor.execute('SELECT COUNT(*) FROM reminders WHERE sent = 0')
    pending = cursor.fetchone()[0]
    print(f"   • التذكيرات المعلقة: {pending}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ تم التنظيف بنجاح!")
    print("="*60)

if __name__ == "__main__":
    cleanup_database()