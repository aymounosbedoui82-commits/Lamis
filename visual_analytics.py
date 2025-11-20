# visual_analytics.py
"""
إحصائيات مرئية باستخدام matplotlib
✅ رسوم بيانية للمواعيد
✅ توزيع الأولويات
✅ نشاط الأسبوع/الشهر
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO

# استخدام backend غير تفاعلي
matplotlib.use('Agg')

# دعم العربية
plt.rcParams['font.family'] = 'DejaVu Sans'


class VisualAnalytics:
    """تحليلات مرئية للمواعيد"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def plot_weekly_activity(self, user_id: int) -> BytesIO:
        """رسم نشاط الأسبوع"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strftime('%w', date_time) as day, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY day
        ''', (user_id,))
        
        data = dict(cursor.fetchall())
        conn.close()
        
        # أيام الأسبوع
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        counts = [data.get(str(i), 0) for i in range(7)]
        
        # الرسم
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(days, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE'])
        
        ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
        ax.set_ylabel('Appointments', fontsize=12, fontweight='bold')
        ax.set_title('Weekly Activity', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # إضافة القيم فوق الأعمدة
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        # حفظ في memory
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def plot_priority_distribution(self, user_id: int) -> BytesIO:
        """توزيع الأولويات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY priority
        ''', (user_id,))
        
        data = dict(cursor.fetchall())
        conn.close()
        
        labels = ['Urgent', 'Medium', 'Low']
        sizes = [data.get(1, 0), data.get(2, 0), data.get(3, 0)]
        colors = ['#FF6B6B', '#FFA07A', '#98D8C8']
        explode = (0.1, 0, 0)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=explode,
            shadow=True
        )
        
        # تحسين النصوص
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Priority Distribution', fontsize=14, fontweight='bold', pad=20)
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def plot_monthly_trend(self, user_id: int, months: int = 6) -> BytesIO:
        """اتجاه المواعيد الشهرية"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT strftime('%Y-%m', date_time) as month, COUNT(*) as count
            FROM appointments
            WHERE user_id = ? AND date_time >= ?
            GROUP BY month
            ORDER BY month
        ''', (user_id, start_date))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            # رسم فارغ
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
        else:
            months_labels = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(months_labels, counts, marker='o', linewidth=2, 
                   markersize=8, color='#4ECDC4')
            ax.fill_between(range(len(counts)), counts, alpha=0.3, color='#4ECDC4')
            
            ax.set_xlabel('Month', fontsize=12, fontweight='bold')
            ax.set_ylabel('Appointments', fontsize=12, fontweight='bold')
            ax.set_title('Monthly Trend', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
        
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf


# إضافة في telegram_bot.py
async def charts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات المرئية"""
    from visual_analytics import VisualAnalytics
    
    user_id = update.effective_user.id
    analytics = VisualAnalytics()
    
    await update.message.reply_text("📊 جاري إنشاء الرسوم البيانية...")
    
    # رسم النشاط الأسبوعي
    weekly_chart = analytics.plot_weekly_activity(user_id)
    await update.message.reply_photo(
        photo=weekly_chart,
        caption="📅 **نشاطك الأسبوعي**"
    )
    
    # رسم الأولويات
    priority_chart = analytics.plot_priority_distribution(user_id)
    await update.message.reply_photo(
        photo=priority_chart,
        caption="🎯 **توزيع الأولويات**"
    )
    
    # رسم الاتجاه الشهري
    trend_chart = analytics.plot_monthly_trend(user_id)
    await update.message.reply_photo(
        photo=trend_chart,
        caption="📈 **الاتجاه الشهري**"
    )