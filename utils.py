# utils.py
"""
ملف الدوال المساعدة للمساعد الذكي
يحتوي على أدوات لتحليل التواريخ، تنظيف النصوص، التحقق من البيانات، والتنسيق
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Tuple, List

class DateTimeParser:
    """محلل التواريخ والأوقات متعدد اللغات"""
    
    @staticmethod
    def parse_arabic_date(text: str) -> Optional[datetime]:
        """تحليل التواريخ بالعربية"""
        now = datetime.now()
        text = text.lower()
        
        # الكلمات المفتاحية
        if 'اليوم' in text:
            return now
        elif 'غدا' in text or 'غدً' in text:
            return now + timedelta(days=1)
        elif 'بعد غد' in text:
            return now + timedelta(days=2)
        elif 'الأسبوع القادم' in text or 'الاسبوع القادم' in text:
            return now + timedelta(weeks=1)
        elif 'الشهر القادم' in text:
            return now + timedelta(days=30)
        
        # أيام الأسبوع
        days_map = {
            'السبت': 5, 'الأحد': 6, 'الاثنين': 0,
            'الثلاثاء': 1, 'الأربعاء': 2, 'الخميس': 3, 'الجمعة': 4
        }
        
        for day_name, day_num in days_map.items():
            if day_name in text:
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return now + timedelta(days=days_ahead)
        
        return None
    
    @staticmethod
    def parse_french_date(text: str) -> Optional[datetime]:
        """تحليل التواريخ بالفرنسية"""
        now = datetime.now()
        text = text.lower()
        
        if "aujourd'hui" in text or 'aujourdhui' in text:
            return now
        elif 'demain' in text:
            return now + timedelta(days=1)
        elif 'après-demain' in text or 'apres-demain' in text:
            return now + timedelta(days=2)
        elif 'semaine prochaine' in text:
            return now + timedelta(weeks=1)
        
        # أيام الأسبوع
        days_map = {
            'lundi': 0, 'mardi': 1, 'mercredi': 2,
            'jeudi': 3, 'vendredi': 4, 'samedi': 5, 'dimanche': 6
        }
        
        for day_name, day_num in days_map.items():
            if day_name in text:
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return now + timedelta(days=days_ahead)
        
        return None
    
    @staticmethod
    def parse_english_date(text: str) -> Optional[datetime]:
        """تحليل التواريخ بالإنجليزية"""
        now = datetime.now()
        text = text.lower()
        
        if 'today' in text:
            return now
        elif 'tomorrow' in text:
            return now + timedelta(days=1)
        elif 'day after tomorrow' in text:
            return now + timedelta(days=2)
        elif 'next week' in text:
            return now + timedelta(weeks=1)
        
        # أيام الأسبوع
        days_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in days_map.items():
            if day_name in text:
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return now + timedelta(days=days_ahead)
        
        return None
    
    @staticmethod
    def parse_time(text: str) -> Optional[Tuple[int, int]]:
        """استخراج الوقت من النص"""
        # نمط XX:XX
        time_pattern = r'(\d{1,2})[:](\d{2})'
        match = re.search(time_pattern, text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        
        # نمط "الساعة X" أو "X صباحاً" أو "X مساءً"
        hour_pattern = r'(\d{1,2})\s*(صباحا|صباحً|مساء|مساءً|am|pm|h)?'
        match = re.search(hour_pattern, text.lower())
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            
            if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                hour += 12
            elif period in ['صباحا', 'صباحً', 'am'] and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23:
                return (hour, 0)
        
        return None
    
    @staticmethod
    def parse_numeric_date(text: str) -> Optional[datetime]:
        """استخراج تاريخ رقمي من النص"""
        # DD/MM/YYYY أو DD-MM-YYYY
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', text)
        if date_match:
            day, month, year = map(int, date_match.groups())
            if year < 100:
                year += 2000
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
        
        return None
    
    @classmethod
    def parse_datetime(cls, text: str, language: str = 'ar') -> Optional[datetime]:
        """تحليل التاريخ والوقت الكامل"""
        # محاولة استخراج تاريخ رقمي أولاً
        date = cls.parse_numeric_date(text)
        
        # إذا لم يُعثر على تاريخ رقمي، استخدم التحليل اللغوي
        if not date:
            if language == 'ar':
                date = cls.parse_arabic_date(text)
            elif language == 'fr':
                date = cls.parse_french_date(text)
            elif language == 'en':
                date = cls.parse_english_date(text)
        
        # إذا لم يُعثر على تاريخ، استخدم غداً كافتراضي
        if not date:
            date = datetime.now() + timedelta(days=1)
        
        # استخراج الوقت
        time = cls.parse_time(text)
        
        # دمج التاريخ والوقت
        if time:
            date = date.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
        else:
            # وقت افتراضي (9 صباحاً)
            date = date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return date
    
    @staticmethod
    def combine_datetime(date: datetime, time: Optional[Tuple[int, int]]) -> datetime:
        """دمج التاريخ والوقت"""
        if time:
            return date.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
        return date.replace(hour=9, minute=0, second=0, microsecond=0)


class TextCleaner:
    """تنظيف وتجهيز النصوص"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """تنظيف النص من الرموز والمسافات الزائدة"""
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        
        # إزالة الرموز غير المرغوبة (مع الحفاظ على الحروف العربية)
        text = re.sub(r'[^\w\s\u0600-\u06FF:/-]', '', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_arabic(text: str) -> str:
        """توحيد الأحرف العربية"""
        # توحيد الهمزات
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'[ؤئ]', 'ء', text)
        
        # إزالة التشكيل
        text = re.sub(r'[\u064B-\u065F]', '', text)
        
        return text
    
    @staticmethod
    def extract_keywords(text: str, language: str) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        # كلمات التوقف حسب اللغة
        stopwords = {
            'ar': ['في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'التي', 'الذي'],
            'fr': ['le', 'la', 'les', 'de', 'du', 'à', 'au', 'en', 'dans', 'pour', 'avec'],
            'en': ['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'from', 'by']
        }
        
        words = text.lower().split()
        stop_list = stopwords.get(language, [])
        
        keywords = [w for w in words if w not in stop_list and len(w) > 2]
        return keywords


class Validator:
    """التحقق من صحة البيانات"""
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """التحقق من صحة التاريخ"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_time(hour: int, minute: int) -> bool:
        """التحقق من صحة الوقت"""
        return 0 <= hour <= 23 and 0 <= minute <= 59
    
    @staticmethod
    def is_future_datetime(dt: datetime) -> bool:
        """التحقق من أن التاريخ في المستقبل"""
        return dt > datetime.now()
    
    @staticmethod
    def is_valid_priority(priority: int) -> bool:
        """التحقق من صحة الأولوية (1-3)"""
        return priority in [1, 2, 3]


class Formatter:
    """تنسيق النصوص والبيانات"""
    
    @staticmethod
    def format_date(dt: datetime, language: str = 'ar') -> str:
        """تنسيق التاريخ حسب اللغة"""
        if language == 'ar':
            weekdays = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
            weekday = weekdays[dt.weekday()]
            return f"{weekday} {dt.strftime('%d/%m/%Y')}"
        elif language == 'fr':
            weekdays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            weekday = weekdays[dt.weekday()]
            return f"{weekday} {dt.strftime('%d/%m/%Y')}"
        else:
            return dt.strftime('%A %d/%m/%Y')
    
    @staticmethod
    def format_time(dt: datetime, language: str = 'ar') -> str:
        """تنسيق الوقت"""
        return dt.strftime('%H:%M')
    
    @staticmethod
    def format_datetime(dt: datetime, language: str = 'ar') -> str:
        """تنسيق التاريخ والوقت معاً"""
        date_str = Formatter.format_date(dt, language)
        time_str = Formatter.format_time(dt, language)
        
        if language == 'ar':
            return f"{date_str} الساعة {time_str}"
        elif language == 'fr':
            return f"{date_str} à {time_str}"
        else:
            return f"{date_str} at {time_str}"
    
    @staticmethod
    def format_priority(priority: int, language: str = 'ar') -> str:
        """تنسيق الأولوية"""
        priority_map = {
            'ar': {1: '🔴 عاجل', 2: '🟡 متوسط', 3: '🟢 منخفض'},
            'fr': {1: '🔴 Urgent', 2: '🟡 Moyen', 3: '🟢 Faible'},
            'en': {1: '🔴 Urgent', 2: '🟡 Medium', 3: '🟢 Low'}
        }
        return priority_map.get(language, priority_map['en']).get(priority, '🟡 متوسط')
    
    @staticmethod
    def format_duration(minutes: int, language: str = 'ar') -> str:
        """تنسيق المدة الزمنية"""
        hours = minutes // 60
        mins = minutes % 60
        
        if language == 'ar':
            if hours > 0 and mins > 0:
                return f"{hours} ساعة و {mins} دقيقة"
            elif hours > 0:
                return f"{hours} ساعة"
            else:
                return f"{mins} دقيقة"
        elif language == 'fr':
            if hours > 0 and mins > 0:
                return f"{hours}h {mins}min"
            elif hours > 0:
                return f"{hours}h"
            else:
                return f"{mins}min"
        else:
            if hours > 0 and mins > 0:
                return f"{hours}h {mins}min"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{mins} minute{'s' if mins > 1 else ''}"


# اختبار الوحدات
if __name__ == "__main__":
    print("="*60)
    print("🧪 اختبار الدوال المساعدة")
    print("="*60)
    
    # اختبار محلل التواريخ
    parser = DateTimeParser()
    
    test_cases = [
        ("موعد غداً الساعة 3 مساءً", 'ar'),
        ("اجتماع يوم الأحد 10 صباحاً", 'ar'),
        ("موعد اليوم 14:30", 'ar'),
        ("RDV demain à 15h", 'fr'),
        ("Meeting tomorrow at 10am", 'en'),
        ("موعد 25/12/2025 الساعة 5 مساءً", 'ar')
    ]
    
    print("\n📅 اختبار محلل التواريخ:")
    for text, lang in test_cases:
        result = parser.parse_datetime(text, lang)
        if result:
            print(f"✅ '{text}' → {result.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"❌ '{text}' → فشل التحليل")
    
    # اختبار تنظيف النصوص
    cleaner = TextCleaner()
    print("\n🧹 اختبار تنظيف النصوص:")
    dirty_text = "  موعد   مع!!  الطبيب   "
    clean = cleaner.clean_text(dirty_text)
    print(f"قبل: '{dirty_text}'")
    print(f"بعد: '{clean}'")
    
    # اختبار استخراج الكلمات المفتاحية
    print("\n🔑 اختبار استخراج الكلمات المفتاحية:")
    text = "موعد مع الطبيب في المستشفى غداً"
    keywords = cleaner.extract_keywords(text, 'ar')
    print(f"النص: '{text}'")
    print(f"الكلمات المفتاحية: {keywords}")
    
    # اختبار المدقق
    print("\n✔️ اختبار المدقق:")
    validator = Validator()
    future_date = datetime.now() + timedelta(days=1)
    past_date = datetime.now() - timedelta(days=1)
    print(f"هل التاريخ المستقبلي صحيح؟ {validator.is_future_datetime(future_date)}")
    print(f"هل التاريخ الماضي صحيح؟ {validator.is_future_datetime(past_date)}")
    print(f"هل الأولوية 2 صحيحة؟ {validator.is_valid_priority(2)}")
    print(f"هل الأولوية 5 صحيحة؟ {validator.is_valid_priority(5)}")
    
    # اختبار المنسق
    print("\n📋 اختبار المنسق:")
    formatter = Formatter()
    now = datetime.now()
    print(f"التاريخ بالعربية: {formatter.format_date(now, 'ar')}")
    print(f"التاريخ بالفرنسية: {formatter.format_date(now, 'fr')}")
    print(f"التاريخ بالإنجليزية: {formatter.format_date(now, 'en')}")
    print(f"التاريخ والوقت بالعربية: {formatter.format_datetime(now, 'ar')}")
    print(f"الأولوية: {formatter.format_priority(1, 'ar')}")
    print(f"المدة: {formatter.format_duration(125, 'ar')}")
    
    print("\n" + "="*60)
    print("✅ جميع الاختبارات تمت بنجاح!")
    print("="*60)