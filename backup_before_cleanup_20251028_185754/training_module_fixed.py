# training_module.py - Fixed Version ✅
"""
نظام التعلم الذاتي - نسخة محدثة
متوافق مع intelligent_agent.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import sqlite3
import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InteractionDataset(Dataset):
    """مجموعة بيانات التفاعلات للتدريب"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
        self.data = self._load_data()
        
        # قائمة النوايا المدعومة
        self.intent_labels = [
            'add_appointment',
            'list_appointments',
            'cancel_appointment',
            'modify_appointment',
            'greeting',
            'thanks',
            'help',
            'check_schedule',
            'check_specific_day',
            'general_query'
        ]
    
    def _load_data(self) -> List[Tuple]:
        """تحميل البيانات من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, intent, language, feedback
                FROM interactions
                WHERE intent IS NOT NULL AND intent != ''
                ORDER BY timestamp DESC
                LIMIT 10000
            ''')
            
            data = cursor.fetchall()
            conn.close()
            
            logger.info(f"✅ تم تحميل {len(data)} تفاعل من قاعدة البيانات")
            return data
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل البيانات: {e}")
            return []
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        message, intent, language, feedback = self.data[idx]
        
        # تحويل النص إلى vector بسيط (يمكن تحسينه لاحقاً)
        # هنا نستخدم طريقة بسيطة: طول النص وعدد الكلمات
        words = message.split()
        features = torch.tensor([
            len(message),           # طول النص
            len(words),            # عدد الكلمات
            len(set(words)),       # عدد الكلمات الفريدة
            1 if language == 'ar' else 0,  # عربي
            1 if language == 'fr' else 0,  # فرنسي
            1 if language == 'en' else 0,  # إنجليزي
            feedback if feedback else 0    # التقييم
        ], dtype=torch.float32)
        
        # تحويل النية إلى رقم
        if intent in self.intent_labels:
            intent_idx = self.intent_labels.index(intent)
        else:
            intent_idx = len(self.intent_labels) - 1  # general_query
        
        return features, torch.tensor(intent_idx, dtype=torch.long), feedback if feedback else 0


class SimpleIntentClassifier(nn.Module):
    """نموذج بسيط لتصنيف النوايا"""
    
    def __init__(self, input_size=7, hidden_size=64, num_classes=10):
        super(SimpleIntentClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x


class AdaptiveLearner:
    """نظام التعلم التكيفي"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
        self.model = SimpleIntentClassifier()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        self.training_history = []
    
    def train_epoch(self, dataloader: DataLoader) -> Tuple[float, float]:
        """تدريب epoch واحد"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for features, labels, feedbacks in dataloader:
            self.optimizer.zero_grad()
            
            # التنبؤ
            outputs = self.model(features)
            loss = self.criterion(outputs, labels)
            
            # تطبيق وزن إضافي للتفاعلات ذات feedback إيجابي
            feedbacks_tensor = torch.tensor([f if f else 0 for f in feedbacks], dtype=torch.float32)
            weighted_loss = loss * (1 + feedbacks_tensor.mean() * 0.1)
            
            # Backpropagation
            weighted_loss.backward()
            self.optimizer.step()
            
            total_loss += weighted_loss.item()
            
            # حساب الدقة
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total if total > 0 else 0
        avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0
        
        return avg_loss, accuracy
    
    def evaluate(self, dataloader: DataLoader) -> Tuple[float, float]:
        """تقييم النموذج"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for features, labels, _ in dataloader:
                outputs = self.model(features)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total if total > 0 else 0
        avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0
        
        return avg_loss, accuracy
    
    def train(self, epochs=10, batch_size=16, validation_split=0.2):
        """تدريب النموذج الكامل"""
        print("\n" + "="*60)
        print("🧠 بدء التدريب الذكي...")
        print("="*60)
        
        # تحميل البيانات
        dataset = InteractionDataset(self.db_path)
        
        if len(dataset) < 10:
            print("\n❌ لا توجد بيانات كافية للتدريب!")
            print(f"   الحد الأدنى: 10 تفاعلات")
            print(f"   الموجود: {len(dataset)} تفاعل")
            print("\n💡 الحل:")
            print("   1. استخدم البوت لفترة أطول")
            print("   2. تفاعل معه بعدة طرق مختلفة")
            print("   3. عد للتدريب لاحقاً")
            return False
        
        print(f"\n📊 تم تحميل {len(dataset)} تفاعل")
        
        # تقسيم البيانات
        train_size = int((1 - validation_split) * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        print(f"   📚 بيانات التدريب: {train_size}")
        print(f"   ✅ بيانات التحقق: {val_size}")
        
        best_val_accuracy = 0
        
        print("\n" + "─"*60)
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.evaluate(val_loader)
            
            print(f"\n📝 Epoch {epoch+1}/{epochs}")
            print(f"   🏋️ التدريب   → Loss: {train_loss:.4f}, Accuracy: {train_acc:.2f}%")
            print(f"   ✅ التحقق    → Loss: {val_loss:.4f}, Accuracy: {val_acc:.2f}%")
            
            # حفظ أفضل نموذج
            if val_acc > best_val_accuracy:
                best_val_accuracy = val_acc
                self.save_model("best_model.pth")
                print(f"   ⭐ أفضل نموذج! (Accuracy: {val_acc:.2f}%)")
            
            self.training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc
            })
        
        print("\n" + "="*60)
        print(f"🎉 انتهى التدريب!")
        print(f"⭐ أفضل دقة: {best_val_accuracy:.2f}%")
        print("="*60)
        
        return True
    
    def save_model(self, path: str):
        """حفظ النموذج"""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'training_history': self.training_history
            }, path)
            logger.info(f"✅ تم حفظ النموذج: {path}")
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ النموذج: {e}")
    
    def load_model(self, path: str):
        """تحميل النموذج"""
        try:
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.training_history = checkpoint.get('training_history', [])
            logger.info(f"✅ تم تحميل النموذج من {path}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل النموذج: {e}")
            return False
    
    def continuous_learning(self, min_new_interactions=50):
        """التعلم المستمر التلقائي"""
        print("\n🔄 فحص التفاعلات الجديدة...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # التحقق من عدد التفاعلات الجديدة
        cursor.execute('''
            SELECT COUNT(*) FROM interactions 
            WHERE timestamp > datetime('now', '-7 days')
            AND intent IS NOT NULL
        ''')
        
        new_interactions = cursor.fetchone()[0]
        conn.close()
        
        print(f"   📊 تفاعلات جديدة (آخر 7 أيام): {new_interactions}")
        
        if new_interactions >= min_new_interactions:
            print(f"   ✅ كافية للتدريب! (الحد الأدنى: {min_new_interactions})")
            print("\n🚀 بدء التعلم المستمر...")
            return self.train(epochs=5, batch_size=16)
        else:
            print(f"   ⏳ غير كافية (الحد الأدنى: {min_new_interactions})")
            print(f"   💡 استمر في استخدام البوت لجمع المزيد من البيانات")
            return False


class FeedbackCollector:
    """جمع ردود الفعل لتحسين التعلم"""
    
    def __init__(self, db_path="agent_data.db"):
        self.db_path = db_path
    
    def add_feedback(self, interaction_id: int, feedback_score: int):
        """إضافة تقييم للتفاعل (1-5)"""
        if not 1 <= feedback_score <= 5:
            logger.warning(f"⚠️ تقييم غير صالح: {feedback_score} (يجب أن يكون 1-5)")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE interactions 
                SET feedback = ? 
                WHERE id = ?
            ''', (feedback_score, interaction_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم إضافة تقييم: {feedback_score}/5 للتفاعل #{interaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة التقييم: {e}")
            return False
    
    def get_feedback_statistics(self) -> dict:
        """إحصائيات ردود الفعل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(feedback) as avg_feedback,
                    COUNT(CASE WHEN feedback >= 4 THEN 1 END) as positive,
                    COUNT(CASE WHEN feedback <= 2 THEN 1 END) as negative
                FROM interactions
                WHERE feedback > 0
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result[0] == 0:
                return {
                    'total_feedbacks': 0,
                    'average_score': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'satisfaction_rate': 0
                }
            
            return {
                'total_feedbacks': result[0],
                'average_score': round(result[1], 2) if result[1] else 0,
                'positive_count': result[2],
                'negative_count': result[3],
                'satisfaction_rate': round((result[2] / result[0] * 100), 2) if result[0] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في الإحصائيات: {e}")
            return {}
    
    def analyze_weaknesses(self) -> List[dict]:
        """تحليل نقاط الضعف في الأداء"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT intent, language, AVG(feedback) as avg_feedback, COUNT(*) as count
                FROM interactions
                WHERE feedback > 0 AND intent IS NOT NULL
                GROUP BY intent, language
                HAVING count >= 3
                ORDER BY avg_feedback ASC
                LIMIT 10
            ''')
            
            weaknesses = []
            for row in cursor.fetchall():
                weaknesses.append({
                    'intent': row[0],
                    'language': row[1],
                    'avg_feedback': round(row[2], 2),
                    'sample_count': row[3]
                })
            
            conn.close()
            return weaknesses
            
        except Exception as e:
            logger.error(f"❌ خطأ في التحليل: {e}")
            return []


# مثال على الاستخدام
if __name__ == "__main__":
    print("="*60)
    print("🧠 نظام التعلم الذاتي للمساعد الذكي")
    print("="*60)
    
    # إنشاء المتعلم التكيفي
    learner = AdaptiveLearner()
    
    # تدريب النموذج
    success = learner.train(epochs=10, batch_size=16)
    
    if success:
        # حفظ النموذج
        learner.save_model("trained_model.pth")
        
        # إحصائيات ردود الفعل
        collector = FeedbackCollector()
        stats = collector.get_feedback_statistics()
        
        if stats['total_feedbacks'] > 0:
            print("\n" + "="*60)
            print("📊 إحصائيات الأداء:")
            print("="*60)
            print(f"   إجمالي التقييمات: {stats['total_feedbacks']}")
            print(f"   متوسط التقييم: {stats['average_score']}/5")
            print(f"   نسبة الرضا: {stats['satisfaction_rate']}%")
            print(f"   تقييمات إيجابية: {stats['positive_count']}")
            print(f"   تقييمات سلبية: {stats['negative_count']}")
            
            # نقاط الضعف
            weaknesses = collector.analyze_weaknesses()
            if weaknesses:
                print("\n⚠️ المجالات التي تحتاج تحسين:")
                for w in weaknesses:
                    print(f"   • {w['intent']} ({w['language']}): {w['avg_feedback']}/5")
        
        print("\n✅ انتهى التدريب بنجاح!")
    else:
        print("\n⚠️ لم يتم التدريب - جمع المزيد من البيانات أولاً")