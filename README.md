# 🧠 Lamis Bot - نظام الذكاء الاصطناعي المتقدم

## 📋 المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [المميزات الجديدة](#المميزات-الجديدة)
3. [التثبيت](#التثبيت)
4. [البنية المعمارية](#البنية-المعمارية)
5. [الاستخدام](#الاستخدام)
6. [التكامل](#التكامل)
7. [التدريب](#التدريب)
8. [API Reference](#api-reference)

---

## 🌟 نظرة عامة

نظام ذكاء اصطناعي متقدم لـ Lamis Bot يوفر:

| الميزة | الوصف |
|--------|-------|
| 🎯 تصنيف ذكي | ML/BERT بدلاً من Keywords |
| 💬 فهم السياق | محادثات متعددة الأدوار |
| 📚 تعلم مستمر | يتحسن من الأخطاء |
| 🌍 متعدد اللغات | عربي، فرنسي، إنجليزي |

---

## ✨ المميزات الجديدة

### 1. تصنيف النوايا بـ Machine Learning

**قبل (Rule-Based):**
```python
# ❌ الطريقة القديمة
if any(kw in message for kw in ['موعد', 'rdv']):
    intent = 'add_appointment'
```

**بعد (ML-Based):**
```python
# ✅ الطريقة الجديدة
result = classifier.predict("أريد حجز موعد مع الطبيب")
# → intent: 'add_appointment', confidence: 0.94
```

### 2. فهم سياق المحادثة

```
👤 المستخدم: موعد مع الطبيب
🤖 البوت: في أي ساعة تريد الموعد؟

👤 المستخدم: 3 العصر
🤖 البوت: في أي يوم؟

👤 المستخدم: غداً
🤖 البوت: ✅ تأكيد الموعد:
         📋 موعد مع الطبيب
         📅 غداً
         ⏰ 15:00
```

### 3. التعلم من التغذية الراجعة

```python
# عندما يصحح المستخدم خطأ
engine.record_correction(
    user_id=123,
    message="عرض",
    wrong_intent="greeting",
    correct_intent="list_appointments"
)

# النظام يتعلم ويتحسن تلقائياً
```

### 4. نموذج BERT للعربية (اختياري)

```python
# للدقة القصوى
engine = SmartAIEngine(config)
config.use_bert = True  # يستخدم AraBERT
```

---

## 📦 التثبيت

### المتطلبات

```bash
# Python 3.8+
pip install -r requirements.txt
```

### requirements.txt

```
torch>=1.9.0
numpy>=1.19.0
transformers>=4.0.0  # اختياري لـ BERT
```

### التثبيت السريع

```bash
# 1. نسخ الملفات
cp *.py /path/to/lamis_bot/

# 2. تثبيت المتطلبات
pip install torch numpy

# 3. تدريب النموذج
python -c "
from smart_ai_engine import create_engine
engine = create_engine()
engine.train_classifier(epochs=20)
"
```

---

## 🏗️ البنية المعمارية

```
lamis_bot/
├── smart_ai_engine.py      # 🧠 المحرك الرئيسي
├── ml_intent_classifier.py # 🎯 مصنف LSTM
├── bert_arabic_classifier.py # 🔤 مصنف BERT
├── conversation_context.py # 💬 إدارة السياق
├── feedback_learning_system.py # 📚 نظام التعلم
├── integration.py          # 🔗 التكامل مع البوت
└── models/
    ├── intent_classifier.pth
    └── text_processor.pkl
```

### مخطط التدفق

```
رسالة المستخدم
       ↓
┌─────────────────┐
│ استخراج الوقت   │
│ والتاريخ        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ تصنيف النية     │◄── ML/BERT
│ (Intent)        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ معالجة السياق   │◄── تاريخ المحادثة
└────────┬────────┘
         ↓
┌─────────────────┐
│ تنفيذ الإجراء   │
└────────┬────────┘
         ↓
    الرد للمستخدم
```

---

## 🚀 الاستخدام

### الاستخدام الأساسي

```python
from smart_ai_engine import create_engine
import asyncio

# إنشاء المحرك
engine = create_engine()

# معالجة رسالة
async def main():
    result = await engine.process_message(
        user_id=123,
        message="موعد غداً الساعة 3"
    )
    
    print(f"النية: {result['intent']}")
    print(f"الثقة: {result['confidence']}")
    print(f"الحالة: {result['state']}")

asyncio.run(main())
```

### مع التكامل

```python
from integration import SmartMessageHandler

handler = SmartMessageHandler()

# تصنيف فقط
intent, confidence = handler.classify_intent("عرض مواعيدي")

# معالجة كاملة
result = await handler.handle(user_id=123, message="موعد غداً")
```

---

## 🔗 التكامل مع البوت الحالي

### الخطوة 1: استيراد المعالج

```python
# في ملف البوت الرئيسي
from integration import SmartMessageHandler

handler = SmartMessageHandler(db_path="agent_data.db")
```

### الخطوة 2: استبدال handle_message

```python
@bot.message_handler(func=lambda m: True)
async def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    # المعالجة الذكية
    result = await handler.handle(user_id, text)
    
    # تنفيذ الإجراء حسب النتيجة
    action = result['action']
    
    if action == 'create_appointment':
        # إنشاء موعد
        info = result['extracted_info']
        await create_appointment(user_id, info)
        
    elif action == 'show_appointments':
        # عرض المواعيد
        await show_user_appointments(user_id)
        
    elif action == 'await_confirmation':
        # انتظار تأكيد
        await bot.send_message(
            message.chat.id,
            result['response']
        )
    
    # إذا كان هناك رد جاهز
    elif result.get('response'):
        await bot.send_message(
            message.chat.id,
            result['response']
        )
```

### الخطوة 3: تسجيل التغذية الراجعة

```python
# عند الضغط على زر 👍
@bot.callback_query_handler(func=lambda c: c.data.startswith('feedback_'))
async def handle_feedback(call):
    data = call.data.split('_')
    is_correct = data[1] == 'positive'
    
    handler.record_feedback(
        user_id=call.from_user.id,
        message=original_message,
        intent=predicted_intent,
        is_correct=is_correct
    )
```

---

## 🎓 التدريب

### التدريب الأولي

```python
from smart_ai_engine import create_engine

engine = create_engine()

# تدريب مع 20 epoch
result = engine.train_classifier(epochs=20)

print(f"الدقة: {result['best_accuracy']:.1f}%")
```

### إعادة التدريب بالتصحيحات

```python
# يدوياً
engine.retrain_with_feedback()

# أو تلقائياً (كل 50 تصحيح)
config.auto_retrain = True
config.retrain_threshold = 50
```

### مراقبة الأداء

```python
# تقرير يومي
print(engine.get_daily_report())

# تقرير أسبوعي
print(engine.get_weekly_report())

# إحصائيات مفصلة
stats = engine.get_performance_report(days=7)
print(f"الدقة الإجمالية: {stats['overall_accuracy']:.1f}%")
```

---

## 📚 API Reference

### SmartAIEngine

```python
class SmartAIEngine:
    # معالجة رسالة
    async def process_message(user_id: int, message: str) -> Dict
    
    # تدريب
    def train_classifier(epochs: int = 20) -> Dict
    def retrain_with_feedback() -> Dict
    
    # السياق
    def get_user_context(user_id: int) -> Dict
    def reset_user_context(user_id: int)
    
    # التغذية الراجعة
    def record_positive_feedback(user_id, message, intent, confidence)
    def record_correction(user_id, message, wrong_intent, correct_intent)
    
    # التقارير
    def get_performance_report(days: int = 7) -> Dict
    def get_daily_report() -> str
```

### نتيجة process_message

```python
{
    'intent': str,           # النية المكتشفة
    'confidence': float,     # نسبة الثقة (0-1)
    'state': str,           # حالة المحادثة
    'extracted_info': {     # المعلومات المستخرجة
        'title': str,
        'date': datetime,
        'time': (hour, minute)
    },
    'response': str,        # الرد المقترح
    'action': str,          # الإجراء المطلوب
    'method': str           # 'ml' أو 'bert' أو 'fallback'
}
```

### حالات المحادثة

| الحالة | الوصف |
|--------|-------|
| `idle` | خامل |
| `awaiting_time` | ينتظر الوقت |
| `awaiting_date` | ينتظر التاريخ |
| `awaiting_title` | ينتظر العنوان |
| `awaiting_confirmation` | ينتظر تأكيد |

### النوايا المدعومة

| النية | الوصف | أمثلة |
|-------|-------|-------|
| `add_appointment` | إضافة موعد | موعد غداً، RDV demain |
| `list_appointments` | عرض المواعيد | مواعيدي، Mes RDV |
| `check_specific_day` | مواعيد يوم | مواعيدي اليوم |
| `cancel_appointment` | إلغاء | إلغاء الموعد |
| `modify_appointment` | تعديل | تغيير الموعد |
| `greeting` | تحية | مرحبا، Bonjour |
| `thanks` | شكر | شكراً، Merci |
| `help` | مساعدة | مساعدة، Help |

---

## 🔧 الإعدادات

```python
class EngineConfig:
    # قاعدة البيانات
    db_path = "agent_data.db"
    models_dir = "models"
    
    # ML
    use_bert = False          # True لاستخدام BERT
    confidence_threshold = 0.6
    
    # السياق
    context_timeout_minutes = 30
    max_history_size = 10
    
    # التعلم التلقائي
    auto_retrain = True
    retrain_threshold = 50    # تصحيحات قبل إعادة التدريب
```

---

## 📊 مقارنة الأداء

| المقياس | النظام القديم | النظام الجديد |
|---------|---------------|---------------|
| دقة التصنيف | ~60% | ~90%+ |
| فهم السياق | ❌ | ✅ |
| التعلم الذاتي | ❌ | ✅ |
| اللغات | 3 | 3 |
| سرعة الاستجابة | سريع | سريع (LSTM) / متوسط (BERT) |

---

## 🆘 حل المشاكل

### خطأ: No module named 'torch'
```bash
pip install torch
```

### خطأ: Model not found
```python
# تدريب النموذج أولاً
engine.train_classifier(epochs=20)
```

### دقة منخفضة
```python
# زيادة بيانات التدريب
# أو استخدام BERT
config.use_bert = True
```

---

## 📝 الترخيص

MIT License - استخدام حر مع ذكر المصدر.

---

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء branch جديد
3. إضافة التحسينات
4. Pull Request

---

**صنع بـ ❤️ لـ Lamis Bot**
