#!/usr/bin/env python3
# cleanup_test_data.py
"""
حذف البيانات التجريبية من قاعدة البيانات
"""

import sqlite3
import os

def cleanup_test_data():
    """حذف المواعيد والتذكيرات التجريبية"""
    print("="*60)
    print("🧹 تنظيف البيانات التجريبية")
    print("="*60)
    
    db_path = "agent_data.db"
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. عرض المستخدمين التجريبيين
    print("\n📋 البحث عن بيانات تجريبية...")
    
    test_user_ids = [99999, 777, 888]  # IDs المستخدمين التجريبيين
    
    for test_id in test_user_ids:
        # عدد المواعيد
        cursor.execute('SELECT COUNT(*) FROM appointments WHERE user_id = ?', (test_id,))
        apt_count = cursor.fetchone()[0]
        
        if apt_count > 0:
            print(f"\n   مستخدم تجريبي: {test_id}")
            print(f"   • المواعيد: {apt_count}")
            
            # عدد التذكيرات
            cursor.execute('''
                SELECT COUNT(*) FROM reminders r
                JOIN appointments a ON r.appointment_id = a.id
                WHERE a.user_id = ?
            ''', (test_id,))
            rem_count = cursor.fetchone()[0]
            print(f"   • التذكيرات: {rem_count}")
    
    # 2. السؤال عن الحذف
    print("\n" + "-"*60)
    confirm = input("هل تريد حذف البيانات التجريبية؟ (y/n): ").lower()
    
    if confirm != 'y':
        print("❌ تم الإلغاء")
        conn.close()
        return
    
    # 3. الحذف
    print("\n🗑️  جاري الحذف...")
    
    deleted_total = 0
    
    for test_id in test_user_ids:
        # حذف التذكيرات
        cursor.execute('''
            DELETE FROM reminders
            WHERE appointment_id IN (
                SELECT id FROM appointments WHERE user_id = ?
            )
        ''', (test_id,))
        
        rem_deleted = cursor.rowcount
        
        # حذف المواعيد
        cursor.execute('DELETE FROM appointments WHERE user_id = ?', (test_id,))
        apt_deleted = cursor.rowcount
        
        if apt_deleted > 0:
            print(f"   ✅ مستخدم {test_id}:")
            print(f"      - حذف {apt_deleted} موعد")
            print(f"      - حذف {rem_deleted} تذكير")
            deleted_total += apt_deleted
    
    # حذف التذكيرات اليتيمة (بدون مواعيد)
    cursor.execute('''
        DELETE FROM reminders
        WHERE appointment_id NOT IN (SELECT id FROM appointments)
    ''')
    orphan = cursor.rowcount
    
    if orphan > 0:
        print(f"   🧹 حذف {orphan} تذكير يتيم")
    
    conn.commit()
    
    # 4. النتيجة النهائية
    print("\n" + "="*60)
    print(f"✅ تم الحذف بنجاح!")
    print(f"   إجمالي المواعيد المحذوفة: {deleted_total}")
    print("="*60)
    
    # 5. عرض الإحصائيات الحالية
    print("\n📊 الإحصائيات الحالية:")
    
    cursor.execute('SELECT COUNT(*) FROM appointments')
    total_apt = cursor.fetchone()[0]
    print(f"   • المواعيد: {total_apt}")
    
    cursor.execute('SELECT COUNT(*) FROM reminders')
    total_rem = cursor.fetchone()[0]
    print(f"   • التذكيرات: {total_rem}")
    
    cursor.execute('SELECT COUNT(*) FROM reminders WHERE sent = 0')
    pending_rem = cursor.fetchone()[0]
    print(f"   • التذكيرات المعلقة: {pending_rem}")
    
    conn.close()


if __name__ == "__main__":
    cleanup_test_data()