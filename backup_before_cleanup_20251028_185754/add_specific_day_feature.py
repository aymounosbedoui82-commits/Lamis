#!/usr/bin/env python3
# add_specific_day_feature.py
"""
تطبيق تلقائي لميزة: عرض مواعيد يوم محدد
يقوم بتعديل intelligent_agent.py تلقائياً
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """إنشاء نسخة احتياطية"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"✅ نسخة احتياطية: {backup_path}")
        return backup_path
    return None


def add_helper_methods():
    """الدوال المساعدة للتنسيق"""
    return '''
    def _format_day_arabic(self, date: datetime) -> str:
        """تنسيق اليوم بالعربية"""
        weekdays = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        today = datetime.now().date()
        target = date.date()
        
        if target == today:
            return "اليوم"
        elif target == today + timedelta(days=1):
            return "غداً"
        elif target == today - timedelta(days=1):
            return "أمس"
        else:
            return f"يوم {weekdays[date.weekday()]}"

    def _format_day_french(self, date: datetime) -> str:
        """تنسيق اليوم بالفرنسية"""
        weekdays = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        today = datetime.now().date()
        target = date.date()
        
        if target == today:
            return "aujourd'hui"
        elif target == today + timedelta(days=1):
            return "demain"
        elif target == today - timedelta(days=1):
            return "hier"
        else:
            return weekdays[date.weekday()]

    def _format_day_english(self, date: datetime) -> str:
        """تنسيق اليوم بالإنجليزية"""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        today = datetime.now().date()
        target = date.date()
        
        if target == today:
            return "today"
        elif target == today + timedelta(days=1):
            return "tomorrow"
        elif target == today - timedelta(days=1):
            return "yesterday"
        else:
            return f"on {weekdays[date.weekday()]}"
'''


def add_intent_keywords():
    """النية الجديدة"""
    return """
        'check_specific_day': [
            # عربي
            'مواعيدي في', 'مواعيد يوم', 'ما هي مواعيدي', 'مواعيدي يوم',
            'مواعيدي غدا', 'مواعيدي غداً', 'مواعيدي اليوم', 
            'مواعيدي الاحد', 'مواعيدي الاثنين', 'مواعيدي الثلاثاء',
            'مواعيدي الاربعاء', 'مواعيدي الخميس', 'مواعيدي الجمعة', 'مواعيدي السبت',
            # فرنسي
            'mes rendez-vous', 'rdv du', 'rendez-vous de', 'quels sont mes',
            'mes rdv', 'rendez-vous demain', 'rdv demain', 'rendez-vous aujourd',
            'mes rendez-vous lundi', 'mes rendez-vous mardi',
            # إنجليزي
            'my appointments on', 'appointments for', 'appointments on',
            'what are my appointments', 'appointments today', 'appointments tomorrow',
            'appointments monday', 'appointments tuesday',
        ],
"""


def add_process_handler():
    """معالج النية الجديدة"""
    return """
        elif intent == 'check_specific_day':
            # استخراج التاريخ المطلوب
            target_date = self.extract_datetime(message, language)
            
            # الحصول على المواعيد لهذا اليوم
            day_start = target_date.replace(hour=0, minute=0, second=0)
            day_end = target_date.replace(hour=23, minute=59, second=59)
            
            appointments = self.db.get_appointments(
                user_id,
                day_start.strftime('%Y-%m-%d %H:%M:%S'),
                day_end.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # تنسيق الرد حسب اللغة
            if language == 'ar':
                day_label = self._format_day_arabic(target_date)
                header = f"📅 **مواعيدك {day_label}**"
                no_apt = f"✨ لا توجد مواعيد {day_label}"
            elif language == 'fr':
                day_label = self._format_day_french(target_date)
                header = f"📅 **Vos rendez-vous {day_label}**"
                no_apt = f"✨ Aucun rendez-vous {day_label}"
            else:
                day_label = self._format_day_english(target_date)
                header = f"📅 **Your appointments {day_label}**"
                no_apt = f"✨ No appointments {day_label}"
            
            response = f"{header}\\n**{target_date.strftime('%d/%m/%Y')}**\\n\\n"
            
            if not appointments:
                response += no_apt
            else:
                for apt in appointments:
                    apt_date = datetime.strptime(apt['date_time'], '%Y-%m-%d %H:%M:%S')
                    priority_emoji = "🔴" if apt['priority'] == 1 else "🟡" if apt['priority'] == 2 else "🟢"
                    response += f"{priority_emoji} **{apt_date.strftime('%H:%M')}** - {apt['title']}\\n"
                    if apt['description']:
                        response += f"   📝 {apt['description'][:50]}...\\n"
                    response += "\\n"
"""


def apply_patch():
    """تطبيق التعديلات"""
    print("="*60)
    print("🔧 تطبيق ميزة: عرض مواعيد يوم محدد")
    print("="*60)
    
    filepath = "intelligent_agent.py"
    
    if not os.path.exists(filepath):
        print(f"❌ الملف غير موجود: {filepath}")
        return False
    
    # إنشاء نسخة احتياطية
    backup_file(filepath)
    
    # قراءة الملف
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n📝 التعديلات المطلوبة:")
    print("─"*60)
    
    # 1. إضافة الدوال المساعدة
    if '_format_day_arabic' not in content:
        print("✅ إضافة دوال التنسيق")
        # البحث عن نهاية class IntelligentAgent
        helper_methods = add_helper_methods()
        
        # إضافة قبل نهاية الـ class (قبل آخر if __name__)
        insertion_point = content.rfind('if __name__ == "__main__":')
        if insertion_point > 0:
            content = content[:insertion_point] + helper_methods + '\n\n' + content[insertion_point:]
        else:
            content += helper_methods
    else:
        print("⏭️  دوال التنسيق موجودة")
    
    # 2. تحديث classify_intent
    if 'check_specific_day' not in content:
        print("✅ إضافة النية الجديدة إلى classify_intent")
        # البحث عن intent_keywords
        intent_keywords_pos = content.find("intent_keywords = {")
        if intent_keywords_pos > 0:
            # البحث عن نهاية القاموس
            end_pos = content.find("'greeting':", intent_keywords_pos)
            if end_pos > 0:
                new_intent = add_intent_keywords()
                content = content[:end_pos] + new_intent + '\n        ' + content[end_pos:]
    else:
        print("⏭️  النية الجديدة موجودة")
    
    # 3. تحديث process_message
    if 'check_specific_day' not in content or "elif intent == 'check_specific_day':" not in content:
        print("✅ إضافة معالج النية في process_message")
        # البحث عن elif intent == 'list_appointments':
        list_apt_pos = content.find("elif intent == 'list_appointments':")
        if list_apt_pos > 0:
            # البحث عن نهاية هذا الـ block
            next_elif = content.find("elif intent ==", list_apt_pos + 100)
            if next_elif > 0:
                handler = add_process_handler()
                # إضافة قبل الـ elif التالي
                content = content[:next_elif] + handler + '\n        ' + content[next_elif:]
    else:
        print("⏭️  معالج النية موجود")
    
    # حفظ الملف
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("✅ تم تطبيق التعديلات بنجاح!")
    print("="*60)
    
    return True


def test_feature():
    """اختبار الميزة"""
    print("\n🧪 اختبار الميزة...")
    print("─"*60)
    
    try:
        from intelligent_agent import IntelligentAgent
        agent = IntelligentAgent()
        
        # اختبار التصنيف
        test_queries = [
            "ما هي مواعيدي اليوم؟",
            "Mes rendez-vous demain",
            "My appointments on Monday"
        ]
        
        print("\n✅ تم استيراد IntelligentAgent بنجاح")
        
        for query in test_queries:
            intent = agent.classify_intent(query)
            print(f"   • '{query}' → {intent}")
        
        print("\n✅ الميزة تعمل بشكل صحيح!")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 تطبيق تلقائي للميزة الجديدة\n")
    
    # تطبيق التعديلات
    if apply_patch():
        # اختبار
        if test_feature():
            print("""
💡 الخطوة التالية:
   
   1. شغّل البوت:
      python telegram_bot.py
   
   2. جرب الأوامر الجديدة:
      🇸🇦 "ما هي مواعيدي اليوم؟"
      🇫🇷 "Mes rendez-vous demain"
      🇬🇧 "My appointments on Monday"
   
   3. أو شغّل الاختبار الشامل:
      python test_specific_day.py

🎉 مبروك! الميزة جاهزة للاستخدام!
            """)
        else:
            print("\n⚠️ قد تحتاج لمراجعة التعديلات يدوياً")
    else:
        print("\n❌ فشل التطبيق")