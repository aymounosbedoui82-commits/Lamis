# calendar_export.py
"""
تصدير المواعيد إلى صيغ التقويم القياسية
✅ iCal (.ics) - متوافق مع Google Calendar, Apple Calendar, Outlook
✅ CSV للاستيراد في Excel
"""

import sqlite3
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class CalendarExporter:
    """تصدير المواعيد لصيغ التقويم"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def export_to_ical(self, user_id: int, filepath: str = None) -> str:
        """
        تصدير إلى iCal (.ics)
        متوافق مع: Google Calendar, Apple Calendar, Outlook, إلخ
        """
        if not filepath:
            filepath = f"calendar_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ics"
        
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
        
        # بناء ملف iCal
        ical = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Lamis Bot//Appointment Manager//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Lamis Bot - My Appointments",
            "X-WR-TIMEZONE:Africa/Tunis"
        ]
        
        for title, description, date_time_str, priority in appointments:
            # تحويل التاريخ لصيغة iCal
            date_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            dtstart = date_obj.strftime('%Y%m%dT%H%M%S')
            dtend = (date_obj.replace(hour=date_obj.hour + 1)).strftime('%Y%m%dT%H%M%S')
            
            # إنشاء UID فريد
            uid = f"{date_obj.strftime('%Y%m%d%H%M%S')}-{hash(title) % 10000}@lamisbot"
            
            # تحديد الأولوية
            priority_level = {1: 1, 2: 5, 3: 9}.get(priority, 5)
            
            event = [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{title}",
                f"DESCRIPTION:{description or 'موعد مهم'}",
                f"PRIORITY:{priority_level}",
                "STATUS:CONFIRMED",
                "TRANSP:OPAQUE",
                "END:VEVENT"
            ]
            
            ical.extend(event)
        
        ical.append("END:VCALENDAR")
        
        # حفظ الملف
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ical))
        
        return filepath
    
    def export_to_google_calendar_csv(self, user_id: int, filepath: str = None) -> str:
        """
        تصدير بصيغة CSV متوافقة مع Google Calendar
        """
        if not filepath:
            filepath = f"google_calendar_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        
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
        
        # رأس CSV لـ Google Calendar
        csv_lines = [
            "Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private"
        ]
        
        for title, description, date_time_str, priority in appointments:
            date_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            end_obj = date_obj.replace(hour=date_obj.hour + 1)
            
            start_date = date_obj.strftime('%m/%d/%Y')
            start_time = date_obj.strftime('%I:%M %p')
            end_date = end_obj.strftime('%m/%d/%Y')
            end_time = end_obj.strftime('%I:%M %p')
            
            # تنظيف النص
            title_clean = title.replace(',', ';').replace('"', "'")
            desc_clean = (description or '').replace(',', ';').replace('"', "'")
            
            csv_line = f'"{title_clean}",{start_date},{start_time},{end_date},{end_time},False,"{desc_clean}",,False'
            csv_lines.append(csv_line)
        
        # حفظ
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(csv_lines))
        
        return filepath


# إضافة في telegram_bot.py
async def export_calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تصدير التقويم"""
    from calendar_export import CalendarExporter
    
    user_id = update.effective_user.id
    exporter = CalendarExporter()
    
    # تصدير iCal
    ical_file = exporter.export_to_ical(user_id)
    
    # إرسال الملف
    with open(ical_file, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=f"my_calendar_{datetime.now().strftime('%Y%m%d')}.ics",
            caption="📅 **تقويمك بصيغة iCal**\n\n"
                   "يمكنك استيراده في:\n"
                   "• Google Calendar\n"
                   "• Apple Calendar\n"
                   "• Outlook\n"
                   "• أي تطبيق تقويم آخر"
        )
    
    # حذف الملف المؤقت
    Path(ical_file).unlink()