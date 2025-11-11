# analytics_dashboard.py
"""
لوحة معلومات تحليلية متقدمة
✅ المرحلة 2: إحصائيات وتحليلات
✅ رؤى ذكية عن أنماط المواعيد
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """لوحة معلومات تحليلية شاملة"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def _execute_query(self, query: str, params: tuple = ()) -> List:
        """تنفيذ استعلام وإرجاع النتائج"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ==========================================
    # إحصائيات عامة
    # ==========================================
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """
        إحصائيات شاملة للمستخدم
        
        Returns:
            Dict: إحصائيات مفصلة
        """
        stats = {}
        
        # 1. إجمالي المواعيد
        result = self._execute_query(
            'SELECT COUNT(*) FROM appointments WHERE user_id = ?',
            (user_id,)
        )
        stats['total_appointments'] = result[0][0]
        
        # 2. المواعيد القادمة
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = self._execute_query(
            'SELECT COUNT(*) FROM appointments WHERE user_id = ? AND date_time >= ?',
            (user_id, now)
        )
        stats['upcoming_appointments'] = result[0][0]
        
        # 3. المواعيد المنتهية
        result = self._execute_query(
            'SELECT COUNT(*) FROM appointments WHERE user_id = ? AND date_time < ?',
            (user_id, now)
        )
        stats['past_appointments'] = result[0][0]
        
        # 4. المواعيد حسب الأولوية
        result = self._execute_query('''
            SELECT priority, COUNT(*) 
            FROM appointments 
            WHERE user_id = ?
            GROUP BY priority
        ''', (user_id,))
        
        stats['by_priority'] = {
            1: 0,  # عاجل
            2: 0,  # متوسط
            3: 0   # منخفض
        }
        for priority, count in result:
            stats['by_priority'][priority] = count
        
        # 5. معدل التفاعل
        result = self._execute_query(
            'SELECT COUNT(*) FROM interactions WHERE user_id = ?',
            (user_id,)
        )
        stats['total_interactions'] = result[0][0]
        
        # 6. التذكيرات المرسلة
        result = self._execute_query('''
            SELECT COUNT(*) FROM reminders r
            JOIN appointments a ON r.appointment_id = a.id
            WHERE a.user_id = ? AND r.sent = 1
        ''', (user_id,))
        stats['reminders_sent'] = result[0][0]
        
        # 7. أكثر يوم نشاطاً
        result = self._execute_query('''
            SELECT strftime('%w', date_time) as day, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY day
            ORDER BY count DESC
            LIMIT 1
        ''', (user_id,))
        
        if result:
            day_names = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
            stats['most_active_day'] = day_names[int(result[0][0])]
            stats['most_active_day_count'] = result[0][1]
        else:
            stats['most_active_day'] = 'N/A'
            stats['most_active_day_count'] = 0
        
        # 8. أكثر ساعة نشاطاً
        result = self._execute_query('''
            SELECT strftime('%H', date_time) as hour, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        ''', (user_id,))
        
        if result:
            stats['most_active_hour'] = f"{result[0][0]}:00"
            stats['most_active_hour_count'] = result[0][1]
        else:
            stats['most_active_hour'] = 'N/A'
            stats['most_active_hour_count'] = 0
        
        return stats
    
    # ==========================================
    # تحليل الأنماط
    # ==========================================
    
    def get_monthly_trend(self, user_id: int, months: int = 6) -> List[Tuple]:
        """
        اتجاه المواعيد الشهرية
        
        Args:
            user_id: معرف المستخدم
            months: عدد الأشهر للتحليل
            
        Returns:
            List[Tuple]: [(شهر, عدد المواعيد)]
        """
        start_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
        
        results = self._execute_query('''
            SELECT strftime('%Y-%m', date_time) as month, COUNT(*) as count
            FROM appointments
            WHERE user_id = ? AND date_time >= ?
            GROUP BY month
            ORDER BY month
        ''', (user_id, start_date))
        
        return results
    
    def get_hourly_distribution(self, user_id: int) -> Dict[int, int]:
        """
        توزيع المواعيد على مدار اليوم
        
        Returns:
            Dict: {hour: count}
        """
        results = self._execute_query('''
            SELECT strftime('%H', date_time) as hour, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY hour
        ''', (user_id,))
        
        distribution = defaultdict(int)
        for hour, count in results:
            distribution[int(hour)] = count
        
        return dict(distribution)
    
    def get_weekly_pattern(self, user_id: int) -> Dict[str, int]:
        """
        نمط المواعيد الأسبوعي
        
        Returns:
            Dict: {day_name: count}
        """
        results = self._execute_query('''
            SELECT strftime('%w', date_time) as day, COUNT(*) as count
            FROM appointments
            WHERE user_id = ?
            GROUP BY day
            ORDER BY day
        ''', (user_id,))
        
        day_names = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        
        pattern = {}
        for day, count in results:
            pattern[day_names[int(day)]] = count
        
        return pattern
    
    # ==========================================
    # تقرير شامل
    # ==========================================
    
    def generate_user_report(self, user_id: int, language: str = 'ar') -> str:
        """
        توليد تقرير تحليلي شامل للمستخدم
        
        Args:
            user_id: معرف المستخدم
            language: اللغة (ar/fr/en)
            
        Returns:
            str: تقرير منسق
        """
        stats = self.get_user_statistics(user_id)
        monthly_trend = self.get_monthly_trend(user_id)
        weekly_pattern = self.get_weekly_pattern(user_id)
        hourly_dist = self.get_hourly_distribution(user_id)
        
        # بناء التقرير
        lines = []
        
        # العنوان
        lines.append("="*70)
        if language == 'ar':
            lines.append("📊 تقرير التحليلات الشامل")
        elif language == 'fr':
            lines.append("📊 Rapport d'Analyse Complet")
        else:
            lines.append("📊 Comprehensive Analytics Report")
        lines.append("="*70)
        lines.append("")
        
        # الإحصائيات العامة
        if language == 'ar':
            lines.append("📈 الإحصائيات العامة:")
        elif language == 'fr':
            lines.append("📈 Statistiques Générales:")
        else:
            lines.append("📈 General Statistics:")
        
        lines.append(f"  • إجمالي المواعيد: {stats['total_appointments']:,}")
        lines.append(f"  • المواعيد القادمة: {stats['upcoming_appointments']:,}")
        lines.append(f"  • المواعيد المنتهية: {stats['past_appointments']:,}")
        lines.append(f"  • التفاعلات: {stats['total_interactions']:,}")
        lines.append(f"  • التذكيرات المرسلة: {stats['reminders_sent']:,}")
        lines.append("")
        
        # حسب الأولوية
        if language == 'ar':
            lines.append("🎯 المواعيد حسب الأولوية:")
        elif language == 'fr':
            lines.append("🎯 Rendez-vous par Priorité:")
        else:
            lines.append("🎯 Appointments by Priority:")
        
        priority_names = {
            'ar': {1: 'عاجل 🔴', 2: 'متوسط 🟡', 3: 'منخفض 🟢'},
            'fr': {1: 'Urgent 🔴', 2: 'Moyen 🟡', 3: 'Faible 🟢'},
            'en': {1: 'Urgent 🔴', 2: 'Medium 🟡', 3: 'Low 🟢'}
        }
        
        for priority in [1, 2, 3]:
            count = stats['by_priority'][priority]
            name = priority_names[language][priority]
            percentage = (count / stats['total_appointments'] * 100) if stats['total_appointments'] > 0 else 0
            lines.append(f"  {name}: {count} ({percentage:.1f}%)")
        
        lines.append("")
        
        # الأنماط
        if language == 'ar':
            lines.append("🔍 تحليل الأنماط:")
        elif language == 'fr':
            lines.append("🔍 Analyse des Modèles:")
        else:
            lines.append("🔍 Pattern Analysis:")
        
        lines.append(f"  • أكثر يوم نشاطاً: {stats['most_active_day']} ({stats['most_active_day_count']} مواعيد)")
        lines.append(f"  • أكثر ساعة نشاطاً: {stats['most_active_hour']} ({stats['most_active_hour_count']} مواعيد)")
        lines.append("")
        
        # النمط الأسبوعي
        if weekly_pattern:
            if language == 'ar':
                lines.append("📅 النمط الأسبوعي:")
            elif language == 'fr':
                lines.append("📅 Modèle Hebdomadaire:")
            else:
                lines.append("📅 Weekly Pattern:")
            
            max_count = max(weekly_pattern.values()) if weekly_pattern else 1
            
            for day, count in sorted(weekly_pattern.items(), key=lambda x: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'].index(x[0])):
                bar_length = int((count / max_count) * 20) if max_count > 0 else 0
                bar = "█" * bar_length
                lines.append(f"  {day:10s}: {bar} {count}")
            
            lines.append("")
        
        # الاتجاه الشهري
        if monthly_trend:
            if language == 'ar':
                lines.append("📈 الاتجاه الشهري (آخر 6 أشهر):")
            elif language == 'fr':
                lines.append("📈 Tendance Mensuelle (6 derniers mois):")
            else:
                lines.append("📈 Monthly Trend (Last 6 months):")
            
            max_count = max([count for _, count in monthly_trend]) if monthly_trend else 1
            
            for month, count in monthly_trend:
                bar_length = int((count / max_count) * 20) if max_count > 0 else 0
                bar = "█" * bar_length
                lines.append(f"  {month}: {bar} {count}")
            
            lines.append("")
        
        # التوزيع اليومي
        if hourly_dist:
            if language == 'ar':
                lines.append("🕐 التوزيع اليومي (أكثر 5 ساعات):")
            elif language == 'fr':
                lines.append("🕐 Distribution Journalière (Top 5):")
            else:
                lines.append("🕐 Daily Distribution (Top 5):")
            
            sorted_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for hour, count in sorted_hours:
                lines.append(f"  {hour:02d}:00 - {hour+1:02d}:00: {count} مواعيد")
            
            lines.append("")
        
        # الخاتمة
        lines.append("="*70)
        
        if language == 'ar':
            lines.append("💡 نصيحة: حاول توزيع مواعيدك بشكل متوازن على مدار الأسبوع!")
        elif language == 'fr':
            lines.append("💡 Conseil: Essayez de répartir vos RDV équitablement!")
        else:
            lines.append("💡 Tip: Try to distribute appointments evenly throughout the week!")
        
        lines.append("="*70)
        
        return "\n".join(lines)
    
    # ==========================================
    # رؤى ذكية
    # ==========================================
    
    def get_smart_insights(self, user_id: int) -> List[str]:
        """
        توليد رؤى ذكية بناءً على أنماط المستخدم
        
        Returns:
            List[str]: قائمة الرؤى
        """
        insights = []
        
        stats = self.get_user_statistics(user_id)
        weekly_pattern = self.get_weekly_pattern(user_id)
        hourly_dist = self.get_hourly_distribution(user_id)
        
        # 1. كثافة المواعيد
        if stats['upcoming_appointments'] > 10:
            insights.append(
                "⚠️ لديك عدد كبير من المواعيد القادمة. "
                "تأكد من ترك وقت كافٍ بين المواعيد!"
            )
        
        # 2. توزيع الأولويات
        urgent_ratio = (
            stats['by_priority'][1] / stats['total_appointments'] * 100
            if stats['total_appointments'] > 0 else 0
        )
        
        if urgent_ratio > 50:
            insights.append(
                "🔴 أكثر من نصف مواعيدك عاجلة. "
                "حاول تخطيط المهام بشكل أفضل لتجنب الضغط!"
            )
        
        # 3. النمط الأسبوعي
        if weekly_pattern:
            max_day = max(weekly_pattern, key=weekly_pattern.get)
            max_count = weekly_pattern[max_day]
            
            if max_count > sum(weekly_pattern.values()) * 0.4:
                insights.append(
                    f"📅 يوم {max_day} هو الأكثر ازدحاماً لديك. "
                    f"حاول توزيع بعض المواعيد على أيام أخرى!"
                )
        
        # 4. التوزيع اليومي
        if hourly_dist:
            morning_count = sum(hourly_dist.get(h, 0) for h in range(6, 12))
            afternoon_count = sum(hourly_dist.get(h, 0) for h in range(12, 18))
            evening_count = sum(hourly_dist.get(h, 0) for h in range(18, 24))
            
            total = morning_count + afternoon_count + evening_count
            
            if total > 0:
                if evening_count > total * 0.5:
                    insights.append(
                        "🌙 معظم مواعيدك مسائية. "
                        "تأكد من أخذ قسط كافٍ من الراحة!"
                    )
                elif morning_count > total * 0.6:
                    insights.append(
                        "🌅 أنت شخص صباحي! "
                        "استمر في الاستفادة من طاقتك الصباحية."
                    )
        
        # 5. معدل الاستخدام
        if stats['total_interactions'] > 100:
            insights.append(
                "🌟 أنت مستخدم نشط! "
                "شكراً لثقتك في بوت Lamis."
            )
        
        return insights


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار لوحة المعلومات التحليلية")
    print("="*70)
    
    # إنشاء Dashboard
    dashboard = AnalyticsDashboard("agent_data.db")
    
    # اختبار مع مستخدم وهمي
    user_id = 1
    
    print(f"\n👤 المستخدم: #{user_id}")
    print("-"*70)
    
    # 1. الإحصائيات العامة
    print("\n📊 الإحصائيات العامة:")
    stats = dashboard.get_user_statistics(user_id)
    
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # 2. التقرير الشامل
    print("\n📋 التقرير الشامل:")
    print("-"*70)
    report = dashboard.generate_user_report(user_id, language='ar')
    print(report)
    
    # 3. الرؤى الذكية
    print("\n💡 الرؤى الذكية:")
    print("-"*70)
    insights = dashboard.get_smart_insights(user_id)
    
    if insights:
        for insight in insights:
            print(f"  • {insight}")
    else:
        print("  لا توجد رؤى متاحة حالياً")
    
    print("\n" + "="*70)
    print("✅ الاختبار اكتمل!")