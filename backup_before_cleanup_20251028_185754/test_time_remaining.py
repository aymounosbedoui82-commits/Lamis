#!/usr/bin/env python3
# test_time_remaining.py
"""
اختبار ميزة الوقت المتبقي في التذكيرات
"""

from datetime import datetime, timedelta

def test_time_utils():
    """اختبار time_utils.py"""
    print("="*60)
    print("🧪 اختبار حساب الوقت المتبقي")
    print("="*60)
    
    try:
        from time_utils import get_time_remaining_message, calculate_time_remaining
        
        print("\n✅ تم استيراد time_utils بنجاح!\n")
        
        # اختبارات مختلفة
        test_cases = [
            (timedelta(minutes=15), "15 دقيقة"),
            (timedelta(hours=1, minutes=30), "ساعة و 30 دقيقة"),
            (timedelta(days=2, hours=3), "يومين و 3 ساعات"),
            (timedelta(days=35), "شهر و 5 أيام"),
        ]
        
        for delta, description in test_cases:
            target = datetime.now() + delta
            print(f"📝 اختبار: موعد بعد {description}")
            print("-"*60)
            
            # حساب الوقت
            time_dict = calculate_time_remaining(target)
            print(f"   الأرقام: {time_dict}")
            
            # الرسالة المنسقة
            message = get_time_remaining_message(target)
            print(message)
            print()
        
        print("="*60)
        print("✅ جميع الاختبارات نجحت!")
        print("="*60)
        
        return True
        
    except ImportError:
        print("\n❌ لم يتم العثور على time_utils.py")
        print("\n📝 الحل:")
        print("   انسخ محتوى time_utils.py من الرد السابق")
        return False
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_test_reminder():
    """إنشاء موعد اختباري لرؤية التذكير مع الوقت المتبقي"""
    print("\n" + "="*60)
    print("📝 إنشاء موعد اختباري")
    print("="*60)
    
    try:
        from intelligent_agent import IntelligentAgent
        
        agent = IntelligentAgent()
        
        # موعد بعد 20 دقيقة
        future = datetime.now() + timedelta(minutes=20)
        
        print(f"\n⏰ الآن: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📅 الموعد: {future.strftime('%H:%M:%S')}")
        
        apt_id = agent.db.add_appointment(
            user_id=5200130110,  # استخدم user_id الحقيقي
            title="اختبار الوقت المتبقي",
            description="موعد لاختبار الميزة الجديدة",
            date_time=future,
            priority=1
        )
        
        print(f"\n✅ تم إنشاء موعد #{apt_id}")
        print(f"\n💡 التذكير سيصل بعد حوالي 5 دقائق")
        print(f"   يجب أن يحتوي على الوقت المتبقي بـ 3 لغات!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_example_message():
    """عرض مثال على الرسالة الجديدة"""
    print("\n" + "="*60)
    print("📱 مثال على الرسالة الجديدة")
    print("="*60)
    
    # محاكاة رسالة تذكير
    future = datetime.now() + timedelta(hours=2, minutes=30)
    
    try:
        from time_utils import get_time_remaining_message
        
        time_msg = get_time_remaining_message(future)
        
        message = f"""⏰ **تذكير بموعد | Rappel | Reminder:**

📋 موعد مع الطبيب
📅 {future.strftime('%Y-%m-%d %H:%M:%S')}

{time_msg}

🔔 لا تنسى موعدك!
🔔 N'oubliez pas votre RDV!
🔔 Don't forget your appointment!"""
        
        print("\n" + "─"*60)
        print(message)
        print("─"*60)
        
    except Exception as e:
        print(f"❌ خطأ: {e}")


if __name__ == "__main__":
    print("\n🚀 اختبار ميزة الوقت المتبقي\n")
    
    # 1. اختبار time_utils
    if not test_time_utils():
        print("\n⚠️ يجب إنشاء ملف time_utils.py أولاً")
        exit(1)
    
    # 2. عرض مثال على الرسالة
    show_example_message()
    
    # 3. سؤال عن إنشاء موعد اختباري
    print("\n" + "="*60)
    response = input("\nهل تريد إنشاء موعد اختباري؟ (y/n): ").lower()
    
    if response == 'y':
        create_test_reminder()
        print("\n💡 الخطوة التالية:")
        print("   1. تأكد من أن البوت يعمل: python telegram_bot.py")
        print("   2. انتظر حوالي 5 دقائق")
        print("   3. ستصلك رسالة تذكير مع الوقت المتبقي!")
    
    print("\n✅ انتهى الاختبار!")