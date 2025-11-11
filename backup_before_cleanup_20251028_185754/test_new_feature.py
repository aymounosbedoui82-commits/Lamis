#!/usr/bin/env python3
from intelligent_agent import IntelligentAgent
from datetime import datetime, timedelta

def quick_test():
    """اختبار سريع للميزة الجديدة"""
    print("="*60)
    print("🧪 اختبار سريع: مواعيد يوم محدد")
    print("="*60)
    
    agent = IntelligentAgent()
    
    # إنشاء موعد اليوم
    today = datetime.now().replace(hour=14, minute=0)
    agent.db.add_appointment(
        user_id=1,
        title="اجتماع مهم",
        description="اجتماع فريق العمل",
        date_time=today,
        priority=1
    )
    
    # اختبار الاستفسارات
    test_queries = [
        ("ما هي مواعيدي اليوم؟", "ar"),
        ("Mes rendez-vous aujourd'hui", "fr"),
        ("My appointments today", "en"),
    ]
    
    for query, lang in test_queries:
        print(f"\n💬 {query}")
        print("─"*60)
        response = agent.process_message(1, query)
        print(response)
        print()
    
    print("="*60)
    print("✅ الاختبار نجح!")

if __name__ == "__main__":
    quick_test()