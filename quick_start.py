#!/usr/bin/env python3
# quick_start.py
"""
🚀 التشغيل السريع لنظام Lamis Bot الذكي
═══════════════════════════════════════════

هذا الملف يساعدك على:
1. تدريب النموذج
2. اختبار التصنيف
3. تشغيل عرض توضيحي

الاستخدام:
    python quick_start.py train    # تدريب النموذج
    python quick_start.py test     # اختبار سريع
    python quick_start.py demo     # عرض توضيحي تفاعلي
    python quick_start.py report   # تقرير الأداء
"""

import sys
import asyncio
from pathlib import Path


def print_header(title: str):
    """طباعة عنوان"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def train_model():
    """تدريب النموذج"""
    print_header("🧠 تدريب نموذج تصنيف النوايا")
    
    from smart_ai_engine import create_engine
    
    engine = create_engine(use_bert=False, auto_retrain=False)
    
    print("📚 جاري التدريب...\n")
    result = engine.train_classifier(epochs=50)
    
    if result.get('success'):
        print(f"\n✅ تم التدريب بنجاح!")
        print(f"⭐ أفضل دقة: {result['best_accuracy']:.1f}%")
    else:
        print(f"\n❌ فشل التدريب: {result.get('reason', 'unknown')}")


def test_model():
    """اختبار سريع"""
    print_header("🔍 اختبار سريع لتصنيف النوايا")
    
    from integration import classify_intent, extract_datetime
    
    test_messages = [
        # العربية
        "موعد غداً الساعة 3",
        "عرض مواعيدي",
        "مرحبا",
        "إلغاء الموعد",
        "مساعدة",
        
        # الفرنسية
        "RDV demain à 15h",
        "Mes rendez-vous",
        "Bonjour",
        
        # الإنجليزية
        "Schedule meeting tomorrow",
        "Show my appointments",
        "Hello",
    ]
    
    print("📝 نتائج التصنيف:\n")
    print(f"{'الرسالة':<40} {'النية':<25} {'الثقة':<10}")
    print("-"*75)
    
    for msg in test_messages:
        intent, confidence = classify_intent(msg)
        conf_str = f"{confidence*100:.0f}%"
        
        # رمز الثقة
        if confidence >= 0.8:
            conf_icon = "🟢"
        elif confidence >= 0.6:
            conf_icon = "🟡"
        else:
            conf_icon = "🔴"
        
        print(f"{msg:<40} {intent:<25} {conf_icon} {conf_str:<10}")
    
    print("\n" + "-"*75)
    
    # اختبار استخراج التاريخ/الوقت
    print("\n📅 اختبار استخراج التاريخ/الوقت:\n")
    
    datetime_tests = [
        "موعد غداً الساعة 3 مساءً",
        "RDV demain à 15h30",
        "Meeting tomorrow at 2pm"
    ]
    
    for text in datetime_tests:
        info = extract_datetime(text)
        print(f"'{text}'")
        print(f"   📅 التاريخ: {info.get('date')}")
        print(f"   ⏰ الوقت: {info.get('time')}")
        print()


async def run_demo():
    """عرض توضيحي تفاعلي"""
    print_header("💬 العرض التوضيحي التفاعلي")
    
    from integration import SmartMessageHandler
    
    handler = SmartMessageHandler()
    user_id = 1
    
    print("مرحباً! أنا Lamis Bot 🤖")
    print("اكتب رسالتك وسأحللها لك.")
    print("اكتب 'خروج' أو 'exit' للإنهاء.\n")
    print("-"*50)
    
    while True:
        try:
            message = input("\n👤 أنت: ").strip()
            
            if not message:
                continue
            
            if message.lower() in ['خروج', 'exit', 'quit', 'q']:
                print("\n👋 مع السلامة!")
                break
            
            # معالجة الرسالة
            result = await handler.handle(user_id, message)
            
            print(f"\n🤖 Lamis Bot:")
            print(f"   🎯 النية: {result['intent']}")
            print(f"   📊 الثقة: {result['confidence']*100:.0f}%")
            print(f"   📍 الحالة: {result['state']}")
            print(f"   🔧 الإجراء: {result['action']}")
            
            if result.get('extracted_info'):
                print(f"   📋 المستخرج: {result['extracted_info']}")
            
            if result.get('response'):
                print(f"\n   💬 الرد:\n{result['response']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 مع السلامة!")
            break
        except Exception as e:
            print(f"\n❌ خطأ: {e}")


def show_report():
    """عرض تقرير الأداء"""
    print_header("📊 تقرير أداء النظام")
    
    from smart_ai_engine import create_engine
    
    engine = create_engine(use_bert=False, auto_retrain=False)
    
    # التقرير اليومي
    print(engine.get_daily_report())
    
    # التقرير الأسبوعي
    print("\n" + "-"*50)
    print(engine.get_weekly_report())
    
    # حالة النظام
    print("\n" + "-"*50)
    status = engine.get_status()
    print("\n⚙️ حالة النظام:")
    for key, value in status.items():
        print(f"   • {key}: {value}")


def show_help():
    """عرض المساعدة"""
    print_header("📖 دليل الاستخدام")
    
    print("""
الأوامر المتاحة:
─────────────────

  python quick_start.py train
      تدريب نموذج تصنيف النوايا (20 epoch)
      
  python quick_start.py test
      اختبار سريع للتصنيف مع أمثلة جاهزة
      
  python quick_start.py demo
      عرض توضيحي تفاعلي - اكتب رسائلك وشاهد التحليل
      
  python quick_start.py report
      عرض تقرير أداء النظام
      
  python quick_start.py help
      عرض هذه المساعدة

أمثلة الاستخدام:
─────────────────

  # تدريب ثم اختبار
  python quick_start.py train
  python quick_start.py test
  
  # تجربة تفاعلية
  python quick_start.py demo

للمزيد من المعلومات، راجع README.md
""")


def main():
    """الدالة الرئيسية"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'train':
        train_model()
    elif command == 'test':
        test_model()
    elif command == 'demo':
        asyncio.run(run_demo())
    elif command == 'report':
        show_report()
    elif command in ['help', '-h', '--help']:
        show_help()
    else:
        print(f"❌ أمر غير معروف: {command}")
        show_help()


if __name__ == "__main__":
    main()
