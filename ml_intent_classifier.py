# ml_intent_classifier.py
"""
نظام تصنيف النوايا الذكي باستخدام Machine Learning
✅ تصنيف حقيقي بدلاً من Keywords
✅ يتعلم من التفاعلات السابقة
✅ يدعم 3 لغات
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sqlite3
import json
import re
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ==========================================
# 1. معالجة النصوص متعددة اللغات
# ==========================================

class MultilingualTextProcessor:
    """معالج نصوص متعدد اللغات"""
    
    def __init__(self, max_vocab_size: int = 10000, max_seq_length: int = 50):
        self.max_vocab_size = max_vocab_size
        self.max_seq_length = max_seq_length
        
        # القاموس
        self.word2idx = {'<PAD>': 0, '<UNK>': 1, '<SOS>': 2, '<EOS>': 3}
        self.idx2word = {0: '<PAD>', 1: '<UNK>', 2: '<SOS>', 3: '<EOS>'}
        self.word_counts = Counter()
        
        # أنماط التنظيف
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        self.french_pattern = re.compile(r'[a-zA-Zàâäéèêëïîôùûüÿç]+')
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        self.number_pattern = re.compile(r'\d+')
        
        # Stop words بسيطة
        self.stop_words = {
            'ar': {'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'و', 'أو', 'ثم'},
            'fr': {'le', 'la', 'les', 'de', 'du', 'à', 'au', 'en', 'et', 'ou', 'un', 'une'},
            'en': {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'is', 'are'}
        }
    
    def detect_language(self, text: str) -> str:
        """كشف لغة النص"""
        arabic_chars = len(self.arabic_pattern.findall(text))
        latin_chars = len(self.french_pattern.findall(text))
        
        if arabic_chars > latin_chars:
            return 'ar'
        
        # التفريق بين الفرنسية والإنجليزية
        french_indicators = ['je', 'tu', 'il', 'nous', 'vous', 'rdv', 'rendez', 'demain', 'aujourd']
        if any(ind in text.lower() for ind in french_indicators):
            return 'fr'
        
        return 'en'
    
    def normalize_arabic(self, text: str) -> str:
        """توحيد الأحرف العربية"""
        # توحيد الهمزات
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'[ؤئ]', 'ء', text)
        # إزالة التشكيل
        text = re.sub(r'[\u064B-\u065F]', '', text)
        # توحيد التاء المربوطة والهاء
        text = re.sub(r'ة', 'ه', text)
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """تقسيم النص إلى كلمات"""
        text = text.lower()
        language = self.detect_language(text)
        
        # تنظيف النص
        if language == 'ar':
            text = self.normalize_arabic(text)
        
        # استخراج الكلمات
        words = re.findall(r'[\u0600-\u06FF]+|[a-zA-Zàâäéèêëïîôùûüÿç]+|\d+', text)
        
        # إزالة stop words
        stop = self.stop_words.get(language, set())
        words = [w for w in words if w not in stop and len(w) > 1]
        
        return words
    
    def build_vocabulary(self, texts: List[str]):
        """بناء القاموس من النصوص"""
        for text in texts:
            tokens = self.tokenize(text)
            self.word_counts.update(tokens)
        
        # اختيار أكثر الكلمات شيوعاً
        most_common = self.word_counts.most_common(self.max_vocab_size - 4)
        
        for idx, (word, _) in enumerate(most_common, start=4):
            self.word2idx[word] = idx
            self.idx2word[idx] = word
        
        logger.info(f"✅ تم بناء قاموس بـ {len(self.word2idx)} كلمة")
    
    def encode(self, text: str) -> torch.Tensor:
        """تحويل النص إلى tensor"""
        tokens = self.tokenize(text)
        
        # تحويل إلى indices
        indices = [self.word2idx.get(token, 1) for token in tokens]  # 1 = <UNK>
        
        # Padding أو Truncation
        if len(indices) < self.max_seq_length:
            indices = indices + [0] * (self.max_seq_length - len(indices))
        else:
            indices = indices[:self.max_seq_length]
        
        return torch.tensor(indices, dtype=torch.long)
    
    def save(self, path: str):
        """حفظ المعالج"""
        data = {
            'word2idx': self.word2idx,
            'idx2word': self.idx2word,
            'max_seq_length': self.max_seq_length
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path: str):
        """تحميل المعالج"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.word2idx = data['word2idx']
        self.idx2word = data['idx2word']
        self.max_seq_length = data['max_seq_length']


# ==========================================
# 2. نموذج تصنيف النوايا
# ==========================================

class IntentClassifierLSTM(nn.Module):
    """نموذج LSTM لتصنيف النوايا"""
    
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        num_intents: int = 10,
        dropout: float = 0.3
    ):
        super(IntentClassifierLSTM, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_dim * 2, 1)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_intents)
        
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_dim)
    
    def attention_weights(self, lstm_output: torch.Tensor) -> torch.Tensor:
        """حساب أوزان Attention"""
        # lstm_output: (batch, seq_len, hidden*2)
        attention_scores = self.attention(lstm_output)  # (batch, seq_len, 1)
        attention_weights = F.softmax(attention_scores, dim=1)
        return attention_weights
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Returns:
            logits: (batch, num_intents)
            attention_weights: (batch, seq_len, 1)
        """
        # Embedding
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)
        embedded = self.dropout(embedded)
        
        # LSTM
        lstm_out, _ = self.lstm(embedded)  # (batch, seq_len, hidden*2)
        
        # Attention
        attn_weights = self.attention_weights(lstm_out)
        
        # Weighted sum
        context = torch.sum(attn_weights * lstm_out, dim=1)  # (batch, hidden*2)
        
        # Classification
        x = self.dropout(context)
        x = F.relu(self.fc1(x))
        x = self.layer_norm(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        
        return logits, attn_weights


class IntentClassifierCNN(nn.Module):
    """نموذج CNN لتصنيف النوايا (أسرع)"""
    
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        num_filters: int = 100,
        filter_sizes: List[int] = [2, 3, 4, 5],
        num_intents: int = 10,
        dropout: float = 0.5
    ):
        super(IntentClassifierCNN, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # Multiple CNN filters
        self.convs = nn.ModuleList([
            nn.Conv1d(embedding_dim, num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        
        self.fc = nn.Linear(num_filters * len(filter_sizes), num_intents)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Embedding
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)
        embedded = embedded.permute(0, 2, 1)  # (batch, embed_dim, seq_len)
        
        # CNN + MaxPool
        conv_outputs = []
        for conv in self.convs:
            conv_out = F.relu(conv(embedded))  # (batch, num_filters, *)
            pooled = F.max_pool1d(conv_out, conv_out.size(2)).squeeze(2)
            conv_outputs.append(pooled)
        
        # Concatenate
        concat = torch.cat(conv_outputs, dim=1)  # (batch, num_filters * len(filter_sizes))
        
        # Dropout + FC
        x = self.dropout(concat)
        logits = self.fc(x)
        
        return logits


# ==========================================
# 3. مجموعة البيانات
# ==========================================

class IntentDataset(Dataset):
    """مجموعة بيانات النوايا"""
    
    INTENT_LABELS = [
        'add_appointment',      # إضافة موعد
        'list_appointments',    # عرض المواعيد
        'check_specific_day',   # مواعيد يوم محدد
        'cancel_appointment',   # إلغاء موعد
        'modify_appointment',   # تعديل موعد
        'set_reminder',         # تعيين تذكير
        'greeting',             # تحية
        'thanks',               # شكر
        'help',                 # مساعدة
        'unknown'               # غير معروف
    ]
    
    def __init__(
        self,
        db_path: str = "agent_data.db",
        processor: MultilingualTextProcessor = None,
        augment: bool = True
    ):
        self.db_path = db_path
        self.processor = processor or MultilingualTextProcessor()
        self.augment = augment
        
        self.samples = []
        self.labels = []
        
        self._load_from_database()
        self._add_synthetic_data()
        
        if not self.processor.word2idx or len(self.processor.word2idx) <= 4:
            texts = [s for s, _ in self.samples]
            self.processor.build_vocabulary(texts)
    
    def _load_from_database(self):
        """تحميل البيانات من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, intent, feedback
                FROM interactions
                WHERE intent IS NOT NULL AND intent != ''
                ORDER BY timestamp DESC
                LIMIT 50000
            ''')
            
            for row in cursor.fetchall():
                message, intent, feedback = row
                if intent in self.INTENT_LABELS:
                    # إعطاء وزن أكبر للتفاعلات ذات feedback إيجابي
                    weight = 1 + (feedback or 0) * 0.2
                    for _ in range(int(weight)):
                        self.samples.append((message, intent))
            
            conn.close()
            logger.info(f"✅ تم تحميل {len(self.samples)} تفاعل من قاعدة البيانات")
            
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تحميل البيانات: {e}")
    
    def _add_synthetic_data(self):
        """إضافة بيانات تدريب صناعية موسعة"""
        synthetic_data = {
            'add_appointment': [
                # العربية - أكثر تنوعاً
                "موعد غداً الساعة 3",
                "أريد حجز موعد",
                "سجل لي موعد مع الطبيب",
                "عندي اجتماع بكرة",
                "موعد يوم الخميس الساعة 10",
                "لدي لقاء مهم غداً",
                "أضف موعد جديد",
                "سجل موعد الساعة 5 مساء",
                "موعد مع المدير غداً صباحاً",
                "حجز موعد للأسبوع القادم",
                "موعد",
                "اجتماع",
                "لقاء",
                "مقابلة",
                "أريد موعد",
                "احتاج موعد",
                "سجل موعد",
                "أضف اجتماع",
                "موعد جديد",
                "حجز جديد",
                "موعد الساعة 4",
                "اجتماع الساعة 2",
                "موعد صباحاً",
                "موعد مساءً",
                "موعد بعد الظهر",
                "اجتماع عمل",
                "لقاء عمل",
                "موعد طبيب",
                "موعد دكتور",
                "موعد مستشفى",
                "اجتماع مع الفريق",
                "لقاء مع العميل",
                # التونسية
                "عندي رندي فو غدوة",
                "نحب نسجل موعد",
                "رندي فو",
                "عندي رندي فو",
                "نحب نحجز موعد",
                # الفرنسية
                "RDV demain à 15h",
                "Je voudrais prendre rendez-vous",
                "Réunion lundi matin",
                "Ajouter un rendez-vous",
                "RDV médecin demain",
                "Planifier une réunion",
                "rdv",
                "rendez-vous",
                "prendre rdv",
                "nouveau rdv",
                "ajouter rdv",
                "réunion",
                "rdv à 14h",
                "rdv à 15h",
                "rdv demain",
                "rdv lundi",
                "je veux un rdv",
                "je voudrais un rdv",
                # الإنجليزية
                "Appointment tomorrow at 3pm",
                "Schedule a meeting",
                "Book an appointment",
                "I have a meeting tomorrow",
                "Set up appointment for Monday",
                "appointment",
                "meeting",
                "schedule",
                "book",
                "new appointment",
                "add meeting",
                "create appointment",
                "i need an appointment",
                "i want to schedule",
                "meeting at 3",
                "appointment at 2pm",
            ],
            'list_appointments': [
                "عرض مواعيدي",
                "ما هي مواعيدي",
                "أظهر المواعيد",
                "مواعيدي",
                "كل مواعيدي",
                "شوف مواعيدي",
                "اعرض المواعيد",
                "قائمة المواعيد",
                "عرض",
                "أظهر",
                "قائمة",
                "المواعيد",
                "جميع مواعيدي",
                "كل المواعيد",
                "أرني مواعيدي",
                "وريني مواعيدي",
                "شو عندي مواعيد",
                "Afficher mes RDV",
                "Mes rendez-vous",
                "Voir mes RDV",
                "mes rdv",
                "afficher rdv",
                "voir rdv",
                "liste rdv",
                "tous mes rdv",
                "montrer mes rdv",
                "Show my appointments",
                "List all appointments",
                "My appointments",
                "What are my appointments",
                "show appointments",
                "list appointments",
                "my schedule",
                "view appointments",
                "see my appointments",
                "all my appointments",
            ],
            'check_specific_day': [
                "مواعيدي اليوم",
                "مواعيدي غداً",
                "ما هي مواعيد اليوم",
                "مواعيد يوم الخميس",
                "ماذا لدي غداً",
                "مواعيدي يوم 25 مارس",
                "مواعيد اليوم",
                "مواعيد غداً",
                "مواعيد بكرة",
                "ماذا عندي اليوم",
                "شو عندي اليوم",
                "ايش عندي بكرة",
                "Mes RDV aujourd'hui",
                "RDV de demain",
                "Mes rendez-vous du lundi",
                "rdv aujourd'hui",
                "rdv demain",
                "mes rdv de demain",
                "Today's appointments",
                "What do I have tomorrow",
                "Appointments on Monday",
                "today appointments",
                "tomorrow schedule",
                "what's on my schedule today",
                "appointments today",
                "appointments tomorrow",
            ],
            'cancel_appointment': [
                "إلغاء الموعد",
                "احذف الموعد",
                "ألغي موعد الطبيب",
                "حذف الموعد رقم 5",
                "إلغاء موعد الغد",
                "إلغاء",
                "الغاء",
                "حذف",
                "امسح",
                "شيل",
                "ألغي",
                "احذف",
                "امحي",
                "إلغاء موعد",
                "حذف موعد",
                "ألغي الموعد",
                "لا أريد الموعد",
                "Annuler le RDV",
                "Supprimer rendez-vous",
                "annuler",
                "supprimer",
                "annuler rdv",
                "supprimer rdv",
                "Cancel the appointment",
                "Delete appointment",
                "Remove meeting",
                "cancel",
                "delete",
                "remove",
                "cancel appointment",
                "delete meeting",
                "remove appointment",
            ],
            'modify_appointment': [
                "تعديل الموعد",
                "غير موعد الطبيب",
                "تأجيل الموعد",
                "تقديم الموعد",
                "تغيير وقت الموعد",
                "تعديل",
                "تغيير",
                "تأجيل",
                "تقديم",
                "غير",
                "عدل",
                "بدل",
                "غير الموعد",
                "عدل الموعد",
                "بدل الموعد",
                "Modifier le RDV",
                "Changer l'heure",
                "modifier",
                "changer",
                "reporter",
                "modifier rdv",
                "changer rdv",
                "Change appointment time",
                "Reschedule meeting",
                "Update appointment",
                "change",
                "modify",
                "reschedule",
                "update",
                "change appointment",
                "modify meeting",
            ],
            'set_reminder': [
                "ذكرني قبل 30 دقيقة",
                "ذكرني بالموعد",
                "أريد تذكير",
                "تذكير قبل ساعة",
                "ذكرني",
                "تذكير",
                "فعل التذكير",
                "أريد تنبيه",
                "نبهني",
                "Rappelle-moi avant",
                "Mettre un rappel",
                "rappel",
                "rappelle-moi",
                "Remind me before",
                "Set a reminder",
                "reminder",
                "remind me",
                "set reminder",
                "notify me",
            ],
            'greeting': [
                "مرحبا",
                "السلام عليكم",
                "صباح الخير",
                "مساء الخير",
                "أهلا",
                "هاي",
                "هلا",
                "اهلين",
                "سلام",
                "مرحبا كيفك",
                "كيف الحال",
                "شلونك",
                "كيفك",
                "أهلا وسهلا",
                "يا هلا",
                "Bonjour",
                "Salut",
                "Bonsoir",
                "Coucou",
                "Bonne journée",
                "Hello",
                "Hi",
                "Hey",
                "Good morning",
                "Good evening",
                "Good afternoon",
                "Hi there",
                "Hello there",
                "Howdy",
            ],
            'thanks': [
                "شكرا",
                "شكراً جزيلاً",
                "مشكور",
                "يعطيك العافية",
                "تسلم",
                "الله يعطيك العافية",
                "جزاك الله خير",
                "ممنون",
                "شكرا لك",
                "Merci",
                "Merci beaucoup",
                "Merci bien",
                "Thanks",
                "Thank you",
                "Thank you so much",
                "Thanks a lot",
                "Many thanks",
                "Appreciated",
            ],
            'help': [
                "مساعدة",
                "ساعدني",
                "كيف أستخدم البوت",
                "ماذا يمكنك فعله",
                "المساعدة",
                "أحتاج مساعدة",
                "كيف",
                "شلون",
                "كيف أسوي",
                "كيف أعمل",
                "الأوامر",
                "ماذا تفعل",
                "شو بتعرف تسوي",
                "ايش تقدر تسوي",
                "Aide",
                "Comment utiliser",
                "aide-moi",
                "comment faire",
                "qu'est-ce que tu fais",
                "Help",
                "How to use",
                "What can you do",
                "help me",
                "how do i",
                "instructions",
                "commands",
                "what do you do",
            ],
        }
        
        for intent, examples in synthetic_data.items():
            for example in examples:
                self.samples.append((example, intent))
                
                # Data augmentation - إضافة نسخ متعددة
                if self.augment:
                    # إضافة اختلافات طفيفة
                    for _ in range(3):  # 3 نسخ إضافية لكل مثال
                        augmented = self._augment_text(example)
                        self.samples.append((augmented, intent))
        
        logger.info(f"✅ إجمالي العينات: {len(self.samples)}")
    
    def _augment_text(self, text: str) -> str:
        """توسيع البيانات بتنوع أكبر"""
        import random
        
        augmentations = [
            lambda t: t.lower(),
            lambda t: t.upper(),
            lambda t: t.capitalize(),
            lambda t: t + ".",
            lambda t: t + "؟" if any(c in t for c in 'ءأإآؤئ') else t + "?",
            lambda t: t + "!",
            lambda t: " ".join(t.split()),  # إزالة المسافات الزائدة
            lambda t: t.strip(),
            lambda t: "  " + t,  # مسافات في البداية
            lambda t: t + "  ",  # مسافات في النهاية
            lambda t: t.replace("ا", "أ") if "ا" in t else t,
            lambda t: t.replace("أ", "ا") if "أ" in t else t,
            lambda t: t.replace("ة", "ه") if "ة" in t else t,
        ]
        
        # اختيار 1-2 تحويلات عشوائية
        num_augs = random.randint(1, 2)
        result = text
        for _ in range(num_augs):
            aug_func = random.choice(augmentations)
            result = aug_func(result)
        
        return result
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        text, intent = self.samples[idx]
        
        # تحويل النص
        encoded = self.processor.encode(text)
        
        # تحويل النية إلى رقم
        label = self.INTENT_LABELS.index(intent) if intent in self.INTENT_LABELS else len(self.INTENT_LABELS) - 1
        
        return encoded, torch.tensor(label, dtype=torch.long)


# ==========================================
# 4. المصنف الذكي
# ==========================================

class SmartIntentClassifier:
    """مصنف النوايا الذكي"""
    
    def __init__(
        self,
        model_path: str = "models/intent_classifier.pth",
        processor_path: str = "models/text_processor.pkl",
        db_path: str = "agent_data.db",
        model_type: str = "lstm"  # "lstm" or "cnn"
    ):
        self.model_path = model_path
        self.processor_path = processor_path
        self.db_path = db_path
        self.model_type = model_type
        
        self.processor = MultilingualTextProcessor()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.intent_labels = IntentDataset.INTENT_LABELS
        
        # محاولة تحميل نموذج موجود
        self._load_model()
    
    def _load_model(self):
        """تحميل النموذج المحفوظ"""
        try:
            if Path(self.processor_path).exists():
                self.processor.load(self.processor_path)
                logger.info("✅ تم تحميل معالج النصوص")
            
            if Path(self.model_path).exists():
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                vocab_size = len(self.processor.word2idx)
                num_intents = len(self.intent_labels)
                
                if self.model_type == "lstm":
                    self.model = IntentClassifierLSTM(vocab_size, num_intents=num_intents)
                else:
                    self.model = IntentClassifierCNN(vocab_size, num_intents=num_intents)
                
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.to(self.device)
                self.model.eval()
                
                logger.info(f"✅ تم تحميل النموذج من {self.model_path}")
            else:
                logger.info("ℹ️ لا يوجد نموذج محفوظ - سيتم التدريب عند الطلب")
                
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تحميل النموذج: {e}")
    
    def train(
        self,
        epochs: int = 50,
        batch_size: int = 16,
        learning_rate: float = 0.002,
        validation_split: float = 0.15
    ) -> Dict:
        """تدريب النموذج"""
        print("\n" + "="*70)
        print("🧠 بدء تدريب نموذج تصنيف النوايا")
        print("="*70)
        
        # تحميل البيانات
        dataset = IntentDataset(self.db_path, self.processor)
        
        if len(dataset) < 50:
            print(f"\n❌ البيانات غير كافية: {len(dataset)} عينة (الحد الأدنى: 50)")
            return {'success': False, 'reason': 'insufficient_data'}
        
        # تقسيم البيانات
        train_size = int((1 - validation_split) * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        print(f"\n📊 البيانات:")
        print(f"   • التدريب: {train_size} عينة")
        print(f"   • التحقق: {val_size} عينة")
        print(f"   • النوايا: {len(self.intent_labels)}")
        
        # إنشاء النموذج
        vocab_size = len(self.processor.word2idx)
        
        if self.model_type == "lstm":
            self.model = IntentClassifierLSTM(vocab_size, num_intents=len(self.intent_labels))
        else:
            self.model = IntentClassifierCNN(vocab_size, num_intents=len(self.intent_labels))
        
        self.model.to(self.device)
        
        # Optimizer و Loss
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3)
        criterion = nn.CrossEntropyLoss()
        
        # التدريب
        history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
        best_val_acc = 0
        
        print(f"\n{'─'*70}")
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            
            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                
                if self.model_type == "lstm":
                    outputs, _ = self.model(batch_x)
                else:
                    outputs = self.model(batch_x)
                
                loss = criterion(outputs, batch_y)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # Validation
            self.model.eval()
            val_loss = 0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    if self.model_type == "lstm":
                        outputs, _ = self.model(batch_x)
                    else:
                        outputs = self.model(batch_x)
                    
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
                    
                    _, predicted = torch.max(outputs, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
            
            val_loss /= len(val_loader)
            val_acc = 100 * correct / total
            
            scheduler.step(val_loss)
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            # طباعة التقدم
            print(f"Epoch {epoch+1:3d}/{epochs} │ "
                  f"Train Loss: {train_loss:.4f} │ "
                  f"Val Loss: {val_loss:.4f} │ "
                  f"Val Acc: {val_acc:.1f}%", end="")
            
            # حفظ أفضل نموذج
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self._save_model()
                print(" ⭐ Best!")
            else:
                print()
        
        print(f"{'─'*70}")
        print(f"\n🎉 انتهى التدريب!")
        print(f"⭐ أفضل دقة: {best_val_acc:.1f}%")
        
        return {
            'success': True,
            'best_accuracy': best_val_acc,
            'history': history
        }
    
    def _save_model(self):
        """حفظ النموذج"""
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_type': self.model_type,
            'intent_labels': self.intent_labels,
            'timestamp': datetime.now().isoformat()
        }, self.model_path)
        
        self.processor.save(self.processor_path)
        logger.info(f"✅ تم حفظ النموذج في {self.model_path}")
    
    def predict(self, text: str) -> Dict:
        """
        التنبؤ بنية النص
        
        Returns:
            dict: {
                'intent': النية المتوقعة,
                'confidence': نسبة الثقة,
                'all_scores': جميع النتائج,
                'method': 'ml' أو 'fallback'
            }
        """
        # إذا لم يكن هناك نموذج، استخدم القواعد
        if self.model is None:
            return self._rule_based_classify(text)
        
        try:
            self.model.eval()
            
            with torch.no_grad():
                encoded = self.processor.encode(text).unsqueeze(0).to(self.device)
                
                if self.model_type == "lstm":
                    outputs, attention = self.model(encoded)
                else:
                    outputs = self.model(encoded)
                
                probabilities = F.softmax(outputs, dim=1)[0]
                confidence, predicted = torch.max(probabilities, 0)
                
                # تحويل إلى dict
                all_scores = {
                    self.intent_labels[i]: probabilities[i].item()
                    for i in range(len(self.intent_labels))
                }
                
                predicted_intent = self.intent_labels[predicted.item()]
                confidence_score = confidence.item()
                
                # إذا كانت الثقة منخفضة، استخدم القواعد كـ fallback
                if confidence_score < 0.5:
                    rule_result = self._rule_based_classify(text)
                    if rule_result['confidence'] > confidence_score:
                        return rule_result
                
                return {
                    'intent': predicted_intent,
                    'confidence': confidence_score,
                    'all_scores': all_scores,
                    'method': 'ml'
                }
                
        except Exception as e:
            logger.error(f"❌ خطأ في التنبؤ: {e}")
            return self._rule_based_classify(text)
    
    def _rule_based_classify(self, text: str) -> Dict:
        """تصنيف بالقواعد (fallback)"""
        text_lower = text.lower()
        
        # قواعد التصنيف
        rules = {
            'add_appointment': [
                'موعد', 'اجتماع', 'لقاء', 'مقابلة', 'أضف', 'سجل', 'حجز',
                'rdv', 'rendez-vous', 'réunion', 'ajouter',
                'appointment', 'meeting', 'schedule', 'book'
            ],
            'list_appointments': [
                'عرض مواعيدي', 'مواعيدي', 'أظهر المواعيد', 'كل مواعيدي',
                'mes rdv', 'mes rendez-vous', 'afficher',
                'my appointments', 'show appointments', 'list'
            ],
            'check_specific_day': [
                'مواعيدي اليوم', 'مواعيدي غدا', 'مواعيد يوم',
                'rdv aujourd', 'rdv demain',
                'today', 'tomorrow', 'appointments on'
            ],
            'cancel_appointment': [
                'إلغاء', 'احذف', 'حذف', 'ألغي',
                'annuler', 'supprimer',
                'cancel', 'delete', 'remove'
            ],
            'greeting': [
                'مرحبا', 'السلام', 'صباح', 'مساء', 'أهلا',
                'bonjour', 'salut', 'bonsoir',
                'hello', 'hi', 'hey', 'good morning'
            ],
            'thanks': [
                'شكرا', 'مشكور',
                'merci',
                'thanks', 'thank you'
            ],
            'help': [
                'مساعدة', 'ساعدني', 'كيف',
                'aide', 'comment',
                'help', 'how'
            ]
        }
        
        best_intent = 'unknown'
        best_score = 0
        
        for intent, keywords in rules.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            score = matches / len(keywords) if keywords else 0
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return {
            'intent': best_intent,
            'confidence': min(best_score * 2, 0.9),  # تحويل إلى نسبة ثقة
            'all_scores': {},
            'method': 'rule_based'
        }


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار نظام تصنيف النوايا الذكي")
    print("="*70)
    
    # إنشاء المصنف
    classifier = SmartIntentClassifier(model_type="lstm")
    
    # تدريب النموذج
    print("\n📚 تدريب النموذج...")
    result = classifier.train(epochs=10, batch_size=16)
    
    if result['success']:
        print(f"\n✅ التدريب ناجح! الدقة: {result['best_accuracy']:.1f}%")
        
        # اختبار التنبؤ
        test_messages = [
            "موعد غداً الساعة 3",
            "عرض مواعيدي",
            "مرحبا",
            "RDV demain à 15h",
            "My appointments today",
            "شكراً جزيلاً"
        ]
        
        print("\n" + "─"*70)
        print("🔍 اختبار التنبؤ:")
        print("─"*70)
        
        for msg in test_messages:
            result = classifier.predict(msg)
            print(f"\n💬 '{msg}'")
            print(f"   → النية: {result['intent']}")
            print(f"   → الثقة: {result['confidence']*100:.1f}%")
            print(f"   → الطريقة: {result['method']}")
    
    print("\n" + "="*70)
    print("✅ الاختبار انتهى!")
