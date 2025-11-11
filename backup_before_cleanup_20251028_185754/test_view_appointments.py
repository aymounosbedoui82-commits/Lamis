#!/usr/bin/env python3
# test_view_appointments.py
"""
اختبار عرض المواعيد
"""

from intelligent_agent import IntelligentAgent

def test_queries():
    print("="*60)
    print("🧪 اختبار عرض المواعيد")
    print("="*60)
    
    agent = IntelligentAgent()
    
    test_cases = [
        "مواعيدي اليوم",
        "مواعيدي غداً",
        "مواعيدي يوم 25 مارس 2027",
        "ما هي مواعيدي يوم 20 فيفري 2026",
        "Mes rendez-vous aujourd'hui",
        "My appointments today",
    ]
    
    for query in test_cases:
        print(f"\n{'='*60}")
        print(f"💬 الاستفسار: {query}")
        print('─'*60)
        
        # تصنيف النية
        intent = agent.classify_intent(query)
        print(f"🎯 النية: {intent}")
        
        # المعالجة الكاملة
        response = agent.process_message(user_id=5200130110, message=query)
        print(f"\n🤖 الرد:")
        print(response)
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_queries()