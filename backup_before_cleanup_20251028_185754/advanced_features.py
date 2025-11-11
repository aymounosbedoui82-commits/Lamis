# advanced_features.py
import sqlite3
import json
from datetime import datetime, timedelta
import csv
from typing import List, Dict
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

class DataExporter:
    """تصدير البيانات بصيغ مختلفة"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def export_appointments_csv(self, user_id: int, filename: str = "appointments.csv"):
        """تصدير المواعيد إلى CSV"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, description, date_time, priority, status, created_at
            FROM appointments
            WHERE user_id = ?
            ORDER BY date_time
        ''', (user_id,))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['العنوان', 'الوصف', 'التاريخ والوقت', 'الأولوية', 'الحالة', 'تاريخ الإنشاء'])
            writer.writerows(cursor.fetchall())
        
        conn.close()
        print(f"✅ تم تصدير المواعيد إلى {filename}")
    
    def export_appointments_json(self, user_id: int, filename: str = "appointments.json"):
        """تصدير المواعيد إلى JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, date_time, priority, status, created_at
            FROM appointments
            WHERE user_id = ?
            ORDER BY date_time
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'date_time': row[3],
                'priority': row[4],
                'status': row[5],
                'created_at': row[6]
            })
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(appointments, jsonfile, ensure_ascii=False, indent=2)
        
        conn.close()
        print(f"✅ تم تصدير المواعيد إلى {filename}")
    
    def import_appointments_json(self, user_id: int, filename: str):
        """استيراد المواعيد من JSON"""
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            appointments = json.load(jsonfile)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        for apt in appointments:
            cursor.execute('''
                INSERT INTO appointments (user_id, title, description, date_time, priority, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, apt['title'], apt['description'], apt['date_time'], 
                  apt['priority'], apt.get('status', 'pending')))
            imported_count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ تم استيراد {imported_count} موعد من {filename}")


class AnalyticsDashboard:
    """لوحة تحكم التحليلات والإحصائيات"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """إحصائيات المستخدم الشاملة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إجمالي المواعيد
        cursor.execute('SELECT COUNT(*) FROM appointments WHERE user_id = ?', (user_id,))
        total_appointments = cursor.fetchone()[0]
        
        # المواعيد القادمة
        cursor.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE user_id = ? AND date_time > datetime('now')
        ''', (user_id,))
        upcoming_appointments = cursor.fetchone()[0]
        
        # المواعيد المنجزة
        cursor.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,))
        completed_appointments = cursor.fetchone()[0]
        
        # المواعيد الملغاة
        cursor.execute('''
            SELECT COUNT(*) FROM appointments 
            WHERE user_id = ? AND status = 'cancelled'
        ''', (user_id,))
        cancelled_appointments = cursor.fetchone()[0]
        
        # إجمالي التفاعلات
        cursor.execute('SELECT COUNT(*) FROM interactions WHERE user_id = ?', (user_id,))
        total_interactions = cursor.fetchone()[0]
        
        # اللغات المستخدمة
        cursor.execute('''
            SELECT language, COUNT(*) as count
            FROM interactions
            WHERE user_id = ?
            GROUP BY language
        ''', (user_id,))
        languages = {row[0]: row[1] for row in cursor.fetchall()}
        
        # النوايا الأكثر استخداماً
        cursor.execute('''
            SELECT intent, COUNT(*) as count
            FROM interactions
            WHERE user_id = ? AND intent IS NOT NULL
            GROUP BY intent
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id,))
        top_intents = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'total_interactions': total_interactions,
            'languages_used': languages,
            'top_intents': top_intents,
            'completion_rate': round((completed_appointments / total_appointments * 100), 2) if total_appointments > 0 else 0
        }
    
    def generate_weekly_report(self, user_id: int) -> str:
        """تقرير أسبوعي"""
        stats = self.get_user_statistics(user_id)
        
        report = f"""
📊 **التقرير الأسبوعي**
{'='*50}

📅 **المواعيد:**
  • إجمالي المواعيد: {stats['total_appointments']}
  • المواعيد القادمة: {stats['upcoming_appointments']}
  • المنجزة: {stats['completed_appointments']}
  • الملغاة: {stats['cancelled_appointments']}
  • معدل الإنجاز: {stats['completion_rate']}%

💬 **التفاعلات:**
  • إجمالي التفاعلات: {stats['total_interactions']}

🌍 **اللغات المستخدمة:**
"""
        for lang, count in stats['languages_used'].items():
            lang_name = {'ar': 'العربية', 'en': 'English', 'fr': 'Français'}.get(lang, lang)
            report += f"  • {lang_name}: {count} تفاعل\n"
        
        report += "\n🎯 **الأنشطة الأكثر شيوعاً:**\n"
        for intent, count in stats['top_intents'].items():
            report += f"  • {intent}: {count} مرة\n"
        
        return report
    
    def get_appointment_trends(self, user_id: int, days: int = 30) -> Dict:
        """تحليل اتجاهات المواعيد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT DATE(date_time) as day, COUNT(*) as count
            FROM appointments
            WHERE user_id = ? AND date_time >= ?
            GROUP BY DATE(date_time)
            ORDER BY day
        ''', (user_id, start_date))
        
        daily_counts = {}
        for row in cursor.fetchall():
            daily_counts[row[0]] = row[1]
        
        # أيام الأسبوع الأكثر ازدحاماً
        cursor.execute('''
            SELECT strftime('%w', date_time) as weekday, COUNT(*) as count
            FROM appointments
            WHERE user_id = ? AND date_time >= ?
            GROUP BY weekday
            ORDER BY count DESC
        ''', (user_id, start_date))
        
        weekday_names = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        busiest_days = {}
        for row in cursor.fetchall():
            weekday_idx = int(row[0])
            busiest_days[weekday_names[weekday_idx]] = row[1]
        
        # الأوقات المفضلة
        cursor.execute('''
            SELECT strftime('%H', date_time) as hour, COUNT(*) as count
            FROM appointments
            WHERE user_id = ? AND date_time >= ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id, start_date))
        
        preferred_hours = {f"{row[0]}:00": row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'daily_counts': daily_counts,
            'busiest_days': busiest_days,
            'preferred_hours': preferred_hours
        }
    
    def visualize_statistics(self, user_id: int, save_path: str = "stats.png"):
        """إنشاء رسم بياني للإحصائيات"""
        try:
            import matplotlib.pyplot as plt
            plt.rcParams['font.family'] = 'Arial'
            
            stats = self.get_user_statistics(user_id)
            trends = self.get_appointment_trends(user_id)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('لوحة تحكم الإحصائيات', fontsize=16, fontweight='bold')
            
            # 1. حالة المواعيد (Pie Chart)
            ax1 = axes[0, 0]
            statuses = ['القادمة', 'المنجزة', 'الملغاة']
            counts = [
                stats['upcoming_appointments'],
                stats['completed_appointments'],
                stats['cancelled_appointments']
            ]
            colors = ['#4CAF50', '#2196F3', '#F44336']
            ax1.pie(counts, labels=statuses, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('توزيع حالة المواعيد')
            
            # 2. اللغات المستخدمة (Bar Chart)
            ax2 = axes[0, 1]
            languages = list(stats['languages_used'].keys())
            lang_counts = list(stats['languages_used'].values())
            lang_names = [{'ar': 'العربية', 'en': 'English', 'fr': 'Français'}.get(l, l) for l in languages]
            ax2.bar(lang_names, lang_counts, color=['#FF5722', '#9C27B0', '#00BCD4'])
            ax2.set_title('اللغات المستخدمة')
            ax2.set_ylabel('عدد التفاعلات')
            
            # 3. أيام الأسبوع الأكثر ازدحاماً (Bar Chart)
            ax3 = axes[1, 0]
            days = list(trends['busiest_days'].keys())
            day_counts = list(trends['busiest_days'].values())
            ax3.barh(days, day_counts, color='#009688')
            ax3.set_title('أيام الأسبوع الأكثر ازدحاماً')
            ax3.set_xlabel('عدد المواعيد')
            
            # 4. الأوقات المفضلة (Bar Chart)
            ax4 = axes[1, 1]
            hours = list(trends['preferred_hours'].keys())
            hour_counts = list(trends['preferred_hours'].values())
            ax4.bar(hours, hour_counts, color='#FF9800')
            ax4.set_title('الأوقات المفضلة للمواعيد')
            ax4.set_ylabel('عدد المواعيد')
            ax4.set_xlabel('الساعة')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ تم حفظ الرسم البياني في {save_path}")
            plt.close()
            
        except ImportError:
            print("❌ مكتبة matplotlib غير مثبتة. استخدم: pip install matplotlib")
        except Exception as e:
            print(f"❌ خطأ في إنشاء الرسم البياني: {e}")


class SmartReminder:
    """نظام تذكيرات ذكي متقدم"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def create_custom_reminder(self, appointment_id: int, reminder_time: datetime, message: str = None):
        """إنشاء تذكير مخصص"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (appointment_id, reminder_time, custom_message)
            VALUES (?, ?, ?)
        ''', (appointment_id, reminder_time, message))
        
        conn.commit()
        conn.close()
        print(f"✅ تم إنشاء تذكير مخصص للموعد #{appointment_id}")
    
    def get_smart_reminder_suggestions(self, user_id: int) -> List[Dict]:
        """اقتراحات ذكية للتذكيرات بناءً على سلوك المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # تحليل أوقات التفاعل المفضلة
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM interactions
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 3
        ''', (user_id,))
        
        preferred_hours = [int(row[0]) for row in cursor.fetchall()]
        
        # المواعيد القادمة بدون تذكيرات كافية
        cursor.execute('''
            SELECT a.id, a.title, a.date_time, COUNT(r.id) as reminder_count
            FROM appointments a
            LEFT JOIN reminders r ON a.id = r.appointment_id
            WHERE a.user_id = ? AND a.date_time > datetime('now')
            GROUP BY a.id
            HAVING reminder_count < 2
        ''', (user_id,))
        
        suggestions = []
        for row in cursor.fetchall():
            apt_id, title, apt_time, reminder_count = row
            apt_datetime = datetime.strptime(apt_time, '%Y-%m-%d %H:%M:%S')
            
            # اقتراح تذكيرات في الأوقات المفضلة
            for hour in preferred_hours:
                suggested_time = apt_datetime - timedelta(days=1)
                suggested_time = suggested_time.replace(hour=hour, minute=0)
                
                if suggested_time > datetime.now():
                    suggestions.append({
                        'appointment_id': apt_id,
                        'appointment_title': title,
                        'suggested_reminder_time': suggested_time,
                        'reason': f'وقت التفاعل المفضل ({hour}:00)'
                    })
        
        conn.close()
        return suggestions[:5]  # أفضل 5 اقتراحات


class ConversationAnalyzer:
    """تحليل المحادثات واستخراج الأنماط"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def analyze_conversation_patterns(self, user_id: int) -> Dict:
        """تحليل أنماط المحادثة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # أكثر الكلمات استخداماً
        cursor.execute('''
            SELECT user_message FROM interactions WHERE user_id = ?
        ''', (user_id,))
        
        all_messages = ' '.join([row[0].lower() for row in cursor.fetchall()])
        words = all_messages.split()
        
        # إزالة كلمات التوقف
        stopwords = set(['في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 
                        'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
                        'le', 'la', 'les', 'de', 'du', 'à', 'au'])
        
        words = [w for w in words if w not in stopwords and len(w) > 2]
        word_freq = Counter(words).most_common(10)
        
        # أوقات الذروة للتفاعل
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM interactions
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY count DESC
        ''', (user_id,))
        
        peak_hours = {row[0]: row[1] for row in cursor.fetchall()}
        
        # معدل الرضا
        cursor.execute('''
            SELECT AVG(feedback), COUNT(CASE WHEN feedback >= 4 THEN 1 END) * 100.0 / COUNT(*)
            FROM interactions
            WHERE user_id = ? AND feedback > 0
        ''', (user_id,))
        
        result = cursor.fetchone()
        avg_satisfaction = round(result[0], 2) if result[0] else 0
        positive_rate = round(result[1], 2) if result[1] else 0
        
        conn.close()
        
        return {
            'most_common_words': word_freq,
            'peak_interaction_hours': peak_hours,
            'average_satisfaction': avg_satisfaction,
            'positive_feedback_rate': positive_rate
        }
    
    def generate_insights_report(self, user_id: int) -> str:
        """تقرير رؤى ذكية"""
        patterns = self.analyze_conversation_patterns(user_id)
        
        report = f"""
🔍 **تقرير الرؤى الذكية**
{'='*60}

📊 **تحليل المحادثات:**
  • معدل الرضا: {patterns['average_satisfaction']}/5
  • نسبة التقييمات الإيجابية: {patterns['positive_feedback_rate']}%

💡 **الكلمات الأكثر استخداماً:**
"""
        for word, count in patterns['most_common_words'][:5]:
            report += f"  • {word}: {count} مرة\n"
        
        report += "\n⏰ **أوقات الذروة للتفاعل:**\n"
        sorted_hours = sorted(patterns['peak_interaction_hours'].items(), 
                            key=lambda x: x[1], reverse=True)[:3]
        for hour, count in sorted_hours:
            report += f"  • الساعة {hour}:00 - {count} تفاعل\n"
        
        # توصيات ذكية
        report += "\n💭 **توصيات ذكية:**\n"
        if patterns['average_satisfaction'] < 3:
            report += "  ⚠️ معدل الرضا منخفض، يُنصح بمراجعة جودة الردود\n"
        if patterns['positive_feedback_rate'] > 80:
            report += "  ✅ أداء ممتاز! استمر على نفس المستوى\n"
        
        return report


class AutomationScheduler:
    """جدولة المهام التلقائية"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def cleanup_old_appointments(self, days_old: int = 90):
        """تنظيف المواعيد القديمة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            DELETE FROM appointments
            WHERE date_time < ? AND status IN ('completed', 'cancelled')
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🗑️ تم حذف {deleted_count} موعد قديم")
        return deleted_count
    
    def archive_old_interactions(self, days_old: int = 180):
        """أرشفة التفاعلات القديمة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
        
        # إنشاء جدول الأرشيف إن لم يكن موجوداً
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions_archive AS
            SELECT * FROM interactions WHERE 1=0
        ''')
        
        # نقل البيانات القديمة للأرشيف
        cursor.execute('''
            INSERT INTO interactions_archive
            SELECT * FROM interactions
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        archived_count = cursor.rowcount
        
        # حذف من الجدول الرئيسي
        cursor.execute('''
            DELETE FROM interactions WHERE timestamp < ?
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()
        
        print(f"📦 تم أرشفة {archived_count} تفاعل")
        return archived_count
    
    def optimize_database(self):
        """تحسين أداء قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إنشاء فهارس لتسريع الاستعلامات
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_appointments_user_date ON appointments(user_id, date_time)',
            'CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)',
            'CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_interactions_intent ON interactions(intent)',
            'CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time, sent)'
        ]
        
        for index_query in indexes:
            cursor.execute(index_query)
        
        # تحليل قاعدة البيانات
        cursor.execute('ANALYZE')
        
        # ضغط قاعدة البيانات
        cursor.execute('VACUUM')
        
        conn.commit()
        conn.close()
        
        print("⚡ تم تحسين قاعدة البيانات بنجاح")


class NotificationManager:
    """إدارة الإشعارات المتقدمة"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def get_daily_summary(self, user_id: int) -> str:
        """ملخص يومي للمستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # مواعيد اليوم
        cursor.execute('''
            SELECT COUNT(*) FROM appointments
            WHERE user_id = ? AND DATE(date_time) = ?
        ''', (user_id, today))
        today_count = cursor.fetchone()[0]
        
        # المواعيد القادمة
        cursor.execute('''
            SELECT title, date_time FROM appointments
            WHERE user_id = ? AND DATE(date_time) = ?
            ORDER BY date_time
        ''', (user_id, today))
        
        appointments = cursor.fetchall()
        
        conn.close()
        
        summary = f"🌅 **صباح الخير!**\n\n"
        summary += f"📅 **ملخص يوم {datetime.now().strftime('%d/%m/%Y')}**\n\n"
        
        if today_count == 0:
            summary += "✨ لا توجد مواعيد لهذا اليوم. استمتع بيومك!\n"
        else:
            summary += f"لديك {today_count} موعد(مواعيد) اليوم:\n\n"
            for apt in appointments:
                time = datetime.strptime(apt[1], '%Y-%m-%d %H:%M:%S')
                summary += f"🕐 {time.strftime('%H:%M')} - {apt[0]}\n"
        
        return summary
    
    def get_weekly_preview(self, user_id: int) -> str:
        """معاينة الأسبوع القادم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now()
        week_end = today + timedelta(days=7)
        
        cursor.execute('''
            SELECT DATE(date_time), COUNT(*) FROM appointments
            WHERE user_id = ? AND date_time BETWEEN ? AND ?
            GROUP BY DATE(date_time)
            ORDER BY date_time
        ''', (user_id, today.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
        
        daily_counts = cursor.fetchall()
        conn.close()
        
        preview = f"📅 **نظرة على الأسبوع القادم**\n\n"
        
        if not daily_counts:
            preview += "✨ أسبوع هادئ بدون مواعيد!\n"
        else:
            for date_str, count in daily_counts:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'][date.weekday()]
                preview += f"• {day_name} {date.strftime('%d/%m')}: {count} موعد\n"
        
        return preview


# مثال على الاستخدام الشامل
if __name__ == "__main__":
    print("="*60)
    print("🚀 الميزات المتقدمة للمساعد الذكي")
    print("="*60)
    
    user_id = 1
    
    # 1. تصدير البيانات
    print("\n📤 تصدير البيانات...")
    exporter = DataExporter()
    exporter.export_appointments_json(user_id, "my_appointments.json")
    exporter.export_appointments_csv(user_id, "my_appointments.csv")
    
    # 2. لوحة التحليلات
    print("\n📊 تحليل البيانات...")
    analytics = AnalyticsDashboard()
    stats = analytics.get_user_statistics(user_id)
    print(f"إجمالي المواعيد: {stats['total_appointments']}")
    print(f"معدل الإنجاز: {stats['completion_rate']}%")
    
    # 3. التقرير الأسبوعي
    print("\n📋 التقرير الأسبوعي:")
    weekly_report = analytics.generate_weekly_report(user_id)
    print(weekly_report)
    
    # 4. التذكيرات الذكية
    print("\n🔔 اقتراحات التذكيرات الذكية:")
    smart_reminder = SmartReminder()
    suggestions = smart_reminder.get_smart_reminder_suggestions(user_id)
    for s in suggestions[:3]:
        print(f"  • {s['appointment_title']}: {s['suggested_reminder_time']}")
    
    # 5. تحليل المحادثات
    print("\n💬 تحليل المحادثات:")
    analyzer = ConversationAnalyzer()
    insights = analyzer.generate_insights_report(user_id)
    print(insights)
    
    # 6. الصيانة التلقائية
    print("\n🔧 صيانة قاعدة البيانات:")
    scheduler = AutomationScheduler()
    scheduler.optimize_database()
    
    # 7. الملخص اليومي
    print("\n☀️ الملخص اليومي:")
    notifier = NotificationManager()
    daily_summary = notifier.get_daily_summary(user_id)
    print(daily_summary)
    
    # 8. الرسومات البيانية
    print("\n📈 إنشاء الرسومات البيانية...")
    analytics.visualize_statistics(user_id, "user_statistics.png")
    
    print("\n" + "="*60)
    print("✅ تم تشغيل جميع الميزات المتقدمة بنجاح!")
    print("="*60)