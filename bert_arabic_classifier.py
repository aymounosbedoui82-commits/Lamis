# bert_arabic_classifier.py
"""
نموذج BERT للعربية - تصنيف نوايا متقدم
✅ يستخدم AraBERT للفهم العميق
✅ دقة عالية جداً
✅ يفهم السياق والمعنى
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple
import numpy as np
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# التحقق من توفر transformers
try:
    from transformers import AutoTokenizer, AutoModel, AutoConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️ مكتبة transformers غير متوفرة - سيتم استخدام النموذج البسيط")


# ==========================================
# 1. نموذج BERT للتصنيف
# ==========================================

class ArabicBERTClassifier(nn.Module):
    """مصنف BERT للعربية"""
    
    def __init__(
        self,
        model_name: str = "aubmindlab/bert-base-arabertv2",
        num_intents: int = 10,
        dropout: float = 0.3,
        freeze_bert: bool = False
    ):
        super(ArabicBERTClassifier, self).__init__()
        
        self.model_name = model_name
        self.num_intents = num_intents
        
        if TRANSFORMERS_AVAILABLE:
            # تحميل BERT
            self.bert = AutoModel.from_pretrained(model_name)
            self.config = self.bert.config
            hidden_size = self.config.hidden_size
            
            # تجميد طبقات BERT (اختياري)
            if freeze_bert:
                for param in self.bert.parameters():
                    param.requires_grad = False
        else:
            # نموذج بديل بسيط
            hidden_size = 256
            self.embedding = nn.Embedding(50000, hidden_size)
            self.lstm = nn.LSTM(hidden_size, hidden_size // 2, bidirectional=True, batch_first=True)
        
        # طبقات التصنيف
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_intents)
        )
    
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        if TRANSFORMERS_AVAILABLE:
            # BERT forward
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            # استخدام [CLS] token
            pooled_output = outputs.last_hidden_state[:, 0, :]
        else:
            # نموذج بديل
            embedded = self.embedding(input_ids)
            lstm_out, _ = self.lstm(embedded)
            pooled_output = lstm_out[:, 0, :]
        
        # التصنيف
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        return logits


# ==========================================
# 2. مجموعة بيانات BERT
# ==========================================

class BERTIntentDataset(Dataset):
    """مجموعة بيانات للتدريب مع BERT"""
    
    INTENT_LABELS = [
        'add_appointment',
        'list_appointments',
        'check_specific_day',
        'cancel_appointment',
        'modify_appointment',
        'set_reminder',
        'greeting',
        'thanks',
        'help',
        'unknown'
    ]
    
    def __init__(
        self,
        tokenizer,
        max_length: int = 64,
        db_path: str = "agent_data.db"
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.db_path = db_path
        
        self.samples = []
        self._load_data()
    
    def _load_data(self):
        """تحميل وتجهيز البيانات"""
        # بيانات تدريب صناعية شاملة
        training_data = {
            'add_appointment': [
                # العربية الفصحى
                "أريد حجز موعد", "موعد غداً", "سجل لي موعد مع الطبيب",
                "أضف موعد جديد", "موعد الساعة الثالثة", "لدي اجتماع غداً",
                "حجز موعد للأسبوع القادم", "موعد يوم الخميس", "اجتماع مهم غداً صباحاً",
                "أريد تحديد موعد", "لقاء مع المدير", "موعد في الساعة 4",
                "سجل موعد عند الطبيب", "موعد فحص طبي", "اجتماع عمل",
                # العربية العامية/التونسية
                "عندي رندي فو", "نحب نسجل موعد", "موعد غدوة", "رندي فو مع الطبيب",
                # الفرنسية
                "RDV demain", "Je voudrais un rendez-vous", "Prendre RDV",
                "Ajouter un rendez-vous", "RDV médecin", "Réunion demain",
                "Planifier une réunion", "RDV à 15h", "Rendez-vous lundi",
                # الإنجليزية
                "Schedule appointment", "Book a meeting", "Appointment tomorrow",
                "Set up meeting", "Doctor appointment", "Meeting at 3pm",
                "I need an appointment", "Book appointment for Monday",
            ],
            'list_appointments': [
                "عرض مواعيدي", "أظهر المواعيد", "ما هي مواعيدي", "كل مواعيدي",
                "قائمة المواعيد", "مواعيدي", "اعرض لي مواعيدي", "شوف المواعيد",
                "Mes rendez-vous", "Afficher mes RDV", "Voir mes RDV", "Liste RDV",
                "Show appointments", "My appointments", "List all appointments",
            ],
            'check_specific_day': [
                "مواعيدي اليوم", "مواعيدي غداً", "ماذا لدي اليوم", "مواعيد يوم الخميس",
                "ما هي مواعيد غداً", "مواعيدي يوم 25", "مواعيد الأسبوع",
                "RDV aujourd'hui", "RDV demain", "Mes RDV du lundi",
                "Today's appointments", "Tomorrow's schedule", "Appointments on Monday",
            ],
            'cancel_appointment': [
                "إلغاء الموعد", "احذف الموعد", "ألغي موعدي", "حذف الموعد رقم 5",
                "إلغاء", "امسح الموعد", "لا أريد الموعد",
                "Annuler le RDV", "Supprimer rendez-vous", "Annuler",
                "Cancel appointment", "Delete meeting", "Remove appointment",
            ],
            'modify_appointment': [
                "تعديل الموعد", "غير الموعد", "تأجيل الموعد", "تقديم الموعد",
                "تغيير وقت الموعد", "تعديل", "غير الساعة",
                "Modifier le RDV", "Changer l'heure", "Reporter le RDV",
                "Change appointment", "Reschedule", "Update meeting time",
            ],
            'set_reminder': [
                "ذكرني", "تذكير قبل 30 دقيقة", "أريد تذكير", "ذكرني بالموعد",
                "تذكير قبل ساعة", "فعل التذكير",
                "Rappelle-moi", "Mettre un rappel", "Rappel avant",
                "Remind me", "Set reminder", "Reminder before",
            ],
            'greeting': [
                "مرحبا", "السلام عليكم", "أهلاً", "صباح الخير", "مساء الخير",
                "هاي", "هلا", "كيف حالك",
                "Bonjour", "Salut", "Bonsoir", "Coucou",
                "Hello", "Hi", "Hey", "Good morning", "Good evening",
            ],
            'thanks': [
                "شكراً", "شكرا جزيلا", "مشكور", "يعطيك العافية", "بارك الله فيك",
                "Merci", "Merci beaucoup", "Merci bien",
                "Thanks", "Thank you", "Thank you so much", "Thanks a lot",
            ],
            'help': [
                "مساعدة", "ساعدني", "كيف أستخدم", "ماذا تستطيع", "الأوامر",
                "كيف أحجز موعد", "شرح", "دليل الاستخدام",
                "Aide", "Comment utiliser", "Comment faire",
                "Help", "How to use", "What can you do", "Commands",
            ],
        }
        
        # تحميل من قاعدة البيانات
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_message, intent FROM interactions
                WHERE intent IS NOT NULL AND intent != ''
                LIMIT 10000
            ''')
            for row in cursor.fetchall():
                if row[1] in self.INTENT_LABELS:
                    self.samples.append((row[0], row[1]))
            conn.close()
        except:
            pass
        
        # إضافة البيانات الصناعية
        for intent, examples in training_data.items():
            for text in examples:
                self.samples.append((text, intent))
        
        logger.info(f"✅ تم تحميل {len(self.samples)} عينة تدريب")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        text, intent = self.samples[idx]
        
        # Tokenization
        if self.tokenizer:
            encoding = self.tokenizer(
                text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            input_ids = encoding['input_ids'].squeeze()
            attention_mask = encoding['attention_mask'].squeeze()
        else:
            # fallback بسيط
            input_ids = torch.zeros(self.max_length, dtype=torch.long)
            attention_mask = torch.ones(self.max_length, dtype=torch.long)
        
        label = self.INTENT_LABELS.index(intent) if intent in self.INTENT_LABELS else len(self.INTENT_LABELS) - 1
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'label': torch.tensor(label, dtype=torch.long)
        }


# ==========================================
# 3. مصنف BERT الذكي
# ==========================================

class SmartBERTClassifier:
    """مصنف BERT الذكي للنوايا"""
    
    MODEL_OPTIONS = {
        'arabert': 'aubmindlab/bert-base-arabertv2',
        'arabert-large': 'aubmindlab/bert-large-arabertv2',
        'camelbert': 'CAMeL-Lab/bert-base-arabic-camelbert-mix',
        'multilingual': 'bert-base-multilingual-cased'
    }
    
    def __init__(
        self,
        model_name: str = 'arabert',
        model_path: str = "models/bert_intent.pth",
        db_path: str = "agent_data.db"
    ):
        self.model_path = model_path
        self.db_path = db_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # اختيار النموذج
        self.bert_model_name = self.MODEL_OPTIONS.get(model_name, model_name)
        
        self.tokenizer = None
        self.model = None
        self.intent_labels = BERTIntentDataset.INTENT_LABELS
        
        self._initialize()
    
    def _initialize(self):
        """تهيئة النموذج"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("⚠️ transformers غير متوفرة - استخدام النموذج البسيط")
            return
        
        try:
            # تحميل Tokenizer
            logger.info(f"📥 جاري تحميل {self.bert_model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
            
            # محاولة تحميل نموذج محفوظ
            if Path(self.model_path).exists():
                self._load_model()
            else:
                logger.info("ℹ️ لا يوجد نموذج محفوظ - جاهز للتدريب")
                
        except Exception as e:
            logger.error(f"❌ خطأ في التهيئة: {e}")
    
    def _load_model(self):
        """تحميل النموذج المحفوظ"""
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            self.model = ArabicBERTClassifier(
                model_name=self.bert_model_name,
                num_intents=len(self.intent_labels)
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ تم تحميل النموذج من {self.model_path}")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل النموذج: {e}")
    
    def train(
        self,
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        warmup_steps: int = 100
    ) -> Dict:
        """تدريب النموذج"""
        if not TRANSFORMERS_AVAILABLE:
            return {'success': False, 'reason': 'transformers not available'}
        
        print("\n" + "="*70)
        print("🧠 تدريب نموذج AraBERT لتصنيف النوايا")
        print("="*70)
        
        # تحميل البيانات
        dataset = BERTIntentDataset(self.tokenizer, db_path=self.db_path)
        
        # تقسيم البيانات
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        print(f"\n📊 البيانات:")
        print(f"   • التدريب: {train_size}")
        print(f"   • التحقق: {val_size}")
        print(f"   • النموذج: {self.bert_model_name}")
        
        # إنشاء النموذج
        self.model = ArabicBERTClassifier(
            model_name=self.bert_model_name,
            num_intents=len(self.intent_labels)
        )
        self.model.to(self.device)
        
        # Optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        # التدريب
        best_val_acc = 0
        history = {'train_loss': [], 'val_acc': []}
        
        print(f"\n{'─'*70}")
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(input_ids, attention_mask)
                loss = criterion(outputs, labels)
                loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # Validation
            self.model.eval()
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['label'].to(self.device)
                    
                    outputs = self.model(input_ids, attention_mask)
                    _, predicted = torch.max(outputs, 1)
                    
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
            
            val_acc = 100 * correct / total
            
            history['train_loss'].append(train_loss)
            history['val_acc'].append(val_acc)
            
            print(f"Epoch {epoch+1}/{epochs} │ Loss: {train_loss:.4f} │ Val Acc: {val_acc:.1f}%", end="")
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self._save_model()
                print(" ⭐")
            else:
                print()
        
        print(f"{'─'*70}")
        print(f"\n🎉 انتهى التدريب! أفضل دقة: {best_val_acc:.1f}%")
        
        return {'success': True, 'best_accuracy': best_val_acc, 'history': history}
    
    def _save_model(self):
        """حفظ النموذج"""
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_name': self.bert_model_name,
            'intent_labels': self.intent_labels,
            'timestamp': datetime.now().isoformat()
        }, self.model_path)
    
    def predict(self, text: str) -> Dict:
        """التنبؤ بالنية"""
        if self.model is None or self.tokenizer is None:
            return self._fallback_predict(text)
        
        try:
            self.model.eval()
            
            # Tokenization
            encoding = self.tokenizer(
                text,
                max_length=64,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask)
                probabilities = torch.softmax(outputs, dim=1)[0]
                confidence, predicted = torch.max(probabilities, 0)
            
            return {
                'intent': self.intent_labels[predicted.item()],
                'confidence': confidence.item(),
                'all_scores': {
                    self.intent_labels[i]: probabilities[i].item()
                    for i in range(len(self.intent_labels))
                },
                'method': 'bert'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في التنبؤ: {e}")
            return self._fallback_predict(text)
    
    def _fallback_predict(self, text: str) -> Dict:
        """تنبؤ احتياطي"""
        text_lower = text.lower()
        
        keywords = {
            'add_appointment': ['موعد', 'اجتماع', 'rdv', 'rendez', 'appointment', 'meeting', 'schedule'],
            'list_appointments': ['عرض', 'مواعيدي', 'afficher', 'mes rdv', 'show', 'list', 'appointments'],
            'cancel_appointment': ['إلغاء', 'حذف', 'annuler', 'cancel', 'delete'],
            'greeting': ['مرحبا', 'السلام', 'bonjour', 'salut', 'hello', 'hi'],
            'thanks': ['شكر', 'merci', 'thank'],
            'help': ['مساعدة', 'aide', 'help', 'how']
        }
        
        best_intent = 'unknown'
        best_score = 0
        
        for intent, kws in keywords.items():
            score = sum(1 for kw in kws if kw in text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return {
            'intent': best_intent,
            'confidence': min(best_score * 0.3, 0.9),
            'all_scores': {},
            'method': 'fallback'
        }


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار نموذج AraBERT")
    print("="*70)
    
    classifier = SmartBERTClassifier(model_name='multilingual')
    
    # اختبار بدون تدريب
    test_texts = [
        "موعد غداً الساعة 3",
        "عرض مواعيدي",
        "مرحبا",
        "RDV demain à 15h",
        "Cancel my appointment"
    ]
    
    print("\n🔍 اختبار التنبؤ:")
    for text in test_texts:
        result = classifier.predict(text)
        print(f"\n'{text}'")
        print(f"  → {result['intent']} ({result['confidence']*100:.0f}%) [{result['method']}]")
