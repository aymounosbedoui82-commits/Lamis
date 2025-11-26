# integration.py
"""
🔗 ملف التكامل مع Lamis Bot الحالي
═══════════════════════════════════════

يوفر:
- دالة classify_intent المحسنة
- دالة handle_message المحسنة
- تكامل سلس مع الكود الموجود

الاستخدام:
    from integration import SmartMessageHandler
    handler = SmartMessageHandler()
    result = await handler.handle(user_id, message)
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
import logging

from smart_ai_engine import SmartAIEngine, EngineConfig

logger = logging.getLogger(__name__)


# ==========================================
# 1. معالج الرسائل الذكي
# ==========================================

class SmartMessageHandler:
    """
    معالج الرسائل الذكي - بديل محسن لـ handle_message
    
    يدمج:
    - تصنيف ML/BERT
    - فهم السياق
    - استخراج التاريخ/الوقت
    - التعلم المستمر
    """
    
    def __init__(self, db_path: str = "agent_data.db", use_bert: bool = False):
        self.db_path = db_path
        
        # إنشاء المحرك الذكي
        config = EngineConfig()
        config.db_path = db_path
        config.use_bert = use_bert
        
        self.engine = SmartAIEngine(config)
        
        # مستخرج التاريخ والوقت (يمكن استيراده من الكود الأصلي)
        self.datetime_extractor = DateTimeExtractor()
    
    async def handle(
        self,
        user_id: int,
        message: str,
        chat_id: int = None
    ) -> Dict[str, Any]:
        """
        معالجة رسالة المستخدم
        
        Args:
            user_id: معرف المستخدم
            message: نص الرسالة
            chat_id: معرف المحادثة (اختياري)
        
        Returns:
            Dict: نتيجة المعالجة مع الرد المقترح
        """
        # 1. استخراج التاريخ والوقت
        extracted_datetime = self.datetime_extractor.extract(message)
        
        # 2. معالجة بالمحرك الذكي
        result = await self.engine.process_message(
            user_id,
            message,
            extracted_datetime
        )
        
        # 3. تحديد الإجراء المطلوب
        action = self._determine_action(result)
        result['action'] = action
        
        # 4. توليد الرد إذا لم يكن موجوداً
        if not result.get('response'):
            result['response'] = self._generate_response(result)
        
        return result
    
    def _determine_action(self, result: Dict) -> str:
        """تحديد الإجراء المطلوب"""
        intent = result.get('intent', 'unknown')
        state = result.get('state', 'idle')
        
        # خريطة النوايا للإجراءات
        intent_to_action = {
            'add_appointment': 'create_appointment',
            'execute_add_appointment': 'create_appointment',
            'list_appointments': 'show_appointments',
            'check_specific_day': 'show_day_appointments',
            'cancel_appointment': 'delete_appointment',
            'modify_appointment': 'update_appointment',
            'set_reminder': 'create_reminder',
            'greeting': 'send_greeting',
            'thanks': 'send_thanks',
            'help': 'show_help',
            'confirm_appointment': 'await_confirmation',
            'awaiting_time': 'request_time',
            'awaiting_date': 'request_date',
            'awaiting_title': 'request_title',
        }
        
        return intent_to_action.get(intent, 'unknown_action')
    
    def _generate_response(self, result: Dict) -> str:
        """توليد رد للمستخدم"""
        intent = result.get('intent', 'unknown')
        confidence = result.get('confidence', 0)
        
        # ردود بسيطة
        simple_responses = {
            'greeting': "مرحباً! كيف يمكنني مساعدتك اليوم؟ 😊",
            'thanks': "على الرحب والسعة! 🙏",
            'help': self._get_help_message(),
            'unknown': "عذراً، لم أفهم طلبك. هل يمكنك إعادة صياغته؟"
        }
        
        if intent in simple_responses:
            return simple_responses[intent]
        
        # رد افتراضي
        return None
    
    def _get_help_message(self) -> str:
        """رسالة المساعدة"""
        return """
🤖 **مرحباً! أنا Lamis Bot**

يمكنني مساعدتك في:

📅 **إدارة المواعيد:**
• "موعد غداً الساعة 3" - إضافة موعد
• "عرض مواعيدي" - قائمة المواعيد
• "مواعيدي اليوم" - مواعيد يوم محدد
• "إلغاء الموعد" - حذف موعد

⏰ **التذكيرات:**
• "ذكرني قبل 30 دقيقة"

🌍 **اللغات المدعومة:**
• العربية 🇸🇦
• الفرنسية 🇫🇷
• الإنجليزية 🇬🇧

اكتب ما تريد وسأساعدك! 💪
"""
    
    def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        تصنيف نية الرسالة (للتوافق مع الكود القديم)
        
        Returns:
            Tuple: (النية, الثقة)
        """
        result = self.engine.intent_classifier.predict(message)
        return result['intent'], result['confidence']
    
    def get_context(self, user_id: int) -> Dict:
        """الحصول على سياق المستخدم"""
        return self.engine.get_user_context(user_id)
    
    def reset_context(self, user_id: int):
        """إعادة تعيين السياق"""
        self.engine.reset_user_context(user_id)
    
    def record_feedback(self, user_id: int, message: str, 
                       intent: str, is_correct: bool, correct_intent: str = None):
        """تسجيل تغذية راجعة"""
        if is_correct:
            self.engine.record_positive_feedback(user_id, message, intent, 1.0)
        elif correct_intent:
            self.engine.record_correction(user_id, message, intent, correct_intent)


# ==========================================
# 2. مستخرج التاريخ والوقت
# ==========================================

class DateTimeExtractor:
    """مستخرج التاريخ والوقت من النصوص"""
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """تجميع الأنماط"""
        # أنماط الوقت
        self.time_patterns = [
            # HH:MM
            (r'(\d{1,2}):(\d{2})', lambda m: (int(m.group(1)), int(m.group(2)))),
            # XXh أو XXhMM
            (r'(\d{1,2})h(\d{2})?', lambda m: (int(m.group(1)), int(m.group(2) or 0))),
            # الساعة X
            (r'الساعة\s*(\d{1,2})', lambda m: (int(m.group(1)), 0)),
            # X صباحاً/مساءً
            (r'(\d{1,2})\s*(صباح|مساء|am|pm)', self._parse_ampm),
        ]
        
        # أنماط التاريخ
        self.date_keywords = {
            'ar': {
                'اليوم': 0, 'غدا': 1, 'غداً': 1, 'بعد غد': 2, 'غدوة': 1,
                'الأحد': 'sunday', 'الإثنين': 'monday', 'الثلاثاء': 'tuesday',
                'الأربعاء': 'wednesday', 'الخميس': 'thursday', 'الجمعة': 'friday',
                'السبت': 'saturday'
            },
            'fr': {
                "aujourd'hui": 0, 'demain': 1, 'après-demain': 2,
                'lundi': 'monday', 'mardi': 'tuesday', 'mercredi': 'wednesday',
                'jeudi': 'thursday', 'vendredi': 'friday', 'samedi': 'saturday',
                'dimanche': 'sunday'
            },
            'en': {
                'today': 0, 'tomorrow': 1,
                'monday': 'monday', 'tuesday': 'tuesday', 'wednesday': 'wednesday',
                'thursday': 'thursday', 'friday': 'friday', 'saturday': 'saturday',
                'sunday': 'sunday'
            }
        }
    
    def _parse_ampm(self, match) -> Tuple[int, int]:
        """تحليل صيغة AM/PM"""
        hour = int(match.group(1))
        period = match.group(2).lower()
        
        if period in ['مساء', 'pm'] and hour < 12:
            hour += 12
        elif period in ['صباح', 'am'] and hour == 12:
            hour = 0
        
        return (hour, 0)
    
    def extract(self, text: str) -> Dict:
        """
        استخراج التاريخ والوقت من النص
        
        Returns:
            Dict: {'date': datetime, 'time': (hour, minute), 'title': str}
        """
        result = {
            'date': None,
            'time': None,
            'title': None
        }
        
        text_lower = text.lower()
        now = datetime.now()
        
        # استخراج الوقت
        for pattern, parser in self.time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['time'] = parser(match)
                break
        
        # استخراج التاريخ
        for lang, keywords in self.date_keywords.items():
            for keyword, value in keywords.items():
                if keyword in text_lower:
                    if isinstance(value, int):
                        result['date'] = now + timedelta(days=value)
                    else:
                        # يوم من أيام الأسبوع
                        result['date'] = self._next_weekday(now, value)
                    break
        
        # محاولة استخراج تاريخ رقمي
        if result['date'] is None:
            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', text)
            if date_match:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else now.year
                if year < 100:
                    year += 2000
                try:
                    result['date'] = datetime(year, month, day)
                except ValueError:
                    pass
        
        # استخراج العنوان (ما تبقى من النص)
        title = self._extract_title(text)
        if title:
            result['title'] = title
        
        return result
    
    def _next_weekday(self, start: datetime, weekday_name: str) -> datetime:
        """الحصول على تاريخ اليوم القادم من الأسبوع"""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target = weekdays.get(weekday_name.lower(), 0)
        current = start.weekday()
        
        days_ahead = target - current
        if days_ahead <= 0:
            days_ahead += 7
        
        return start + timedelta(days=days_ahead)
    
    def _extract_title(self, text: str) -> Optional[str]:
        """استخراج العنوان من النص"""
        # إزالة الكلمات المفتاحية
        remove_patterns = [
            r'موعد', r'اجتماع', r'rdv', r'rendez-vous', r'appointment', r'meeting',
            r'الساعة\s*\d+', r'\d{1,2}:\d{2}', r'\d{1,2}h\d{0,2}',
            r'غدا|غداً|اليوم|بكرة', r'demain|aujourd', r'today|tomorrow',
            r'صباحا|مساء|صباحاً|مساءً'
        ]
        
        title = text
        for pattern in remove_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # تنظيف
        title = re.sub(r'\s+', ' ', title).strip()
        
        # إذا تبقى نص ذو معنى
        if len(title) > 2:
            return title
        
        return None


# ==========================================
# 3. دوال للتوافق مع الكود القديم
# ==========================================

# Instance عام للاستخدام المباشر
_handler_instance = None

def get_handler() -> SmartMessageHandler:
    """الحصول على معالج الرسائل"""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = SmartMessageHandler()
    return _handler_instance


def classify_intent(message: str) -> Tuple[str, float]:
    """
    تصنيف نية الرسالة
    (دالة للتوافق مع الكود القديم)
    
    Usage:
        intent, confidence = classify_intent("موعد غداً")
    """
    handler = get_handler()
    return handler.classify_intent(message)


async def handle_message(user_id: int, message: str) -> Dict:
    """
    معالجة رسالة
    (دالة للتوافق مع الكود القديم)
    
    Usage:
        result = await handle_message(123, "موعد غداً الساعة 3")
    """
    handler = get_handler()
    return await handler.handle(user_id, message)


def extract_datetime(message: str) -> Dict:
    """
    استخراج التاريخ والوقت
    
    Usage:
        info = extract_datetime("موعد غداً الساعة 3 مساءً")
    """
    extractor = DateTimeExtractor()
    return extractor.extract(message)


# ==========================================
# 4. مثال التكامل مع البوت
# ==========================================

"""
مثال التكامل مع ملف البوت الرئيسي:

```python
# في ملف lamis_bot.py أو main.py

from integration import SmartMessageHandler, classify_intent, extract_datetime

# إنشاء المعالج
handler = SmartMessageHandler(db_path="agent_data.db")

@bot.message_handler(func=lambda m: True)
async def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    # معالجة ذكية
    result = await handler.handle(user_id, text)
    
    # تنفيذ الإجراء
    if result['action'] == 'create_appointment':
        # إنشاء موعد
        await create_appointment(
            user_id=user_id,
            title=result['extracted_info'].get('title'),
            date=result['extracted_info'].get('date'),
            time=result['extracted_info'].get('time')
        )
        
    elif result['action'] == 'show_appointments':
        # عرض المواعيد
        appointments = await get_appointments(user_id)
        # ...
    
    # إرسال الرد
    if result.get('response'):
        await bot.send_message(message.chat.id, result['response'])
```
"""


# ==========================================
# اختبار
# ==========================================

async def test_integration():
    """اختبار التكامل"""
    print("\n" + "="*70)
    print("🧪 اختبار نظام التكامل")
    print("="*70)
    
    handler = SmartMessageHandler()
    
    # تدريب أولي
    print("\n📚 تدريب النموذج...")
    handler.engine.train_classifier(epochs=50)
    
    # اختبار
    test_messages = [
        "مرحبا",
        "موعد مع الطبيب غداً الساعة 3",
        "عرض مواعيدي",
        "إلغاء الموعد رقم 5",
        "RDV demain à 14h30",
        "What are my appointments today?"
    ]
    
    print("\n" + "─"*70)
    print("🔍 اختبار المعالجة:")
    print("─"*70)
    
    for msg in test_messages:
        print(f"\n📩 '{msg}'")
        result = await handler.handle(user_id=1, message=msg)
        
        print(f"   🎯 Intent: {result['intent']}")
        print(f"   📊 Confidence: {result['confidence']*100:.0f}%")
        print(f"   🔧 Action: {result['action']}")
        
        if result['extracted_info']:
            print(f"   📋 Extracted: {result['extracted_info']}")
    
    # اختبار استخراج التاريخ/الوقت
    print("\n" + "─"*70)
    print("📅 اختبار استخراج التاريخ/الوقت:")
    print("─"*70)
    
    datetime_tests = [
        "موعد غداً الساعة 3 مساءً",
        "RDV demain à 15h30",
        "Meeting tomorrow at 2pm",
        "موعد يوم 25/12 الساعة 10:30"
    ]
    
    for text in datetime_tests:
        info = extract_datetime(text)
        print(f"\n'{text}'")
        print(f"   📅 Date: {info.get('date')}")
        print(f"   ⏰ Time: {info.get('time')}")
        print(f"   📋 Title: {info.get('title')}")
    
    print("\n" + "="*70)
    print("✅ اختبار التكامل ناجح!")


if __name__ == "__main__":
    asyncio.run(test_integration())
