#!/usr/bin/env python3
# test_on_time_reminder.py
"""
اختبار ميزة التذكير عند وقت الموعد 🚨
"""

import sqlite3
from datetime import datetime, timedelta
from intelligent_agent import IntelligentAgent

def test_on_time_reminder():
    """اختبار إنشاء موعد مع تذكير عند الموعد"""
    print("="*70)
    print("🧪 اختبار: التذكير عند وقت الموعد")
    print("="*70)
    
    agent = IntelligentAgent()
    
    # سيناريوهات اختبار
    test_cases = [
        {
            'name': 'موعد بعد 5 دقائق (اختبار سريع)',
            'time_delta': timedelta(minutes=5),
            'expected_reminders': 1  # فقط تذكير عند الموعد
        },
        {
            'name': 'موعد بعد 20 دقيقة',
            'time_delta': timedelta(minutes=20),
            'expected_reminders': 2  # 15 دقيقة + عند الموعد
        },
        {
            'name': 'موعد بعد 2 ساعات',
            'time_delta': timedelta(hours=2),
            'expected_reminders': 3  # 1 ساعة + 15 دقيقة + عند الموعد
        },
        {
            'name': 'موعد بعد 30 ساعة',
            'time_delta': timedelta(hours=30),
            'expected_reminders': 4  # 24 ساعة + 1 ساعة + 15 دقيقة + عند الموعد ✨
        }
    ]
    
    for test in test_cases:
        print(f"\n{'─'*70}")
        print(f"📝 {test['name']}")
        print('─'*70)
        
        future_time = datetime.now() + test['time_delta']
        
        # إنشاء الموعد
        apt_id = agent.db.add_appointment(
            user_id=99999,
            title=test['name'],
            description="اختبار التذكير عند الموعد",
            date_time=future_time,
            priority=1
        )
        
        print(f"\n✅ تم إنشاء موعد #{apt_id}")
        print(f"   📅 التاريخ: {future_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # فحص التذكيرات المُنشأة
        conn = sqlite3.connect(agent.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, reminder_time, custom_message
            FROM reminders
            WHERE appointment_id = ?
            ORDER BY reminder_time
        ''', (apt_id,))
        
        reminders = cursor.fetchall()
        conn.close()
        
        print(f"\n   🔔 عدد التذكيرات: {len(reminders)}")
        
        if len(reminders) == test['expected_reminders']:
            print(f"   ✅ صحيح! (متوقع: {test['expected_reminders']})")
        else:
            print(f"   ⚠️ غير متوقع! (متوقع: {test['expected_reminders']}, حصلنا: {len(reminders)})")
        
        print(f"\n   📋 تفاصيل التذكيرات:")
        now = datetime.now()
        
        for reminder in reminders:
            rid, rtime, custom_msg = reminder
            
            # تنظيف التاريخ
            if '.' in rtime:
                rtime = rtime.split('.')[0]
            
            rtime_dt = datetime.strptime(rtime, '%Y-%m-%d %H:%M:%S')
            diff_minutes = int((rtime_dt - now).total_seconds() / 60)
            
            # تحديد النوع
            reminder_type = "advance"
            if custom_msg and "type:" in custom_msg:
                reminder_type = custom_msg.split("type:")[1].strip()
            
            # إيموجي حسب النوع
            if reminder_type == "now":
                emoji = "🚨"
                type_label = "عند الموعد"
            else:
                emoji = "🔔"
                type_label = "قبل الموعد"
            
            if diff_minutes < 0:
                time_str = f"متأخر {abs(diff_minutes)} دقيقة"
            else:
                time_str = f"بعد {diff_minutes} دقيقة"
            
            print(f"      {emoji} تذكير #{rid}: {type_label} ({time_str})")
    
    print("\n" + "="*70)


def show_reminder_types():
    """عرض أنواع التذكيرات"""
    print("\n" + "="*70)
    print("📋 أنواع التذكيرات الآن (4 أنواع)")
    print("="*70)
    
    print("""
┌────────────────────────────────────────────────────────────────┐
│  الوقت قبل الموعد  │  النوع    │  الرسالة                      │
├────────────────────────────────────────────────────────────────┤
│  📅 24 ساعة        │  advance  │  ⏰ تذكير بموعد (عادي)        │
│  ⏰ 1 ساعة         │  advance  │  ⏰ تذكير بموعد (عادي)        │
│  ⏱️  15 دقيقة       │  advance  │  ⏰ تذكير بموعد (عادي)        │
│  🚨 0 دقيقة (الآن!) │  now      │  🚨 حان وقت الموعد! (عاجل)   │
└────────────────────────────────────────────────────────────────┘

✨ الجديد:
   التذكير الرابع يصل **عند وقت الموعد بالضبط**
   مع رسالة مختلفة وأكثر إلحاحاً! 🚨
    """)
    
    print("="*70)


def compare_messages():
    """مقارنة بين الرسائل"""
    print("\n" + "="*70)
    print("📱 مقارنة بين الرسائل")
    print("="*70)
    
    print("\n🔔 **رسالة التذكير العادي (قبل الموعد):**")
    print("─"*70)
    print("""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 موعد مع الطبيب
📅 2025-10-14 10:00:00

⏰ الوقت المتبقي | Temps restant:
🇸🇦 ساعة واحدة
🇫🇷 1 heure
🇬🇧 1 hour

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!""")
    
    print("\n\n🚨 **رسالة التذكير عند الموعد (الآن!):**")
    print("─"*70)
    print("""🚨 **حان وقت الموعد! | C'est l'heure! | It's time!** 🚨

📋 **موعد مع الطبيب**
📅 2025-10-14 10:00:00

⏰ **موعدك الآن!**
⏰ **Votre RDV maintenant!**
⏰ **Your appointment is NOW!**

🏃‍♂️ لا تتأخر! | Ne soyez pas en retard! | Don't be late!""")
    
    print("\n" + "="*70)


def practical_test():
    """اختبار عملي: موعد بعد 3 دقائق"""
    print("\n" + "="*70)
    print("💡 اختبار عملي: موعد بعد 3 دقائق")
    print("="*70)
    
    response = input("\nهل تريد إنشاء موعد اختباري بعد 3 دقائق؟ (y/n): ").lower()
    
    if response != 'y':
        print("❌ تم الإلغاء")
        return
    
    agent = IntelligentAgent()
    
    # موعد بعد 3 دقائق (ستحصل على تذكير عند الموعد فقط)
    future_time = datetime.now() + timedelta(minutes=3)
    
    print(f"\n⏰ الآن: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📅 الموعد: {future_time.strftime('%H:%M:%S')}")
    
    # استخدم user_id الحقيقي من Telegram
    user_id_input = input("\nأدخل user_id من Telegram (أو Enter لاستخدام 99999): ").strip()
    user_id = int(user_id_input) if user_id_input else 99999
    
    apt_id = agent.db.add_appointment(
        user_id=user_id,
        title="🧪 اختبار التذكير عند الموعد",
        description="موعد تجريبي - ستحصل على تذكير عند الموعد!",
        date_time=future_time,
        priority=1
    )
    
    print(f"\n✅ تم إنشاء موعد #{apt_id}")
    print(f"\n💡 الخطوة التالية:")
    print(f"   1. تأكد من أن البوت يعمل: python telegram_bot.py")
    print(f"   2. انتظر **3 دقائق بالضبط**")
    print(f"   3. في الدقيقة الثالثة، ستصلك رسالة: 🚨 حان وقت الموعد!")
    print(f"\n⏱️  العد التنازلي: 3 دقائق... ⏱️")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n🚀 اختبار شامل: التذكير عند وقت الموعد\n")
    
    # 1. عرض أنواع التذكيرات
    show_reminder_types()
    
    # 2. مقارنة الرسائل
    compare_messages()
    
    # 3. الاختبار الفعلي
    test_on_time_reminder()
    
    # 4. اختبار عملي
    practical_test()
    
    print("\n✅ انتهى الاختبار!")
    print("""
💡 ملاحظة نهائية:
   الآن لديك 4 تذكيرات لكل موعد:
   
   📅 قبل 24 ساعة → "لا تنسى موعدك!"
   ⏰ قبل 1 ساعة → "لا تنسى موعدك!"
   ⏱️  قبل 15 دقيقة → "لا تنسى موعدك!"
   🚨 عند الموعد → "حان وقت الموعد! لا تتأخر!"
    """)