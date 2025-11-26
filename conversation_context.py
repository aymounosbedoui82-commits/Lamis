# conversation_context.py
"""
نظام إدارة سياق المحادثة المتقدم
✅ تتبع حالة المحادثة
✅ فهم الأسئلة المتتالية
✅ استخراج المعلومات التراكمي
✅ ذاكرة قصيرة المدى للمحادثة
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import deque
import re

logger = logging.getLogger(__name__)


# ==========================================
# 1. حالات المحادثة
# ==========================================

class ConversationState(Enum):
    """حالات المحادثة الممكنة"""
    IDLE = "idle"                          # خامل - لا يوجد إجراء معلق
    AWAITING_TIME = "awaiting_time"        # ينتظر وقت الموعد
    AWAITING_DATE = "awaiting_date"        # ينتظر تاريخ الموعد
    AWAITING_TITLE = "awaiting_title"      # ينتظر عنوان الموعد
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # ينتظر تأكيد
    AWAITING_SELECTION = "awaiting_selection"  # ينتظر اختيار من قائمة
    AWAITING_REMINDER_TIME = "awaiting_reminder_time"  # ينتظر وقت التذكير
    COLLECTING_INFO = "collecting_info"    # يجمع معلومات متعددة


@dataclass
class ExtractedInfo:
    """المعلومات المستخرجة من المحادثة"""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[Tuple[int, int]] = None  # (hour, minute)
    priority: Optional[int] = None
    appointment_id: Optional[int] = None
    reminder_minutes: Optional[int] = None
    
    def is_complete_for_appointment(self) -> bool:
        """هل المعلومات كافية لإنشاء موعد؟"""
        return self.title is not None and (self.date is not None or self.time is not None)
    
    def get_datetime(self) -> Optional[datetime]:
        """الحصول على التاريخ والوقت الكاملين"""
        if self.date is None:
            return None
        
        if self.time:
            return self.date.replace(hour=self.time[0], minute=self.time[1])
        return self.date
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time,
            'priority': self.priority,
            'appointment_id': self.appointment_id,
            'reminder_minutes': self.reminder_minutes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExtractedInfo':
        """إنشاء من قاموس"""
        info = cls()
        info.title = data.get('title')
        info.description = data.get('description')
        if data.get('date'):
            info.date = datetime.fromisoformat(data['date'])
        info.time = tuple(data['time']) if data.get('time') else None
        info.priority = data.get('priority')
        info.appointment_id = data.get('appointment_id')
        info.reminder_minutes = data.get('reminder_minutes')
        return info


@dataclass
class ConversationTurn:
    """دورة محادثة واحدة"""
    user_message: str
    bot_response: str
    intent: str
    extracted_info: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'intent': self.intent,
            'extracted_info': self.extracted_info,
            'timestamp': self.timestamp.isoformat()
        }


# ==========================================
# 2. مدير سياق المحادثة
# ==========================================

class ConversationContext:
    """مدير سياق المحادثة لمستخدم واحد"""
    
    MAX_HISTORY_SIZE = 10  # عدد الرسائل المحفوظة
    CONTEXT_TIMEOUT_MINUTES = 30  # مهلة انتهاء السياق
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = ConversationState.IDLE
        self.extracted_info = ExtractedInfo()
        self.history: deque = deque(maxlen=self.MAX_HISTORY_SIZE)
        self.pending_action: Optional[str] = None
        self.last_activity: datetime = datetime.now()
        self.language: str = 'ar'
        self.metadata: Dict[str, Any] = {}
    
    def is_expired(self) -> bool:
        """هل انتهت صلاحية السياق؟"""
        elapsed = datetime.now() - self.last_activity
        return elapsed > timedelta(minutes=self.CONTEXT_TIMEOUT_MINUTES)
    
    def reset(self):
        """إعادة تعيين السياق"""
        self.state = ConversationState.IDLE
        self.extracted_info = ExtractedInfo()
        self.pending_action = None
        self.metadata = {}
        logger.debug(f"🔄 تم إعادة تعيين سياق المستخدم {self.user_id}")
    
    def update_activity(self):
        """تحديث وقت النشاط"""
        self.last_activity = datetime.now()
    
    def add_turn(self, user_message: str, bot_response: str, intent: str, extracted: Dict = None):
        """إضافة دورة محادثة"""
        turn = ConversationTurn(
            user_message=user_message,
            bot_response=bot_response,
            intent=intent,
            extracted_info=extracted or {}
        )
        self.history.append(turn)
        self.update_activity()
    
    def get_last_intent(self) -> Optional[str]:
        """الحصول على النية الأخيرة"""
        if self.history:
            return self.history[-1].intent
        return None
    
    def get_last_n_messages(self, n: int = 3) -> List[Dict]:
        """الحصول على آخر n رسائل"""
        return [turn.to_dict() for turn in list(self.history)[-n:]]
    
    def get_conversation_summary(self) -> str:
        """ملخص المحادثة"""
        if not self.history:
            return "لا توجد محادثة سابقة"
        
        summary = []
        for turn in self.history:
            summary.append(f"المستخدم: {turn.user_message[:50]}...")
            summary.append(f"البوت: {turn.bot_response[:50]}...")
        
        return "\n".join(summary)
    
    def to_dict(self) -> Dict:
        """تحويل السياق إلى قاموس"""
        return {
            'user_id': self.user_id,
            'state': self.state.value,
            'extracted_info': self.extracted_info.to_dict(),
            'pending_action': self.pending_action,
            'last_activity': self.last_activity.isoformat(),
            'language': self.language,
            'history_count': len(self.history)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationContext':
        """إنشاء السياق من قاموس"""
        ctx = cls(data['user_id'])
        ctx.state = ConversationState(data.get('state', 'idle'))
        ctx.extracted_info = ExtractedInfo.from_dict(data.get('extracted_info', {}))
        ctx.pending_action = data.get('pending_action')
        if data.get('last_activity'):
            ctx.last_activity = datetime.fromisoformat(data['last_activity'])
        ctx.language = data.get('language', 'ar')
        return ctx


# ==========================================
# 3. مدير السياقات المتعددة
# ==========================================

class ConversationManager:
    """مدير السياقات لجميع المستخدمين"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self.contexts: Dict[int, ConversationContext] = {}
        self._ensure_table()
    
    def _ensure_table(self):
        """إنشاء جدول السياقات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_contexts (
                user_id INTEGER PRIMARY KEY,
                context_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent TEXT,
                extracted_info TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_context(self, user_id: int) -> ConversationContext:
        """الحصول على سياق المستخدم"""
        # التحقق من الذاكرة أولاً
        if user_id in self.contexts:
            ctx = self.contexts[user_id]
            
            # التحقق من انتهاء الصلاحية
            if ctx.is_expired():
                ctx.reset()
            
            return ctx
        
        # محاولة التحميل من قاعدة البيانات
        ctx = self._load_context(user_id)
        
        if ctx is None:
            ctx = ConversationContext(user_id)
        
        self.contexts[user_id] = ctx
        return ctx
    
    def _load_context(self, user_id: int) -> Optional[ConversationContext]:
        """تحميل السياق من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT context_data FROM conversation_contexts WHERE user_id = ?',
                (user_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data = json.loads(row[0])
                return ConversationContext.from_dict(data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل السياق: {e}")
            return None
    
    def save_context(self, user_id: int):
        """حفظ السياق في قاعدة البيانات"""
        if user_id not in self.contexts:
            return
        
        try:
            ctx = self.contexts[user_id]
            data = json.dumps(ctx.to_dict(), ensure_ascii=False)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversation_contexts (user_id, context_data, updated_at)
                VALUES (?, ?, ?)
            ''', (user_id, data, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ السياق: {e}")
    
    def save_turn(self, user_id: int, user_message: str, bot_response: str, 
                  intent: str, extracted_info: Dict = None):
        """حفظ دورة محادثة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_history 
                (user_id, user_message, bot_response, intent, extracted_info)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_message,
                bot_response,
                intent,
                json.dumps(extracted_info or {}, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ المحادثة: {e}")
    
    def get_user_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """الحصول على تاريخ محادثات المستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, bot_response, intent, extracted_info, timestamp
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'user_message': row[0],
                    'bot_response': row[1],
                    'intent': row[2],
                    'extracted_info': json.loads(row[3]) if row[3] else {},
                    'timestamp': row[4]
                })
            
            conn.close()
            return history[::-1]  # ترتيب تصاعدي
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب التاريخ: {e}")
            return []
    
    def clear_context(self, user_id: int):
        """مسح سياق المستخدم"""
        if user_id in self.contexts:
            self.contexts[user_id].reset()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversation_contexts WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ خطأ في مسح السياق: {e}")


# ==========================================
# 4. معالج السياق الذكي
# ==========================================

class ContextAwareProcessor:
    """معالج يفهم السياق"""
    
    def __init__(self, conversation_manager: ConversationManager):
        self.manager = conversation_manager
    
    def process_with_context(
        self,
        user_id: int,
        message: str,
        current_intent: str,
        extracted_info: Dict
    ) -> Tuple[str, Dict, ConversationState]:
        """
        معالجة الرسالة مع مراعاة السياق
        
        Returns:
            Tuple: (النية المعدلة, المعلومات الكاملة, الحالة الجديدة)
        """
        ctx = self.manager.get_context(user_id)
        
        # التحقق من انتهاء الصلاحية
        if ctx.is_expired():
            ctx.reset()
        
        # ==========================================
        # معالجة حسب الحالة الحالية
        # ==========================================
        
        # حالة: ينتظر وقت
        if ctx.state == ConversationState.AWAITING_TIME:
            time_extracted = self._extract_time_from_message(message)
            if time_extracted:
                ctx.extracted_info.time = time_extracted
                
                if ctx.extracted_info.is_complete_for_appointment():
                    ctx.state = ConversationState.AWAITING_CONFIRMATION
                    return 'confirm_appointment', ctx.extracted_info.to_dict(), ctx.state
                else:
                    ctx.state = ConversationState.AWAITING_DATE
                    return 'awaiting_date', ctx.extracted_info.to_dict(), ctx.state
        
        # حالة: ينتظر تاريخ
        if ctx.state == ConversationState.AWAITING_DATE:
            date_extracted = self._extract_date_from_message(message)
            if date_extracted:
                ctx.extracted_info.date = date_extracted
                
                if ctx.extracted_info.is_complete_for_appointment():
                    ctx.state = ConversationState.AWAITING_CONFIRMATION
                    return 'confirm_appointment', ctx.extracted_info.to_dict(), ctx.state
        
        # حالة: ينتظر تأكيد
        if ctx.state == ConversationState.AWAITING_CONFIRMATION:
            if self._is_confirmation(message):
                ctx.state = ConversationState.IDLE
                return 'execute_add_appointment', ctx.extracted_info.to_dict(), ctx.state
            elif self._is_rejection(message):
                ctx.reset()
                return 'cancelled', {}, ConversationState.IDLE
        
        # ==========================================
        # معالجة النية الجديدة
        # ==========================================
        
        if current_intent == 'add_appointment':
            # دمج المعلومات المستخرجة
            self._merge_extracted_info(ctx, extracted_info)
            
            # التحقق من اكتمال المعلومات
            if ctx.extracted_info.is_complete_for_appointment():
                ctx.state = ConversationState.AWAITING_CONFIRMATION
                return 'confirm_appointment', ctx.extracted_info.to_dict(), ctx.state
            
            # تحديد ما ينقص
            if ctx.extracted_info.title is None:
                ctx.state = ConversationState.AWAITING_TITLE
                return 'awaiting_title', ctx.extracted_info.to_dict(), ctx.state
            
            if ctx.extracted_info.date is None and ctx.extracted_info.time is None:
                ctx.state = ConversationState.AWAITING_TIME
                return 'awaiting_time', ctx.extracted_info.to_dict(), ctx.state
        
        # حالات أخرى - تمرير كما هي
        ctx.pending_action = current_intent
        return current_intent, extracted_info, ctx.state
    
    def _merge_extracted_info(self, ctx: ConversationContext, new_info: Dict):
        """دمج المعلومات الجديدة مع الموجودة"""
        if new_info.get('title'):
            ctx.extracted_info.title = new_info['title']
        if new_info.get('description'):
            ctx.extracted_info.description = new_info['description']
        if new_info.get('date'):
            if isinstance(new_info['date'], str):
                ctx.extracted_info.date = datetime.fromisoformat(new_info['date'])
            else:
                ctx.extracted_info.date = new_info['date']
        if new_info.get('time'):
            ctx.extracted_info.time = tuple(new_info['time']) if isinstance(new_info['time'], list) else new_info['time']
        if new_info.get('priority'):
            ctx.extracted_info.priority = new_info['priority']
    
    def _extract_time_from_message(self, message: str) -> Optional[Tuple[int, int]]:
        """استخراج الوقت من الرسالة"""
        # نمط XX:XX
        match = re.search(r'(\d{1,2}):(\d{2})', message)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        
        # نمط XXh أو XXh00
        match = re.search(r'(\d{1,2})h(\d{2})?', message.lower())
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            return (hour, minute)
        
        # نمط رقم + صباحاً/مساءً
        match = re.search(r'(\d{1,2})\s*(صباحا|صباحاً|مساء|مساءً|am|pm)', message.lower())
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            if period in ['مساء', 'مساءً', 'pm'] and hour < 12:
                hour += 12
            elif period in ['صباحا', 'صباحاً', 'am'] and hour == 12:
                hour = 0
            return (hour, 0)
        
        return None
    
    def _extract_date_from_message(self, message: str) -> Optional[datetime]:
        """استخراج التاريخ من الرسالة"""
        now = datetime.now()
        message_lower = message.lower()
        
        # اليوم/غداً
        if 'اليوم' in message_lower or "aujourd'hui" in message_lower or 'today' in message_lower:
            return now
        if 'غدا' in message_lower or 'غداً' in message_lower or 'demain' in message_lower or 'tomorrow' in message_lower:
            return now + timedelta(days=1)
        
        # تاريخ رقمي
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', message)
        if match:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if year < 100:
                year += 2000
            try:
                return datetime(year, month, day)
            except:
                pass
        
        return None
    
    def _is_confirmation(self, message: str) -> bool:
        """هل الرسالة تأكيد؟"""
        confirmations = [
            'نعم', 'أيوا', 'اي', 'صح', 'تمام', 'موافق', 'أكيد', 'طبعا',
            'oui', 'ouais', 'ok', 'd\'accord', 'parfait',
            'yes', 'yeah', 'sure', 'ok', 'confirm', 'correct'
        ]
        return any(c in message.lower() for c in confirmations)
    
    def _is_rejection(self, message: str) -> bool:
        """هل الرسالة رفض؟"""
        rejections = [
            'لا', 'لأ', 'إلغاء', 'غلط', 'خطأ',
            'non', 'annuler', 'pas',
            'no', 'cancel', 'wrong', 'nevermind'
        ]
        return any(r in message.lower() for r in rejections)
    
    def get_missing_info_prompt(self, ctx: ConversationContext) -> str:
        """الحصول على سؤال للمعلومات الناقصة"""
        lang = ctx.language
        
        prompts = {
            ConversationState.AWAITING_TIME: {
                'ar': "⏰ في أي ساعة تريد الموعد؟\n\nمثال: 3 مساءً أو 15:00",
                'fr': "⏰ À quelle heure voulez-vous le RDV?\n\nExemple: 15h ou 15:00",
                'en': "⏰ What time would you like the appointment?\n\nExample: 3pm or 15:00"
            },
            ConversationState.AWAITING_DATE: {
                'ar': "📅 في أي يوم تريد الموعد؟\n\nمثال: غداً، الخميس، أو 25/12",
                'fr': "📅 Quel jour voulez-vous le RDV?\n\nExemple: demain, jeudi, ou 25/12",
                'en': "📅 What day would you like the appointment?\n\nExample: tomorrow, Thursday, or 25/12"
            },
            ConversationState.AWAITING_TITLE: {
                'ar': "📋 ما هو عنوان الموعد؟\n\nمثال: موعد مع الطبيب",
                'fr': "📋 Quel est le titre du RDV?\n\nExemple: RDV médecin",
                'en': "📋 What is the appointment title?\n\nExample: Doctor appointment"
            },
            ConversationState.AWAITING_CONFIRMATION: {
                'ar': "✅ هل تريد تأكيد هذا الموعد؟\n\nأجب بـ: نعم أو لا",
                'fr': "✅ Voulez-vous confirmer ce RDV?\n\nRépondez: oui ou non",
                'en': "✅ Would you like to confirm this appointment?\n\nReply: yes or no"
            }
        }
        
        if ctx.state in prompts:
            return prompts[ctx.state].get(lang, prompts[ctx.state]['ar'])
        
        return ""


# ==========================================
# 5. مولد الردود السياقية
# ==========================================

class ContextualResponseGenerator:
    """مولد ردود يراعي السياق"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """تحميل قوالب الردود"""
        return {
            'confirm_appointment': {
                'ar': """✅ **تأكيد الموعد:**

📋 العنوان: {title}
📅 التاريخ: {date}
⏰ الوقت: {time}
{priority_line}

هل تريد تأكيد هذا الموعد؟
أجب بـ: **نعم** للتأكيد أو **لا** للإلغاء""",
                'fr': """✅ **Confirmation du RDV:**

📋 Titre: {title}
📅 Date: {date}
⏰ Heure: {time}
{priority_line}

Voulez-vous confirmer ce RDV?
Répondez: **oui** pour confirmer ou **non** pour annuler""",
                'en': """✅ **Confirm Appointment:**

📋 Title: {title}
📅 Date: {date}
⏰ Time: {time}
{priority_line}

Would you like to confirm this appointment?
Reply: **yes** to confirm or **no** to cancel"""
            },
            'appointment_created': {
                'ar': "✅ تم إنشاء الموعد بنجاح! رقم الموعد: #{id}",
                'fr': "✅ RDV créé avec succès! Numéro: #{id}",
                'en': "✅ Appointment created successfully! ID: #{id}"
            },
            'cancelled': {
                'ar': "❌ تم إلغاء العملية",
                'fr': "❌ Opération annulée",
                'en': "❌ Operation cancelled"
            }
        }
    
    def generate(self, template_key: str, language: str, **kwargs) -> str:
        """توليد رد من قالب"""
        if template_key not in self.templates:
            return ""
        
        template = self.templates[template_key].get(language, self.templates[template_key].get('ar', ''))
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"⚠️ مفتاح ناقص في القالب: {e}")
            return template


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار نظام سياق المحادثة")
    print("="*70)
    
    # إنشاء المدير
    manager = ConversationManager("test_context.db")
    processor = ContextAwareProcessor(manager)
    
    user_id = 12345
    
    # محاكاة محادثة متعددة الأدوار
    print("\n📱 محاكاة محادثة:")
    print("-"*70)
    
    # الرسالة 1: طلب موعد بدون تفاصيل كاملة
    print("\n👤 المستخدم: موعد مع الطبيب")
    intent, info, state = processor.process_with_context(
        user_id, 
        "موعد مع الطبيب",
        "add_appointment",
        {'title': 'موعد مع الطبيب'}
    )
    print(f"🤖 النية: {intent}")
    print(f"📊 الحالة: {state.value}")
    
    ctx = manager.get_context(user_id)
    prompt = processor.get_missing_info_prompt(ctx)
    print(f"🤖 البوت: {prompt}")
    
    # الرسالة 2: إضافة الوقت
    print("\n👤 المستخدم: غداً الساعة 3")
    intent, info, state = processor.process_with_context(
        user_id,
        "غداً الساعة 3",
        "unknown",
        {}
    )
    print(f"🤖 النية: {intent}")
    print(f"📊 الحالة: {state.value}")
    print(f"📋 المعلومات: {info}")
    
    # الرسالة 3: التأكيد
    print("\n👤 المستخدم: نعم")
    intent, info, state = processor.process_with_context(
        user_id,
        "نعم",
        "unknown",
        {}
    )
    print(f"🤖 النية: {intent}")
    print(f"📊 الحالة: {state.value}")
    
    print("\n" + "="*70)
    print("✅ الاختبار انتهى!")
