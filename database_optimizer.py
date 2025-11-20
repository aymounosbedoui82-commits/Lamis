# database_optimizer.py
"""
تحسين استعلامات قاعدة البيانات
✅ إضافة indexes ذكية
✅ تحسين الاستعلامات البطيئة
✅ VACUUM وصيانة دورية
"""

import sqlite3
from typing import List


class DatabaseOptimizer:
    """محسّن قاعدة البيانات"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def create_optimized_indexes(self):
        """إنشاء indexes محسّنة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        indexes = [
            # Index مركب للمواعيد حسب المستخدم والتاريخ
            '''CREATE INDEX IF NOT EXISTS idx_appointments_user_date 
               ON appointments(user_id, date_time)''',
            
            # Index للبحث في العنوان
            '''CREATE INDEX IF NOT EXISTS idx_appointments_title 
               ON appointments(title)''',
            
            # Index للأولوية
            '''CREATE INDEX IF NOT EXISTS idx_appointments_priority 
               ON appointments(user_id, priority)''',
            
            # Index للتذكيرات
            '''CREATE INDEX IF NOT EXISTS idx_reminders_time_sent 
               ON reminders(reminder_time, sent)''',
            
            # Index للتفاعلات
            '''CREATE INDEX IF NOT EXISTS idx_interactions_user_timestamp 
               ON interactions(user_id, timestamp DESC)''',
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created: {index_sql.split('idx_')[1].split(' ')[0]}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ جميع الـ indexes تم إنشاؤها بنجاح!")
    
    def analyze_query_performance(self):
        """تحليل أداء الاستعلامات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # تفعيل EXPLAIN QUERY PLAN
        test_queries = [
            "SELECT * FROM appointments WHERE user_id = 1",
            "SELECT * FROM appointments WHERE user_id = 1 AND date_time >= '2025-01-01'",
            "SELECT * FROM appointments WHERE user_id = 1 ORDER BY date_time",
        ]
        
        print("\n📊 تحليل الأداء:\n")
        for query in test_queries:
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            print(f"Query: {query[:50]}...")
            for row in plan:
                print(f"  {row}")
            print()
        
        conn.close()
    
    def vacuum_database(self):
        """تنظيف وضغط قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        
        print("🧹 جاري تنظيف قاعدة البيانات...")
        
        # الحصول على الحجم قبل
        cursor = conn.cursor()
        cursor.execute("PRAGMA page_count")
        pages_before = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        size_before = pages_before * page_size / (1024 * 1024)  # MB
        
        # VACUUM
        conn.execute("VACUUM")
        
        # الحصول على الحجم بعد
        cursor.execute("PRAGMA page_count")
        pages_after = cursor.fetchone()[0]
        size_after = pages_after * page_size / (1024 * 1024)  # MB
        
        saved = size_before - size_after
        
        print(f"  قبل: {size_before:.2f} MB")
        print(f"  بعد: {size_after:.2f} MB")
        print(f"  توفير: {saved:.2f} MB ({saved/size_before*100:.1f}%)")
        
        conn.close()
    
    def optimize_all(self):
        """تشغيل جميع التحسينات"""
        print("="*60)
        print("⚡ تحسين قاعدة البيانات")
        print("="*60)
        
        self.create_optimized_indexes()
        self.analyze_query_performance()
        self.vacuum_database()
        
        print("\n" + "="*60)
        print("✅ اكتمل التحسين!")
        print("="*60)


# تشغيل
if __name__ == "__main__":
    optimizer = DatabaseOptimizer()
    optimizer.optimize_all()