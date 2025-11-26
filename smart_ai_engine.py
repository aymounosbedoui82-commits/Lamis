# smart_ai_engine.py
"""
🧠 المحرك الذكي المتكامل لـ Lamis Bot
═══════════════════════════════════════

يدمج جميع الأنظمة الذكية:
✅ تصنيف النوايا بـ ML/BERT
✅ إدارة سياق المحادثة
✅ التعلم من التغذية الراجعة
✅ التحسين المستمر

الاستخدام:
    engine = SmartAIEngine()
    result = await engine.process_message(user_id, message)
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
import json

# استيراد الأنظمة الفرعية
from ml_intent_classifier import SmartIntentClassifier, MultilingualTextProcessor
from conversation_context import (
    ConversationManager, 
    ConversationContext,
    ConversationState,
    ContextAwareProcessor,
    ContextualResponseGenerator,
    ExtractedInfo
)
from feedback_learning_system import (
    FeedbackManager,
    FeedbackEntry,
    FeedbackType,
    AutoLearningSystem,
    UserFeedbackInterface,
    AnalyticsReporter
)

# محاولة استيراد BERT
try:
    from bert_arabic_classifier import SmartBERTClassifier
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False

logger = logging.getLogger(__name__)


# ==========================================
# إعدادات النظام
# ==========================================

class EngineConfig:
    """إعدادات المحرك"""
    
    def __init__(self):
        # المسارات
        self.db_path = "agent_data.db"
        self.models_dir = "models"
        
        # إعدادات ML
        self.use_bert = False  # استخدام BERT (أبطأ لكن أدق)
        self.confidence_threshold = 0.6  # حد الثقة الأدنى
        self.fallback_to_rules = True  # الرجوع للقواعد عند الثقة المنخفضة
        
        # إعدادات السياق
        self.context_timeout_minutes = 30
        self.max_history_size = 10
        
        # إعدادات التعلم
        self.auto_retrain = True
        self.retrain_threshold = 50  # عدد التصحيحات قبل إعادة التدريب
        self.check_interval = 3600  # فحص كل ساعة
        
        # إعدادات Feedback
        self.request_feedback_below = 0.7  # طلب تأكيد تحت هذه الثقة
    
    def to_dict(self) -> Dict:
        return {
            'db_path': self.db_path,
            'use_bert': self.use_bert,
            'confidence_threshold': self.confidence_threshold,
            'auto_retrain': self.auto_retrain
        }


# ==========================================
# المحرك الذكي الرئيسي
# ==========================================

class SmartAIEngine:
    """
    المحرك الذكي المتكامل
    
    يجمع بين:
    - تصنيف النوايا (ML/BERT)
    - فهم السياق
    - التعلم من الأخطاء
    """
    
    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        
        # تهيئة المكونات
        self._init_components()
        
        logger.info("🚀 تم تشغيل المحرك الذكي")
    
    def _init_components(self):
        """تهيئة جميع المكونات"""
        
        # 1. مصنف النوايا
        print("📦 جاري تحميل مصنف النوايا...")
        if self.config.use_bert and BERT_AVAILABLE:
            self.intent_classifier = SmartBERTClassifier(
                model_path=f"{self.config.models_dir}/bert_intent.pth",
                db_path=self.config.db_path
            )
            print("   ✅ BERT Classifier")
        else:
            self.intent_classifier = SmartIntentClassifier(
                model_path=f"{self.config.models_dir}/intent_classifier.pth",
                processor_path=f"{self.config.models_dir}/text_processor.pkl",
                db_path=self.config.db_path,
                model_type="lstm"
            )
            print("   ✅ LSTM Classifier")
        
        # 2. مدير السياق
        print("📦 جاري تحميل مدير السياق...")
        self.conversation_manager = ConversationManager(self.config.db_path)
        self.context_processor = ContextAwareProcessor(self.conversation_manager)
        self.response_generator = ContextualResponseGenerator()
        print("   ✅ Conversation Manager")
        
        # 3. نظام التغذية الراجعة
        print("📦 جاري تحميل نظام التعلم...")
        self.feedback_manager = FeedbackManager(self.config.db_path)
        self.feedback_interface = UserFeedbackInterface(self.feedback_manager)
        
        # 4. نظام التعلم التلقائي
        self.auto_learner = AutoLearningSystem(
            self.feedback_manager,
            self.intent_classifier,
            retrain_threshold=self.config.retrain_threshold
        )
        
        if self.config.auto_retrain:
            self.auto_learner.start_monitoring(self.config.check_interval)
        print("   ✅ Auto Learning System")
        
        # 5. مولد التقارير
        self.reporter = AnalyticsReporter(self.feedback_manager)
        
        print("\n✅ تم تهيئة جميع المكونات!")
    
    # ==========================================
    # المعالجة الرئيسية
    # ==========================================
    
    async def process_message(
        self,
        user_id: int,
        message: str,
        extracted_datetime: Dict = None
    ) -> Dict[str, Any]:
        """
        معالجة رسالة المستخدم
        
        Args:
            user_id: معرف المستخدم
            message: نص الرسالة
            extracted_datetime: التاريخ/الوقت المستخرج مسبقاً (اختياري)
        
        Returns:
            Dict: {
                'intent': النية,
                'confidence': الثقة,
                'state': حالة المحادثة,
                'extracted_info': المعلومات المستخرجة,
                'response': الرد المقترح (اختياري),
                'needs_confirmation': هل يحتاج تأكيد,
                'method': طريقة التصنيف
            }
        """
        try:
            # 1. الحصول على سياق المحادثة
            ctx = self.conversation_manager.get_context(user_id)
            
            # 2. تصنيف النية
            classification = self.intent_classifier.predict(message)
            
            intent = classification['intent']
            confidence = classification['confidence']
            method = classification['method']
            
            # 3. معالجة مع السياق
            processed_intent, extracted_info, new_state = self.context_processor.process_with_context(
                user_id,
                message,
                intent,
                extracted_datetime or {}
            )
            
            # تحديث السياق
            ctx.state = new_state
            ctx.update_activity()
            
            # 4. التحقق من الحاجة للتأكيد
            needs_confirmation = confidence < self.config.request_feedback_below
            
            # 5. توليد رد إذا لزم الأمر
            response = None
            if new_state == ConversationState.AWAITING_CONFIRMATION:
                response = self._generate_confirmation_response(ctx, extracted_info)
            elif new_state in [ConversationState.AWAITING_TIME, 
                              ConversationState.AWAITING_DATE,
                              ConversationState.AWAITING_TITLE]:
                response = self.context_processor.get_missing_info_prompt(ctx)
            
            # 6. حفظ في التاريخ
            ctx.add_turn(message, response or "", processed_intent, extracted_info)
            self.conversation_manager.save_context(user_id)
            
            # 7. تحديث الإحصائيات
            self.feedback_manager.update_performance_stats(intent, True)
            
            return {
                'intent': processed_intent,
                'original_intent': intent,
                'confidence': confidence,
                'state': new_state.value,
                'extracted_info': extracted_info,
                'response': response,
                'needs_confirmation': needs_confirmation,
                'method': method,
                'language': ctx.language
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة الرسالة: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0,
                'state': 'idle',
                'extracted_info': {},
                'error': str(e)
            }
    
    def _generate_confirmation_response(self, ctx: ConversationContext, info: Dict) -> str:
        """توليد رسالة تأكيد"""
        lang = ctx.language
        
        # تنسيق التاريخ والوقت
        date_str = "غير محدد"
        time_str = "غير محدد"
        
        if info.get('date'):
            try:
                date = datetime.fromisoformat(info['date']) if isinstance(info['date'], str) else info['date']
                date_str = date.strftime("%Y-%m-%d")
            except:
                pass
        
        if info.get('time'):
            time_tuple = info['time']
            if isinstance(time_tuple, (list, tuple)) and len(time_tuple) >= 2:
                time_str = f"{time_tuple[0]:02d}:{time_tuple[1]:02d}"
        
        priority_line = ""
        if info.get('priority'):
            priorities = {1: "🔴 عاجل", 2: "🟡 متوسط", 3: "🟢 عادي"}
            priority_line = f"\n⚡ الأولوية: {priorities.get(info['priority'], 'عادي')}"
        
        return self.response_generator.generate(
            'confirm_appointment',
            lang,
            title=info.get('title', 'موعد جديد'),
            date=date_str,
            time=time_str,
            priority_line=priority_line
        )
    
    # ==========================================
    # إدارة التغذية الراجعة
    # ==========================================
    
    async def process_feedback(
        self,
        user_id: int,
        original_message: str,
        predicted_intent: str,
        confidence: float,
        user_response: str
    ) -> Dict:
        """معالجة تغذية راجعة من المستخدم"""
        
        correct_intent = self.auto_learner.process_feedback(
            user_id,
            original_message,
            predicted_intent,
            confidence,
            user_response
        )
        
        return {
            'processed': True,
            'was_correct': correct_intent is None,
            'correct_intent': correct_intent
        }
    
    def record_positive_feedback(self, user_id: int, message: str, intent: str, confidence: float):
        """تسجيل تغذية راجعة إيجابية"""
        entry = FeedbackEntry(
            user_id=user_id,
            message=message,
            predicted_intent=intent,
            predicted_confidence=confidence,
            feedback_type=FeedbackType.POSITIVE
        )
        self.feedback_manager.record_feedback(entry)
    
    def record_correction(self, user_id: int, message: str, 
                         wrong_intent: str, correct_intent: str):
        """تسجيل تصحيح"""
        self.feedback_manager.record_correction(message, wrong_intent, correct_intent, user_id)
    
    # ==========================================
    # إدارة السياق
    # ==========================================
    
    def get_user_context(self, user_id: int) -> Dict:
        """الحصول على سياق المستخدم"""
        ctx = self.conversation_manager.get_context(user_id)
        return ctx.to_dict()
    
    def reset_user_context(self, user_id: int):
        """إعادة تعيين سياق المستخدم"""
        self.conversation_manager.clear_context(user_id)
    
    def get_conversation_history(self, user_id: int, limit: int = 10) -> list:
        """الحصول على تاريخ المحادثة"""
        return self.conversation_manager.get_user_history(user_id, limit)
    
    # ==========================================
    # التدريب والتحسين
    # ==========================================
    
    def train_classifier(self, epochs: int = 50) -> Dict:
        """تدريب مصنف النوايا"""
        print("\n" + "="*70)
        print("🧠 تدريب مصنف النوايا")
        print("="*70)
        
        result = self.intent_classifier.train(epochs=epochs)
        return result
    
    def retrain_with_feedback(self) -> Dict:
        """إعادة التدريب بناءً على التغذية الراجعة"""
        return self.auto_learner.retrain_model()
    
    # ==========================================
    # التقارير والإحصائيات
    # ==========================================
    
    def get_performance_report(self, days: int = 7) -> Dict:
        """الحصول على تقرير الأداء"""
        return self.feedback_manager.get_performance_report(days)
    
    def get_daily_report(self) -> str:
        """تقرير يومي نصي"""
        return self.reporter.generate_daily_report()
    
    def get_weekly_report(self) -> str:
        """تقرير أسبوعي نصي"""
        return self.reporter.generate_weekly_report()
    
    # ==========================================
    # أدوات مساعدة
    # ==========================================
    
    def detect_language(self, text: str) -> str:
        """كشف لغة النص"""
        processor = MultilingualTextProcessor()
        return processor.detect_language(text)
    
    def get_status(self) -> Dict:
        """حالة النظام"""
        return {
            'engine': 'running',
            'classifier': 'bert' if self.config.use_bert else 'lstm',
            'auto_learning': self.config.auto_retrain,
            'corrections_pending': len(self.feedback_manager.get_pending_corrections()),
            'config': self.config.to_dict()
        }
    
    def shutdown(self):
        """إيقاف النظام"""
        if hasattr(self, 'auto_learner'):
            self.auto_learner.stop_monitoring()
        logger.info("🛑 تم إيقاف المحرك الذكي")


# ==========================================
# دوال مساعدة للتكامل
# ==========================================

def create_engine(use_bert: bool = False, auto_retrain: bool = True) -> SmartAIEngine:
    """إنشاء محرك ذكي جاهز للاستخدام"""
    config = EngineConfig()
    config.use_bert = use_bert
    config.auto_retrain = auto_retrain
    
    return SmartAIEngine(config)


# ==========================================
# اختبار
# ==========================================

async def test_engine():
    """اختبار المحرك"""
    print("\n" + "="*70)
    print("🧪 اختبار المحرك الذكي المتكامل")
    print("="*70)
    
    # إنشاء المحرك
    engine = create_engine(use_bert=False, auto_retrain=False)
    
    # تدريب أولي
    print("\n📚 التدريب الأولي...")
    engine.train_classifier(epochs=5)
    
    # اختبار المعالجة
    print("\n" + "─"*70)
    print("🔍 اختبار معالجة الرسائل:")
    print("─"*70)
    
    test_cases = [
        (1, "مرحبا"),
        (1, "موعد غداً الساعة 3"),
        (1, "عرض مواعيدي"),
        (2, "RDV demain à 15h"),
        (2, "Cancel my appointment"),
    ]
    
    for user_id, message in test_cases:
        print(f"\n👤 [{user_id}]: {message}")
        
        result = await engine.process_message(user_id, message)
        
        print(f"   🎯 النية: {result['intent']}")
        print(f"   📊 الثقة: {result['confidence']*100:.0f}%")
        print(f"   📍 الحالة: {result['state']}")
        print(f"   🔧 الطريقة: {result['method']}")
        
        if result.get('response'):
            print(f"   💬 الرد: {result['response'][:100]}...")
    
    # اختبار التغذية الراجعة
    print("\n" + "─"*70)
    print("📝 اختبار التغذية الراجعة:")
    print("─"*70)
    
    # تسجيل تصحيح
    engine.record_correction(1, "عرض", "greeting", "list_appointments")
    print("✅ تم تسجيل تصحيح")
    
    # عرض التقرير
    print("\n" + engine.get_daily_report())
    
    # إيقاف
    engine.shutdown()
    
    print("\n" + "="*70)
    print("✅ الاختبار انتهى بنجاح!")


if __name__ == "__main__":
    asyncio.run(test_engine())
