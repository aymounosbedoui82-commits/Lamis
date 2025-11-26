# feedback_learning_system.py
"""
نظام التعلم من التغذية الراجعة
✅ جمع feedback من المستخدمين
✅ تصحيح الأخطاء تلقائياً
✅ إعادة التدريب الدوري
✅ تحسين مستمر
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)


# ==========================================
# 1. أنواع التغذية الراجعة
# ==========================================

class FeedbackType(Enum):
    """أنواع التغذية الراجعة"""
    POSITIVE = "positive"           # ردة فعل إيجابية
    NEGATIVE = "negative"           # ردة فعل سلبية
    CORRECTION = "correction"       # تصحيح
    CONFIRMATION = "confirmation"   # تأكيد
    SKIP = "skip"                   # تخطي


@dataclass
class FeedbackEntry:
    """سجل تغذية راجعة"""
    user_id: int
    message: str
    predicted_intent: str
    predicted_confidence: float
    feedback_type: FeedbackType
    correct_intent: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# ==========================================
# 2. مدير التغذية الراجعة
# ==========================================

class FeedbackManager:
    """مدير التغذية الراجعة"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """إنشاء الجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول التغذية الراجعة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                predicted_intent TEXT,
                predicted_confidence REAL,
                feedback_type TEXT NOT NULL,
                correct_intent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed INTEGER DEFAULT 0
            )
        ''')
        
        # جدول التصحيحات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                wrong_intent TEXT NOT NULL,
                correct_intent TEXT NOT NULL,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied INTEGER DEFAULT 0
            )
        ''')
        
        # جدول إحصائيات الأداء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL,
                intent TEXT,
                UNIQUE(date, intent)
            )
        ''')
        
        # جدول سجل التدريب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_type TEXT,
                samples_count INTEGER,
                accuracy REAL,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_feedback(self, entry: FeedbackEntry):
        """تسجيل تغذية راجعة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback 
                (user_id, message, predicted_intent, predicted_confidence, 
                 feedback_type, correct_intent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.user_id,
                entry.message,
                entry.predicted_intent,
                entry.predicted_confidence,
                entry.feedback_type.value,
                entry.correct_intent,
                entry.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم تسجيل feedback: {entry.feedback_type.value}")
            
            # إذا كان تصحيحاً، سجله بشكل منفصل
            if entry.feedback_type == FeedbackType.CORRECTION and entry.correct_intent:
                self.record_correction(
                    entry.message,
                    entry.predicted_intent,
                    entry.correct_intent,
                    entry.user_id
                )
                
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل feedback: {e}")
    
    def record_correction(self, message: str, wrong_intent: str, 
                         correct_intent: str, user_id: int = None):
        """تسجيل تصحيح"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO corrections 
                (message, wrong_intent, correct_intent, user_id)
                VALUES (?, ?, ?, ?)
            ''', (message, wrong_intent, correct_intent, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📝 تم تسجيل تصحيح: {wrong_intent} → {correct_intent}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل التصحيح: {e}")
    
    def get_pending_corrections(self, limit: int = 100) -> List[Dict]:
        """الحصول على التصحيحات غير المطبقة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, message, wrong_intent, correct_intent, user_id
                FROM corrections
                WHERE applied = 0
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            corrections = []
            for row in cursor.fetchall():
                corrections.append({
                    'id': row[0],
                    'message': row[1],
                    'wrong_intent': row[2],
                    'correct_intent': row[3],
                    'user_id': row[4]
                })
            
            conn.close()
            return corrections
            
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
            return []
    
    def mark_corrections_applied(self, correction_ids: List[int]):
        """تعليم التصحيحات كمطبقة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.executemany(
                'UPDATE corrections SET applied = 1 WHERE id = ?',
                [(cid,) for cid in correction_ids]
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
    
    def update_performance_stats(self, intent: str, correct: bool):
        """تحديث إحصائيات الأداء"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # محاولة التحديث
            cursor.execute('''
                INSERT INTO performance_stats (date, intent, total_predictions, correct_predictions)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(date, intent) DO UPDATE SET
                    total_predictions = total_predictions + 1,
                    correct_predictions = correct_predictions + ?,
                    accuracy = CAST(correct_predictions + ? AS REAL) / (total_predictions + 1)
            ''', (today, intent, 1 if correct else 0, 1 if correct else 0, 1 if correct else 0))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث الإحصائيات: {e}")
    
    def get_performance_report(self, days: int = 7) -> Dict:
        """الحصول على تقرير الأداء"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            # إجمالي الأداء
            cursor.execute('''
                SELECT 
                    SUM(total_predictions) as total,
                    SUM(correct_predictions) as correct
                FROM performance_stats
                WHERE date >= ?
            ''', (start_date,))
            
            row = cursor.fetchone()
            total = row[0] or 0
            correct = row[1] or 0
            
            # أداء كل نية
            cursor.execute('''
                SELECT 
                    intent,
                    SUM(total_predictions) as total,
                    SUM(correct_predictions) as correct
                FROM performance_stats
                WHERE date >= ?
                GROUP BY intent
            ''', (start_date,))
            
            intent_stats = {}
            for row in cursor.fetchall():
                intent_stats[row[0]] = {
                    'total': row[1],
                    'correct': row[2],
                    'accuracy': (row[2] / row[1] * 100) if row[1] > 0 else 0
                }
            
            conn.close()
            
            return {
                'period_days': days,
                'total_predictions': total,
                'correct_predictions': correct,
                'overall_accuracy': (correct / total * 100) if total > 0 else 0,
                'intent_breakdown': intent_stats
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
            return {}
    
    def get_training_candidates(self, min_feedback: int = 3) -> List[Dict]:
        """الحصول على أمثلة للتدريب من التصحيحات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # التصحيحات المتكررة
            cursor.execute('''
                SELECT message, correct_intent, COUNT(*) as count
                FROM corrections
                GROUP BY message, correct_intent
                HAVING count >= ?
                ORDER BY count DESC
            ''', (min_feedback,))
            
            candidates = []
            for row in cursor.fetchall():
                candidates.append({
                    'message': row[0],
                    'intent': row[1],
                    'frequency': row[2]
                })
            
            conn.close()
            return candidates
            
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
            return []


# ==========================================
# 3. نظام التعلم التلقائي
# ==========================================

class AutoLearningSystem:
    """نظام التعلم التلقائي"""
    
    def __init__(
        self,
        feedback_manager: FeedbackManager,
        classifier,  # ML classifier instance
        retrain_threshold: int = 50,
        min_accuracy_drop: float = 5.0
    ):
        self.feedback_manager = feedback_manager
        self.classifier = classifier
        self.retrain_threshold = retrain_threshold
        self.min_accuracy_drop = min_accuracy_drop
        
        self.corrections_since_retrain = 0
        self.last_retrain = datetime.now()
        self.is_training = False
        
        self._running = False
        self._monitor_thread = None
    
    def start_monitoring(self, check_interval: int = 3600):
        """بدء المراقبة التلقائية"""
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(check_interval,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("🔄 بدء المراقبة التلقائية للتعلم")
    
    def stop_monitoring(self):
        """إيقاف المراقبة"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self, interval: int):
        """حلقة المراقبة"""
        while self._running:
            try:
                self._check_retrain_needed()
            except Exception as e:
                logger.error(f"❌ خطأ في المراقبة: {e}")
            
            time.sleep(interval)
    
    def _check_retrain_needed(self) -> bool:
        """التحقق من الحاجة لإعادة التدريب"""
        # التحقق من عدد التصحيحات
        corrections = self.feedback_manager.get_pending_corrections()
        
        if len(corrections) >= self.retrain_threshold:
            logger.info(f"📊 {len(corrections)} تصحيح - يجب إعادة التدريب")
            return True
        
        # التحقق من انخفاض الدقة
        report = self.feedback_manager.get_performance_report(days=1)
        if report.get('overall_accuracy', 100) < (100 - self.min_accuracy_drop):
            logger.info(f"📉 الدقة منخفضة: {report['overall_accuracy']:.1f}%")
            return True
        
        return False
    
    def process_feedback(self, user_id: int, message: str, 
                        predicted_intent: str, confidence: float,
                        user_response: str) -> Optional[str]:
        """
        معالجة رد المستخدم كتغذية راجعة
        
        Returns:
            النية الصحيحة إذا تم التصحيح، None إذا كان التنبؤ صحيحاً
        """
        feedback_type, correct_intent = self._analyze_response(user_response, predicted_intent)
        
        entry = FeedbackEntry(
            user_id=user_id,
            message=message,
            predicted_intent=predicted_intent,
            predicted_confidence=confidence,
            feedback_type=feedback_type,
            correct_intent=correct_intent
        )
        
        self.feedback_manager.record_feedback(entry)
        
        # تحديث الإحصائيات
        is_correct = feedback_type in [FeedbackType.POSITIVE, FeedbackType.CONFIRMATION]
        self.feedback_manager.update_performance_stats(predicted_intent, is_correct)
        
        if feedback_type == FeedbackType.CORRECTION:
            self.corrections_since_retrain += 1
        
        return correct_intent
    
    def _analyze_response(self, response: str, predicted_intent: str) -> Tuple[FeedbackType, Optional[str]]:
        """تحليل رد المستخدم"""
        response_lower = response.lower()
        
        # ردود إيجابية
        positive_patterns = [
            'نعم', 'صح', 'تمام', 'صحيح', 'أكيد', 'بالضبط', 'ممتاز',
            'oui', 'correct', 'exactement', 'parfait',
            'yes', 'right', 'correct', 'exactly', 'perfect', 'good'
        ]
        
        if any(p in response_lower for p in positive_patterns):
            return FeedbackType.POSITIVE, None
        
        # ردود سلبية
        negative_patterns = [
            'لا', 'خطأ', 'غلط', 'مش صح',
            'non', 'faux', 'pas correct',
            'no', 'wrong', 'incorrect', 'not right'
        ]
        
        if any(p in response_lower for p in negative_patterns):
            # محاولة استخراج النية الصحيحة
            correct_intent = self._extract_correct_intent(response)
            return FeedbackType.CORRECTION, correct_intent
        
        # تصحيح مباشر (المستخدم يذكر النية الصحيحة)
        intent_mapping = {
            'موعد': 'add_appointment',
            'عرض': 'list_appointments',
            'إلغاء': 'cancel_appointment',
            'تعديل': 'modify_appointment',
            'تذكير': 'set_reminder',
            'مساعدة': 'help'
        }
        
        for keyword, intent in intent_mapping.items():
            if keyword in response_lower and intent != predicted_intent:
                return FeedbackType.CORRECTION, intent
        
        return FeedbackType.SKIP, None
    
    def _extract_correct_intent(self, response: str) -> Optional[str]:
        """استخراج النية الصحيحة من الرد"""
        response_lower = response.lower()
        
        intent_keywords = {
            'add_appointment': ['موعد', 'إضافة', 'حجز', 'rdv', 'appointment', 'add'],
            'list_appointments': ['عرض', 'قائمة', 'afficher', 'list', 'show'],
            'cancel_appointment': ['إلغاء', 'حذف', 'annuler', 'cancel', 'delete'],
            'modify_appointment': ['تعديل', 'تغيير', 'modifier', 'change', 'update'],
            'greeting': ['تحية', 'سلام', 'bonjour', 'hello', 'greeting'],
            'help': ['مساعدة', 'aide', 'help']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(kw in response_lower for kw in keywords):
                return intent
        
        return None
    
    def retrain_model(self) -> Dict:
        """إعادة تدريب النموذج"""
        if self.is_training:
            return {'success': False, 'reason': 'training_in_progress'}
        
        self.is_training = True
        logger.info("🔄 بدء إعادة التدريب...")
        
        try:
            # الحصول على التصحيحات
            corrections = self.feedback_manager.get_pending_corrections()
            
            if not corrections:
                return {'success': False, 'reason': 'no_corrections'}
            
            # إضافة التصحيحات لبيانات التدريب
            # (هذا سيتم تلقائياً عبر IntentDataset)
            
            # إعادة التدريب
            result = self.classifier.train(epochs=5)
            
            if result.get('success'):
                # تعليم التصحيحات كمطبقة
                correction_ids = [c['id'] for c in corrections]
                self.feedback_manager.mark_corrections_applied(correction_ids)
                
                # تسجيل في سجل التدريب
                self._log_training(result)
                
                self.corrections_since_retrain = 0
                self.last_retrain = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعادة التدريب: {e}")
            return {'success': False, 'reason': str(e)}
            
        finally:
            self.is_training = False
    
    def _log_training(self, result: Dict):
        """تسجيل التدريب"""
        try:
            conn = sqlite3.connect(self.feedback_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO training_log (model_type, samples_count, accuracy, notes)
                VALUES (?, ?, ?, ?)
            ''', (
                'auto_retrain',
                result.get('samples_count', 0),
                result.get('best_accuracy', 0),
                json.dumps(result.get('history', {}))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل التدريب: {e}")


# ==========================================
# 4. واجهة Feedback للمستخدم
# ==========================================

class UserFeedbackInterface:
    """واجهة جمع Feedback من المستخدم"""
    
    def __init__(self, feedback_manager: FeedbackManager):
        self.feedback_manager = feedback_manager
        self.pending_feedback: Dict[int, Dict] = {}  # user_id -> pending prediction
    
    def request_feedback(self, user_id: int, message: str, 
                        predicted_intent: str, confidence: float) -> str:
        """طلب تغذية راجعة من المستخدم"""
        # حفظ التنبؤ المعلق
        self.pending_feedback[user_id] = {
            'message': message,
            'intent': predicted_intent,
            'confidence': confidence,
            'timestamp': datetime.now()
        }
        
        # رسالة طلب التأكيد
        if confidence < 0.7:
            return self._low_confidence_prompt(predicted_intent)
        else:
            return None  # لا حاجة لتأكيد
    
    def _low_confidence_prompt(self, intent: str) -> str:
        """رسالة عند ثقة منخفضة"""
        intent_names = {
            'add_appointment': 'إضافة موعد',
            'list_appointments': 'عرض المواعيد',
            'cancel_appointment': 'إلغاء موعد',
            'modify_appointment': 'تعديل موعد',
            'greeting': 'تحية',
            'help': 'مساعدة'
        }
        
        name = intent_names.get(intent, intent)
        return f"🤔 هل تقصد **{name}**؟\n\nأجب بـ 'نعم' للتأكيد أو اكتب ما تريده"
    
    def process_response(self, user_id: int, response: str) -> Optional[Dict]:
        """معالجة رد المستخدم"""
        if user_id not in self.pending_feedback:
            return None
        
        pending = self.pending_feedback.pop(user_id)
        response_lower = response.lower()
        
        # تأكيد
        if any(p in response_lower for p in ['نعم', 'صح', 'oui', 'yes']):
            entry = FeedbackEntry(
                user_id=user_id,
                message=pending['message'],
                predicted_intent=pending['intent'],
                predicted_confidence=pending['confidence'],
                feedback_type=FeedbackType.CONFIRMATION
            )
            self.feedback_manager.record_feedback(entry)
            return {'confirmed': True, 'intent': pending['intent']}
        
        # رفض - محاولة فهم النية الصحيحة
        correct_intent = self._guess_correct_intent(response)
        
        entry = FeedbackEntry(
            user_id=user_id,
            message=pending['message'],
            predicted_intent=pending['intent'],
            predicted_confidence=pending['confidence'],
            feedback_type=FeedbackType.CORRECTION,
            correct_intent=correct_intent
        )
        self.feedback_manager.record_feedback(entry)
        
        return {'confirmed': False, 'correct_intent': correct_intent}
    
    def _guess_correct_intent(self, response: str) -> Optional[str]:
        """تخمين النية الصحيحة من الرد"""
        keywords = {
            'add_appointment': ['موعد', 'إضافة', 'appointment', 'add'],
            'list_appointments': ['عرض', 'مواعيدي', 'show', 'list'],
            'cancel_appointment': ['إلغاء', 'حذف', 'cancel'],
            'help': ['مساعدة', 'help']
        }
        
        for intent, kws in keywords.items():
            if any(kw in response.lower() for kw in kws):
                return intent
        
        return None


# ==========================================
# 5. تقارير وإحصائيات
# ==========================================

class AnalyticsReporter:
    """مولد التقارير والإحصائيات"""
    
    def __init__(self, feedback_manager: FeedbackManager):
        self.feedback_manager = feedback_manager
    
    def generate_daily_report(self) -> str:
        """تقرير يومي"""
        report = self.feedback_manager.get_performance_report(days=1)
        
        text = f"""
📊 **تقرير الأداء اليومي**
{'─'*40}

📈 **الإحصائيات العامة:**
• إجمالي التنبؤات: {report.get('total_predictions', 0)}
• التنبؤات الصحيحة: {report.get('correct_predictions', 0)}
• الدقة: {report.get('overall_accuracy', 0):.1f}%

📋 **أداء النوايا:**
"""
        
        for intent, stats in report.get('intent_breakdown', {}).items():
            text += f"• {intent}: {stats['accuracy']:.0f}% ({stats['correct']}/{stats['total']})\n"
        
        return text
    
    def generate_weekly_report(self) -> str:
        """تقرير أسبوعي"""
        report = self.feedback_manager.get_performance_report(days=7)
        
        text = f"""
📊 **تقرير الأداء الأسبوعي**
{'═'*40}

📈 **ملخص الأسبوع:**
• إجمالي التنبؤات: {report.get('total_predictions', 0)}
• الدقة الإجمالية: {report.get('overall_accuracy', 0):.1f}%

🎯 **أفضل النوايا أداءً:**
"""
        
        sorted_intents = sorted(
            report.get('intent_breakdown', {}).items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )
        
        for intent, stats in sorted_intents[:5]:
            text += f"• {intent}: {stats['accuracy']:.0f}%\n"
        
        return text


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار نظام التغذية الراجعة")
    print("="*70)
    
    # إنشاء المدير
    manager = FeedbackManager("test_feedback.db")
    
    # تسجيل بعض التغذية الراجعة
    print("\n📝 تسجيل feedback...")
    
    entries = [
        FeedbackEntry(1, "موعد غداً", "add_appointment", 0.9, FeedbackType.POSITIVE),
        FeedbackEntry(1, "عرض مواعيدي", "greeting", 0.6, FeedbackType.CORRECTION, "list_appointments"),
        FeedbackEntry(2, "مرحبا", "greeting", 0.95, FeedbackType.POSITIVE),
    ]
    
    for entry in entries:
        manager.record_feedback(entry)
    
    # عرض التقرير
    reporter = AnalyticsReporter(manager)
    print(reporter.generate_daily_report())
    
    # عرض التصحيحات
    corrections = manager.get_pending_corrections()
    print(f"\n📋 التصحيحات المعلقة: {len(corrections)}")
    for c in corrections:
        print(f"  • '{c['message']}': {c['wrong_intent']} → {c['correct_intent']}")
    
    print("\n" + "="*70)
    print("✅ الاختبار انتهى!")
