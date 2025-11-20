# smart_search.py
"""
نظام بحث ذكي متقدم - البحث بالتاريخ، العنوان، الوصف، النطاق الزمني
✅ دعم البحث الغامض (fuzzy search)
✅ البحث بالنطاق الزمني
✅ تصنيف النتائج حسب الأهمية
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import re


class SmartSearch:
    """محرك بحث ذكي للمواعيد"""
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
    
    def _similarity(self, a: str, b: str) -> float:
        """حساب نسبة التشابه بين نصين"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def search_appointments(
        self,
        user_id: int,
        query: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        priority: int = None,
        min_similarity: float = 0.6
    ) -> List[Dict]:
        """
        بحث متقدم في المواعيد
        
        Args:
            user_id: معرف المستخدم
            query: نص البحث (في العنوان أو الوصف)
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            priority: الأولوية
            min_similarity: الحد الأدنى للتشابه (0-1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # بناء الاستعلام الأساسي
        sql = "SELECT id, title, description, date_time, priority FROM appointments WHERE user_id = ?"
        params = [user_id]
        
        # إضافة فلاتر
        if start_date:
            sql += " AND date_time >= ?"
            params.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))
        
        if end_date:
            sql += " AND date_time <= ?"
            params.append(end_date.strftime('%Y-%m-%d %H:%M:%S'))
        
        if priority:
            sql += " AND priority = ?"
            params.append(priority)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        # تحويل إلى قاموس
        appointments = []
        for row in results:
            apt = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'date_time': row[3],
                'priority': row[4],
                'relevance': 1.0  # افتراضي
            }
            
            # حساب نسبة الصلة بالبحث
            if query:
                title_sim = self._similarity(query, apt['title'])
                desc_sim = self._similarity(query, apt['description'] or "")
                apt['relevance'] = max(title_sim, desc_sim)
                
                # تصفية النتائج ضعيفة الصلة
                if apt['relevance'] < min_similarity:
                    continue
            
            appointments.append(apt)
        
        # ترتيب حسب الصلة ثم التاريخ
        appointments.sort(key=lambda x: (-x['relevance'], x['date_time']))
        
        return appointments
    
    def search_by_keywords(self, user_id: int, keywords: List[str]) -> List[Dict]:
        """بحث بكلمات مفتاحية متعددة"""
        all_results = []
        
        for keyword in keywords:
            results = self.search_appointments(user_id, query=keyword)
            all_results.extend(results)
        
        # إزالة المكررات
        unique_results = {apt['id']: apt for apt in all_results}
        return list(unique_results.values())
    
    def find_conflicts(self, user_id: int, target_date: datetime, duration_minutes: int = 60) -> List[Dict]:
        """البحث عن تعارضات في المواعيد"""
        start_time = target_date
        end_time = target_date + timedelta(minutes=duration_minutes)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, date_time, priority
            FROM appointments
            WHERE user_id = ?
            AND date_time BETWEEN ? AND ?
        ''', (
            user_id,
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conflicts = []
        for row in cursor.fetchall():
            conflicts.append({
                'id': row[0],
                'title': row[1],
                'date_time': row[2],
                'priority': row[3]
            })
        
        conn.close()
        return conflicts
    
    def get_suggestions(self, user_id: int, query: str, limit: int = 5) -> List[str]:
        """اقتراحات بحث ذكية بناءً على التاريخ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT title FROM appointments
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 100
        ''', (user_id,))
        
        titles = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # العثور على أقرب التطابقات
        suggestions = []
        for title in titles:
            similarity = self._similarity(query, title)
            if similarity > 0.3:
                suggestions.append((title, similarity))
        
        # ترتيب وإرجاع الأفضل
        suggestions.sort(key=lambda x: -x[1])
        return [title for title, _ in suggestions[:limit]]


# إضافة commands في telegram_bot.py
async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """البحث في المواعيد"""
    from smart_search import SmartSearch
    
    user_id = update.effective_user.id
    query = ' '.join(context.args) if context.args else None
    
    if not query:
        await update.message.reply_text(
            "🔍 استخدام البحث:\n"
            "/search [كلمة البحث]\n\n"
            "مثال:\n"
            "/search طبيب\n"
            "/search اجتماع"
        )
        return
    
    searcher = SmartSearch()
    results = searcher.search_appointments(user_id, query=query)
    
    if not results:
        await update.message.reply_text(
            f"❌ لم يتم العثور على مواعيد تطابق: {query}"
        )
        return
    
    message = f"🔍 **نتائج البحث عن:** {query}\n\n"
    
    for apt in results[:10]:  # أول 10 نتائج
        relevance_emoji = "🎯" if apt['relevance'] > 0.8 else "📌"
        date_obj = datetime.strptime(apt['date_time'], '%Y-%m-%d %H:%M:%S')
        
        message += f"{relevance_emoji} **{apt['title']}**\n"
        message += f"📅 {date_obj.strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🎯 صلة: {apt['relevance']*100:.0f}%\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')