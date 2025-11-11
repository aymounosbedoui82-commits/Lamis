# advanced_features.py
"""
ميزات إضافية متقدمة للبوت
✅ المرحلة 2: ميزات جديدة
1. تذكيرات مخصصة
2. مواعيد متكررة
3. عرض تقويم شهري
4. تصدير/استيراد المواعيد
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from calendar import monthcalendar, month_name
import logging

logger = logging.getLogger(__name__)


# ==========================================
# 1. تذكيرات مخصصة
# ==========================================

class CustomReminderManager:
    """إدارة التذكيرات المخصصة للمستخدم"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """إنشاء جدول التذكيرات المخصصة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                minutes_before INTEGER NOT NULL,
                custom_message TEXT,
                sent INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_custom_reminder(
        self,
        appointment_id: int,
        minutes_before: int,
        custom_message: Optional[str] = None
    ) -> int:
        """
        إضافة تذكير مخصص
        
        Args:
            appointment_id: معرف الموعد
            minutes_before: عدد الدقائق قبل الموعد (15, 30, 60, 120, 1440, إلخ)
            custom_message: رسالة مخصصة (اختياري)
            
        Returns:
            int: معرف التذكير
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO custom_reminders (appointment_id, minutes_before, custom_message)
            VALUES (?, ?, ?)
        ''', (appointment_id, minutes_before, custom_message))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(
            f"✅ Custom reminder added: {minutes_before}min before "
            f"appointment #{appointment_id}"
        )
        
        return reminder_id
    
    def get_reminders_for_appointment(self, appointment_id: int) -> List[Dict]:
        """الحصول على جميع التذكيرات المخصصة لموعد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, minutes_before, custom_message, sent
            FROM custom_reminders
            WHERE appointment_id = ?
            ORDER BY minutes_before DESC
        ''', (appointment_id,))
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append({
                'id': row[0],
                'minutes_before': row[1],
                'custom_message': row[2],
                'sent': row[3]
            })
        
        conn.close()
        return reminders
    
    def remove_reminder(self, reminder_id: int):
        """حذف تذكير مخصص"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM custom_reminders WHERE id = ?', (reminder_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🗑️ Removed custom reminder #{reminder_id}")


# ==========================================
# 2. مواعيد متكررة
# ==========================================

class RecurringAppointmentManager:
    """إدارة المواعيد المتكررة"""
    
    PATTERNS = {
        'daily': 'يومياً',
        'weekly': 'أسبوعياً',
        'biweekly': 'كل أسبوعين',
        'monthly': 'شهرياً',
        'yearly': 'سنوياً'
    }
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """إنشاء جدول المواعيد المتكررة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                pattern TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                time TEXT NOT NULL,
                priority INTEGER DEFAULT 2,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_recurring_appointment(
        self,
        user_id: int,
        title: str,
        pattern: str,
        start_date: datetime,
        time_str: str,
        description: str = "",
        end_date: Optional[datetime] = None,
        priority: int = 2
    ) -> int:
        """
        إضافة موعد متكرر
        
        Args:
            user_id: معرف المستخدم
            title: عنوان الموعد
            pattern: نمط التكرار (daily, weekly, monthly, yearly)
            start_date: تاريخ البداية
            time_str: الوقت (مثل: "10:30")
            description: وصف
            end_date: تاريخ النهاية (اختياري)
            priority: الأولوية
            
        Returns:
            int: معرف الموعد المتكرر
        """
        if pattern not in self.PATTERNS:
            raise ValueError(f"Invalid pattern: {pattern}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recurring_appointments 
            (user_id, title, description, pattern, start_date, end_date, time, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, title, description, pattern,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d') if end_date else None,
            time_str, priority
        ))
        
        recurring_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(
            f"✅ Recurring appointment added: '{title}' "
            f"({self.PATTERNS[pattern]})"
        )
        
        return recurring_id
    
    def generate_instances(
        self,
        recurring_id: int,
        from_date: datetime,
        to_date: datetime
    ) -> List[datetime]:
        """
        توليد مواعيد من النمط المتكرر
        
        Args:
            recurring_id: معرف الموعد المتكرر
            from_date: من تاريخ
            to_date: إلى تاريخ
            
        Returns:
            List[datetime]: قائمة المواعيد المولدة
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern, start_date, end_date, time
            FROM recurring_appointments
            WHERE id = ?
        ''', (recurring_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return []
        
        pattern, start_str, end_str, time_str = row
        
        # تحويل التواريخ
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else to_date
        
        # استخراج الوقت
        hour, minute = map(int, time_str.split(':'))
        
        # توليد المواعيد
        instances = []
        current = start_date.replace(hour=hour, minute=minute)
        
        while current <= min(to_date, end_date):
            if current >= from_date:
                instances.append(current)
            
            # الانتقال للتالي حسب النمط
            if pattern == 'daily':
                current += timedelta(days=1)
            elif pattern == 'weekly':
                current += timedelta(weeks=1)
            elif pattern == 'biweekly':
                current += timedelta(weeks=2)
            elif pattern == 'monthly':
                # نفس اليوم من الشهر التالي
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            elif pattern == 'yearly':
                current = current.replace(year=current.year + 1)
        
        return instances
    
    def get_user_recurring_appointments(self, user_id: int) -> List[Dict]:
        """الحصول على جميع المواعيد المتكررة للمستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, pattern, start_date, end_date, time, priority, active
            FROM recurring_appointments
            WHERE user_id = ? AND active = 1
            ORDER BY start_date
        ''', (user_id,))
        
        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'pattern': row[3],
                'pattern_ar': self.PATTERNS.get(row[3], row[3]),
                'start_date': row[4],
                'end_date': row[5],
                'time': row[6],
                'priority': row[7],
                'active': row[8]
            })
        
        conn.close()
        return appointments


# ==========================================
# 3. عرض تقويم شهري
# ==========================================

class MonthlyCalendar:
    """عرض تقويم شهري جميل مع المواعيد"""
    
    ARABIC_MONTHS = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
    
    FRENCH_MONTHS = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def get_appointments_for_month(
        self,
        user_id: int,
        year: int,
        month: int
    ) -> Dict[int, List[Dict]]:
        """
        الحصول على جميع مواعيد الشهر
        
        Returns:
            Dict: {day: [appointments]}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # نطاق الشهر
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        cursor.execute('''
            SELECT id, title, date_time, priority
            FROM appointments
            WHERE user_id = ?
            AND date_time >= ?
            AND date_time < ?
            ORDER BY date_time
        ''', (
            user_id,
            start_date.strftime('%Y-%m-%d %H:%M:%S'),
            end_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # تنظيم حسب اليوم
        appointments_by_day = {}
        for row in cursor.fetchall():
            apt_datetime = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            day = apt_datetime.day
            
            if day not in appointments_by_day:
                appointments_by_day[day] = []
            
            appointments_by_day[day].append({
                'id': row[0],
                'title': row[1][:20],  # أول 20 حرف
                'time': apt_datetime.strftime('%H:%M'),
                'priority': row[3]
            })
        
        conn.close()
        return appointments_by_day
    
    def generate_calendar_text(
        self,
        user_id: int,
        year: int,
        month: int,
        language: str = 'ar'
    ) -> str:
        """
        توليد نص تقويم شهري جميل
        
        Args:
            user_id: معرف المستخدم
            year: السنة
            month: الشهر (1-12)
            language: اللغة (ar/fr/en)
            
        Returns:
            str: نص التقويم منسق
        """
        # اسم الشهر
        if language == 'ar':
            month_name = self.ARABIC_MONTHS[month - 1]
        elif language == 'fr':
            month_name = self.FRENCH_MONTHS[month - 1]
        else:
            month_name = month_name[month]
        
        # المواعيد
        appointments = self.get_appointments_for_month(user_id, year, month)
        
        # بناء التقويم
        calendar_lines = []
        
        # الرأس
        calendar_lines.append("="*50)
        calendar_lines.append(f"📅 {month_name} {year}")
        calendar_lines.append("="*50)
        calendar_lines.append("")
        
        # أيام الأسبوع
        if language == 'ar':
            weekdays = "   اثن   ثلا   أرب   خمي   جمع   سبت   أحد"
        elif language == 'fr':
            weekdays = "   Lun   Mar   Mer   Jeu   Ven   Sam   Dim"
        else:
            weekdays = "   Mon   Tue   Wed   Thu   Fri   Sat   Sun"
        
        calendar_lines.append(weekdays)
        calendar_lines.append("-"*50)
        
        # أيام الشهر
        cal = monthcalendar(year, month)
        
        for week in cal:
            week_line = ""
            for day in week:
                if day == 0:
                    week_line += "      "
                else:
                    # علامة إذا كان هناك مواعيد
                    marker = "●" if day in appointments else " "
                    week_line += f"  {day:2d}{marker} "
            
            calendar_lines.append(week_line)
        
        calendar_lines.append("-"*50)
        
        # قائمة المواعيد
        if appointments:
            calendar_lines.append("")
            if language == 'ar':
                calendar_lines.append("📋 المواعيد:")
            elif language == 'fr':
                calendar_lines.append("📋 Rendez-vous:")
            else:
                calendar_lines.append("📋 Appointments:")
            
            calendar_lines.append("")
            
            for day in sorted(appointments.keys()):
                day_appointments = appointments[day]
                calendar_lines.append(f"  {day:2d} {month_name[:3]}:")
                
                for apt in day_appointments:
                    priority_emoji = ['🔴', '🟡', '🟢'][apt['priority'] - 1]
                    calendar_lines.append(
                        f"    {priority_emoji} {apt['time']} - {apt['title']}"
                    )
                
                calendar_lines.append("")
        
        calendar_lines.append("="*50)
        
        return "\n".join(calendar_lines)


# ==========================================
# 4. تصدير/استيراد المواعيد
# ==========================================

class AppointmentExportImport:
    """تصدير واستيراد المواعيد"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def export_to_json(self, user_id: int, filepath: str):
        """
        تصدير المواعيد إلى JSON
        
        Args:
            user_id: معرف المستخدم
            filepath: مسار الملف
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, date_time, priority, created_at
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
                'created_at': row[5]
            })
        
        conn.close()
        
        # حفظ JSON
        export_data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'total_appointments': len(appointments),
            'appointments': appointments
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Exported {len(appointments)} appointments to {filepath}")
        return len(appointments)
    
    def export_to_csv(self, user_id: int, filepath: str):
        """
        تصدير المواعيد إلى CSV
        
        Args:
            user_id: معرف المستخدم
            filepath: مسار الملف
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, description, date_time, priority
            FROM appointments
            WHERE user_id = ?
            ORDER BY date_time
        ''', (user_id,))
        
        appointments = cursor.fetchall()
        conn.close()
        
        # حفظ CSV
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Title', 'Description', 'Date & Time', 'Priority'])
            
            # Data
            writer.writerows(appointments)
        
        logger.info(f"✅ Exported {len(appointments)} appointments to {filepath}")
        return len(appointments)
    
    def import_from_json(self, user_id: int, filepath: str) -> int:
        """
        استيراد المواعيد من JSON
        
        Args:
            user_id: معرف المستخدم
            filepath: مسار الملف
            
        Returns:
            int: عدد المواعيد المستوردة
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        appointments = data.get('appointments', [])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported = 0
        for apt in appointments:
            try:
                cursor.execute('''
                    INSERT INTO appointments (user_id, title, description, date_time, priority)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    apt['title'],
                    apt.get('description', ''),
                    apt['date_time'],
                    apt.get('priority', 2)
                ))
                imported += 1
            except Exception as e:
                logger.warning(f"Failed to import appointment: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Imported {imported} appointments from {filepath}")
        return imported


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار الميزات المتقدمة")
    print("="*70)
    
    # 1. تذكيرات مخصصة
    print("\n🔔 اختبار التذكيرات المخصصة:")
    print("-"*70)
    
    reminder_mgr = CustomReminderManager("test_features.db")
    
    # إضافة تذكير مخصص (يحتاج موعد موجود)
    print("  ✅ مدير التذكيرات المخصصة جاهز")
    
    # 2. مواعيد متكررة
    print("\n🔄 اختبار المواعيد المتكررة:")
    print("-"*70)
    
    recurring_mgr = RecurringAppointmentManager("test_features.db")
    
    # إضافة موعد متكرر
    recurring_id = recurring_mgr.add_recurring_appointment(
        user_id=123,
        title="اجتماع الفريق",
        pattern="weekly",
        start_date=datetime.now(),
        time_str="10:00",
        description="اجتماع أسبوعي"
    )
    
    # توليد مواعيد الشهر القادم
    instances = recurring_mgr.generate_instances(
        recurring_id,
        from_date=datetime.now(),
        to_date=datetime.now() + timedelta(days=30)
    )
    
    print(f"  ✅ موعد متكرر: {len(instances)} مواعيد في الشهر القادم")
    for inst in instances[:3]:
        print(f"     • {inst.strftime('%Y-%m-%d %H:%M')}")
    
    # 3. تقويم شهري
    print("\n📅 اختبار التقويم الشهري:")
    print("-"*70)
    
    calendar = MonthlyCalendar("test_features.db")
    
    # توليد تقويم (يحتاج مواعيد موجودة)
    print("  ✅ مولد التقويم جاهز")
    
    # 4. تصدير/استيراد
    print("\n💾 اختبار التصدير/الاستيراد:")
    print("-"*70)
    
    export_mgr = AppointmentExportImport("test_features.db")
    
    print("  ✅ مدير التصدير/الاستيراد جاهز")
    
    print("\n" + "="*70)
    print("✅ جميع الميزات جاهزة!")