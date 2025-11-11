# setup_database.py
import sqlite3
from datetime import datetime
import os

def create_database(db_path="agent_data.db"):
    """إنشاء قاعدة البيانات مع كل الجداول المطلوبة"""
    
    print(f"🗄️ إنشاء قاعدة البيانات: {db_path}")
    
    # حذف قاعدة البيانات القديمة إن وجدت (اختياري)
    # if os.path.exists(db_path):
    #     os.remove(db_path)
    #     print("  ➤ تم حذف قاعدة البيانات القديمة")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. جدول المواعيد
    print("  ➤ إنشاء جدول المواعيد...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            date_time TIMESTAMP NOT NULL,
            priority INTEGER DEFAULT 2,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. جدول التفاعلات
    print("  ➤ إنشاء جدول التفاعلات...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            intent TEXT,
            language TEXT,
            feedback INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. جدول التذكيرات
    print("  ➤ إنشاء جدول التذكيرات...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            reminder_time TIMESTAMP NOT NULL,
            custom_message TEXT,
            sent BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
        )
    ''')
    
    # 4. جدول المستخدمين
    print("  ➤ إنشاء جدول المستخدمين...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_preference TEXT DEFAULT 'ar',
            timezone TEXT DEFAULT 'UTC',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. جدول الإعدادات
    print("  ➤ إنشاء جدول الإعدادات...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            notification_enabled BOOLEAN DEFAULT 1,
            reminder_hours TEXT DEFAULT '24,1',
            working_hours_start INTEGER DEFAULT 9,
            working_hours_end INTEGER DEFAULT 18,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 6. جدول أرشيف التفاعلات
    print("  ➤ إنشاء جدول الأرشيف...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            bot_response TEXT,
            intent TEXT,
            language TEXT,
            feedback INTEGER,
            timestamp TIMESTAMP
        )
    ''')
    
    # إنشاء الفهارس لتحسين الأداء
    print("  ➤ إنشاء الفهارس...")
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_appointments_user ON appointments(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date_time)',
        'CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)',
        'CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)',
        'CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)',
        'CREATE INDEX IF NOT EXISTS idx_reminders_sent ON reminders(sent)'
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    
    # إضافة بيانات تجريبية (اختياري)
    add_sample = input("\n❓ هل تريد إضافة بيانات تجريبية؟ (y/n): ").lower()
    if add_sample == 'y':
        add_sample_data(cursor)
        conn.commit()
    
    conn.close()
    
    print("\n✅ تم إنشاء قاعدة البيانات بنجاح!")
    print(f"📊 الموقع: {os.path.abspath(db_path)}")
    
    # عرض معلومات الجداول
    show_database_info(db_path)


def add_sample_data(cursor):
    """إضافة بيانات تجريبية للاختبار"""
    print("\n  ➤ إضافة بيانات تجريبية...")
    
    # مستخدم تجريبي
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, first_name, language_preference)
        VALUES (1, 'testuser', 'مستخدم تجريبي', 'ar')
    ''')
    
    # مواعيد تجريبية
    sample_appointments = [
        (1, 'موعد مع الطبيب', 'فحص دوري', '2025-10-05 10:00:00', 2, 'pending'),
        (1, 'اجتماع العمل', 'مناقشة المشروع الجديد', '2025-10-06 14:00:00', 1, 'pending'),
        (1, 'دورة تدريبية', 'تعلم Python', '2025-10-08 09:00:00', 3, 'pending')
    ]
    
    cursor.executemany('''
        INSERT INTO appointments (user_id, title, description, date_time, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_appointments)
    
    # تفاعلات تجريبية
    sample_interactions = [
        (1, 'مرحبا', 'مرحباً! كيف يمكنني مساعدتك؟', 'greeting', 'ar', 5),
        (1, 'موعد غداً الساعة 10', 'تم إضافة الموعد بنجاح', 'add_appointment', 'ar', 4),
        (1, 'عرض مواعيدي', 'إليك قائمة بمواعيدك...', 'list_appointments', 'ar', 5),
        (1, 'Bonjour', 'Bonjour! Comment puis-je vous aider?', 'greeting', 'fr', 4),
        (1, 'Hello', 'Hello! How can I help you?', 'greeting', 'en', 5)
    ]
    
    cursor.executemany('''
        INSERT INTO interactions (user_id, user_message, bot_response, intent, language, feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_interactions)
    
    print("  ✓ تم إضافة 3 مواعيد تجريبية")
    print("  ✓ تم إضافة 5 تفاعلات تجريبية")


def show_database_info(db_path="agent_data.db"):
    """عرض معلومات عن قاعدة البيانات"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 معلومات قاعدة البيانات")
    print("="*60)
    
    # الجداول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📋 الجداول ({len(tables)}):")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  • {table_name}: {count} صف")
    
    conn.close()


def reset_database(db_path="agent_data.db"):
    """إعادة تعيين قاعدة البيانات (حذف كل البيانات)"""
    confirm = input("⚠️ هل أنت متأكد من حذف جميع البيانات؟ (yes/no): ")
    if confirm.lower() == 'yes':
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ تم حذف قاعدة البيانات القديمة")
        create_database(db_path)
    else:
        print("❌ تم إلغاء العملية")


def backup_database(db_path="agent_data.db"):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backup_{timestamp}_{db_path}"
    
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")


def verify_database(db_path="agent_data.db"):
    """التحقق من سلامة قاعدة البيانات"""
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من الجداول المطلوبة
        required_tables = ['appointments', 'interactions', 'reminders', 'users']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"⚠️ الجداول المفقودة: {', '.join(missing_tables)}")
            return False
        
        print("✅ قاعدة البيانات سليمة")
        
        # عرض الإحصائيات
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  • {table}: {count} سجل")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحقق: {e}")
        return False


def main():
    """القائمة الرئيسية"""
    print("="*60)
    print("🗄️ إدارة قاعدة البيانات - المساعد الذكي")
    print("="*60)
    print("\nالخيارات المتاحة:")
    print("1. إنشاء قاعدة بيانات جديدة")
    print("2. التحقق من قاعدة البيانات")
    print("3. عرض معلومات قاعدة البيانات")
    print("4. إنشاء نسخة احتياطية")
    print("5. إعادة تعيين قاعدة البيانات")
    print("6. خروج")
    
    while True:
        choice = input("\n👉 اختر رقم (1-6): ").strip()
        
        if choice == '1':
            db_name = input("اسم قاعدة البيانات (اضغط Enter للافتراضي: agent_data.db): ").strip()
            db_name = db_name if db_name else "agent_data.db"
            create_database(db_name)
            break
            
        elif choice == '2':
            db_name = input("اسم قاعدة البيانات (اضغط Enter للافتراضي: agent_data.db): ").strip()
            db_name = db_name if db_name else "agent_data.db"
            verify_database(db_name)
            
        elif choice == '3':
            db_name = input("اسم قاعدة البيانات (اضغط Enter للافتراضي: agent_data.db): ").strip()
            db_name = db_name if db_name else "agent_data.db"
            if os.path.exists(db_name):
                show_database_info(db_name)
            else:
                print("❌ قاعدة البيانات غير موجودة")
                
        elif choice == '4':
            db_name = input("اسم قاعدة البيانات (اضغط Enter للافتراضي: agent_data.db): ").strip()
            db_name = db_name if db_name else "agent_data.db"
            backup_database(db_name)
            
        elif choice == '5':
            db_name = input("اسم قاعدة البيانات (اضغط Enter للافتراضي: agent_data.db): ").strip()
            db_name = db_name if db_name else "agent_data.db"
            reset_database(db_name)
            break
            
        elif choice == '6':
            print("👋 وداعاً!")
            break
            
        else:
            print("❌ خيار غير صحيح، حاول مرة أخرى")


if __name__ == "__main__":
    main()