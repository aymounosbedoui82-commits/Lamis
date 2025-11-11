#!/usr/bin/env python3
# recurring_appointments.py
"""
نظام المواعيد المتكررة - المرحلة 2
✅ يدعم: يومي، أسبوعي، شهري
"""

from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import logging

logger = logging.getLogger(__name__)


class RecurringAppointments:
    """
    نظام المواعيد المتكررة
    
    الأنماط المدعومة:
    - daily: كل يوم
    - weekly: كل أسبوع
    - monthly: كل شهر
    """
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """إنشاء جدول المواعيد المتكررة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recurring_appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TIME NOT NULL,
                    pattern TEXT NOT NULL,  -- daily, weekly, monthly
                    start_date DATE NOT NULL,
                    end_date DATE,
                    days_of_week TEXT,  -- للأسبوعي: "0,1,2" (الاثنين، الثلاثاء، الأربعاء)
                    day_of_month INTEGER,  -- للشهري: 15 (اليوم 15 من كل شهر)
                    priority INTEGER DEFAULT 2,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ جدول المواعيد المتكررة جاهز")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء جدول المواعيد المتكررة: {e}")
    
    def add_recurring_appointment(
        self,
        user_id: int,
        title: str,
        start_time: str,  # "HH:MM"
        pattern: str,  # "daily" | "weekly" | "monthly"
        start_date: Optional[str] = None,  # "YYYY-MM-DD"
        end_date: Optional[str] = None,
        description: str = "",
        days_of_week: Optional[List[int]] = None,  # [0, 1, 2] للأسبوعي
        day_of_month: Optional[int] = None,  # 15 للشهري
        priority: int = 2
    ) -> int:
        """
        إضافة موعد متكرر
        
        Args:
            user_id: معرف المستخدم
            title: عنوان الموعد
            start_time: الوقت "HH:MM"
            pattern: النمط (daily/weekly/monthly)
            start_date: تاريخ البداية (اختياري)
            end_date: تاريخ النهاية (اختياري)
            description: وصف
            days_of_week: أيام الأسبوع [0-6] للأسبوعي
            day_of_month: يوم الشهر [1-31] للشهري
            priority: الأولوية
            
        Returns:
            int: معرف الموعد المتكرر
        """
        try:
            # التاريخ الافتراضي = اليوم
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            
            # تحويل days_of_week إلى نص
            days_of_week_str = None
            if days_of_week:
                days_of_week_str = ','.join(map(str, days_of_week))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recurring_appointments (
                    user_id, title, description, start_time,
                    pattern, start_date, end_date,
                    days_of_week, day_of_month, priority
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, title, description, start_time,
                pattern, start_date, end_date,
                days_of_week_str, day_of_month, priority
            ))
            
            recurring_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ موعد متكرر مُضاف: #{recurring_id} ({pattern})")
            
            # إنشاء المواعيد للشهر القادم
            self.generate_appointments(recurring_id)
            
            return recurring_id
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة موعد متكرر: {e}")
            raise
    
    def generate_appointments(
        self,
        recurring_id: int,
        days_ahead: int = 30
    ) -> int:
        """
        توليد مواعيد من موعد متكرر
        
        Args:
            recurring_id: معرف الموعد المتكرر
            days_ahead: عدد الأيام المستقبلية
            
        Returns:
            int: عدد المواعيد المُنشأة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # الحصول على الموعد المتكرر
            cursor.execute('''
                SELECT 
                    user_id, title, description, start_time,
                    pattern, start_date, end_date,
                    days_of_week, day_of_month, priority
                FROM recurring_appointments
                WHERE id = ? AND active = 1
            ''', (recurring_id,))
            
            recurring = cursor.fetchone()
            
            if not recurring:
                logger.warning(f"⚠️ موعد متكرر غير موجود: #{recurring_id}")
                return 0
            
            (user_id, title, description, start_time,
             pattern, start_date, end_date,
             days_of_week_str, day_of_month, priority) = recurring
            
            # تحويل days_of_week من نص
            days_of_week = None
            if days_of_week_str:
                days_of_week = [int(d) for d in days_of_week_str.split(',')]
            
            # توليد التواريخ
            dates = self._generate_dates(
                pattern, start_date, end_date,
                days_ahead, days_of_week, day_of_month
            )
            
            # إضافة المواعيد
            created = 0
            for date in dates:
                datetime_str = f"{date} {start_time}:00"
                
                # فحص إذا كان الموعد موجود بالفعل
                cursor.execute('''
                    SELECT COUNT(*) FROM appointments
                    WHERE user_id = ? AND title = ? AND date_time = ?
                ''', (user_id, title, datetime_str))
                
                if cursor.fetchone()[0] == 0:
                    # إضافة الموعد
                    cursor.execute('''
                        INSERT INTO appointments (
                            user_id, title, description,
                            date_time, priority, status
                        ) VALUES (?, ?, ?, ?, ?, 'pending')
                    ''', (user_id, title, description, datetime_str, priority))
                    
                    created += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم إنشاء {created} موعد من #{recurring_id}")
            
            return created
            
        except Exception as e:
            logger.error(f"❌ خطأ في توليد المواعيد: {e}")
            return 0
    
    def _generate_dates(
        self,
        pattern: str,
        start_date: str,
        end_date: Optional[str],
        days_ahead: int,
        days_of_week: Optional[List[int]],
        day_of_month: Optional[int]
    ) -> List[str]:
        """توليد قائمة التواريخ حسب النمط"""
        dates = []
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else start + timedelta(days=days_ahead)
        
        current = start
        
        while current <= end:
            should_add = False
            
            if pattern == 'daily':
                # كل يوم
                should_add = True
                
            elif pattern == 'weekly' and days_of_week:
                # أيام محددة من الأسبوع
                if current.weekday() in days_of_week:
                    should_add = True
                    
            elif pattern == 'monthly' and day_of_month:
                # يوم محدد من الشهر
                if current.day == day_of_month:
                    should_add = True
            
            if should_add:
                dates.append(current.strftime('%Y-%m-%d'))
            
            current += timedelta(days=1)
        
        return dates
    
    def get_recurring_appointments(self, user_id: int) -> List[dict]:
        """الحصول على جميع المواعيد المتكررة للمستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM recurring_appointments
                WHERE user_id = ? AND active = 1
                ORDER BY created_at DESC
            ''', (user_id,))
            
            appointments = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return appointments
            
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على المواعيد المتكررة: {e}")
            return []
    
    def deactivate_recurring(self, recurring_id: int) -> bool:
        """إلغاء موعد متكرر"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE recurring_appointments
                SET active = 0
                WHERE id = ?
            ''', (recurring_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم إلغاء الموعد المتكرر #{recurring_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إلغاء الموعد المتكرر: {e}")
            return False


# ==========================================
# Telegram Bot Integration
# ==========================================

async def handle_recurring_appointment(update, context, agent):
    """
    معالج المواعيد المتكررة في البوت
    
    أمثلة:
    - "اجتماع كل ثلاثاء 10 صباحاً"
    - "رياضة يومياً 7 صباحاً"
    - "فاتورة كل شهر يوم 15"
    """
    message = update.message.text.lower()
    user_id = update.effective_user.id
    
    recurring = RecurringAppointments()
    
    # اكتشاف النمط
    pattern = None
    days_of_week = None
    day_of_month = None
    
    if 'يومي' in message or 'كل يوم' in message:
        pattern = 'daily'
    elif 'أسبوع' in message or 'كل' in message:
        pattern = 'weekly'
        # استخراج اليوم
        days_map = {
            'الاثنين': [0], 'الثلاثاء': [1], 'الأربعاء': [2],
            'الخميس': [3], 'الجمعة': [4], 'السبت': [5], 'الأحد': [6]
        }
        for day_name, day_nums in days_map.items():
            if day_name in message:
                days_of_week = day_nums
                break
    elif 'شهر' in message or 'monthly' in message:
        pattern = 'monthly'
        # استخراج اليوم من الشهر
        import re
        match = re.search(r'يوم (\d+)', message)
        if match:
            day_of_month = int(match.group(1))
        else:
            day_of_month = 1  # افتراضي: أول الشهر
    
    if not pattern:
        return False  # ليس موعد متكرر
    
    # استخراج العنوان والوقت (استخدام agent الموجود)
    # هنا نستخدم extract من intelligent_agent
    # للبساطة، سنستخدم قيم افتراضية
    
    title = message.split('كل')[0].strip() if 'كل' in message else "موعد متكرر"
    start_time = "09:00"  # افتراضي
    
    # إضافة الموعد المتكرر
    try:
        recurring_id = recurring.add_recurring_appointment(
            user_id=user_id,
            title=title,
            start_time=start_time,
            pattern=pattern,
            description=f"موعد متكرر {pattern}",
            days_of_week=days_of_week,
            day_of_month=day_of_month
        )
        
        pattern_ar = {
            'daily': 'يومي',
            'weekly': 'أسبوعي',
            'monthly': 'شهري'
        }
        
        await update.message.reply_text(
            f"✅ تم إضافة موعد متكرر! 🔄\n\n"
            f"📋 {title}\n"
            f"🔁 النمط: {pattern_ar[pattern]}\n"
            f"🕐 الوقت: {start_time}\n\n"
            f"💡 سيتم إنشاء المواعيد تلقائياً للشهر القادم!"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return False


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🔄 اختبار نظام المواعيد المتكررة")
    print("="*70)
    
    recurring = RecurringAppointments()
    
    # مثال: اجتماع كل ثلاثاء
    print("\n📝 إضافة: اجتماع كل ثلاثاء 10:00")
    recurring_id = recurring.add_recurring_appointment(
        user_id=12345,
        title="اجتماع الفريق",
        start_time="10:00",
        pattern="weekly",
        days_of_week=[1],  # الثلاثاء
        description="اجتماع أسبوعي"
    )
    
    print(f"✅ تم! ID: {recurring_id}")
    
    # عرض المواعيد المتكررة
    print("\n📋 المواعيد المتكررة:")
    appointments = recurring.get_recurring_appointments(12345)
    for apt in appointments:
        print(f"  • {apt['title']} ({apt['pattern']})")
    
    print("\n" + "="*70)
    print("✅ الاختبار اكتمل!")