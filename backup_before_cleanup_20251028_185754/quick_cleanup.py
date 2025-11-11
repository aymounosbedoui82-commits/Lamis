import sqlite3

conn = sqlite3.connect('agent_data.db')
cursor = conn.cursor()

# حذف المواعيد التجريبية
cursor.execute('DELETE FROM appointments WHERE user_id IN (777, 888, 999, 99999)')
print(f"✅ حذف {cursor.rowcount} موعد تجريبي")

# حذف التذكيرات اليتيمة
cursor.execute('DELETE FROM reminders WHERE appointment_id NOT IN (SELECT id FROM appointments)')
print(f"✅ حذف {cursor.rowcount} تذكير يتيم")

conn.commit()
conn.close()
print("✅ تم التنظيف!")