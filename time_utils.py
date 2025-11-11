# time_utils.py
"""
دوال مساعدة لحساب وتنسيق الوقت المتبقي
"""

from datetime import datetime
from typing import Dict

def calculate_time_remaining(target_datetime: datetime) -> Dict[str, int]:
    """
    حساب الوقت المتبقي حتى تاريخ معين
    
    Returns:
        dict: {'months': x, 'days': x, 'hours': x, 'minutes': x, 'seconds': x}
    """
    now = datetime.now()
    
    if target_datetime <= now:
        return {'months': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    
    # حساب الفرق
    diff = target_datetime - now
    
    # تحويل إلى ثواني
    total_seconds = int(diff.total_seconds())
    
    # حساب الأشهر (تقريبي - 30 يوم)
    months = total_seconds // (30 * 24 * 3600)
    remaining = total_seconds % (30 * 24 * 3600)
    
    # حساب الأيام
    days = remaining // (24 * 3600)
    remaining = remaining % (24 * 3600)
    
    # حساب الساعات
    hours = remaining // 3600
    remaining = remaining % 3600
    
    # حساب الدقائق
    minutes = remaining // 60
    seconds = remaining % 60
    
    return {
        'months': months,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }


def format_time_remaining_arabic(time_dict: Dict[str, int]) -> str:
    """تنسيق الوقت المتبقي بالعربية"""
    parts = []
    
    if time_dict['months'] > 0:
        if time_dict['months'] == 1:
            parts.append("شهر واحد")
        elif time_dict['months'] == 2:
            parts.append("شهرين")
        elif time_dict['months'] <= 10:
            parts.append(f"{time_dict['months']} أشهر")
        else:
            parts.append(f"{time_dict['months']} شهراً")
    
    if time_dict['days'] > 0:
        if time_dict['days'] == 1:
            parts.append("يوم واحد")
        elif time_dict['days'] == 2:
            parts.append("يومين")
        elif time_dict['days'] <= 10:
            parts.append(f"{time_dict['days']} أيام")
        else:
            parts.append(f"{time_dict['days']} يوماً")
    
    if time_dict['hours'] > 0:
        if time_dict['hours'] == 1:
            parts.append("ساعة واحدة")
        elif time_dict['hours'] == 2:
            parts.append("ساعتين")
        elif time_dict['hours'] <= 10:
            parts.append(f"{time_dict['hours']} ساعات")
        else:
            parts.append(f"{time_dict['hours']} ساعة")
    
    if time_dict['minutes'] > 0:
        if time_dict['minutes'] == 1:
            parts.append("دقيقة واحدة")
        elif time_dict['minutes'] == 2:
            parts.append("دقيقتين")
        elif time_dict['minutes'] <= 10:
            parts.append(f"{time_dict['minutes']} دقائق")
        else:
            parts.append(f"{time_dict['minutes']} دقيقة")
    
    if not parts:
        return "أقل من دقيقة"
    
    return " و ".join(parts)


def format_time_remaining_french(time_dict: Dict[str, int]) -> str:
    """تنسيق الوقت المتبقي بالفرنسية"""
    parts = []
    
    if time_dict['months'] > 0:
        if time_dict['months'] == 1:
            parts.append("1 mois")
        else:
            parts.append(f"{time_dict['months']} mois")
    
    if time_dict['days'] > 0:
        if time_dict['days'] == 1:
            parts.append("1 jour")
        else:
            parts.append(f"{time_dict['days']} jours")
    
    if time_dict['hours'] > 0:
        if time_dict['hours'] == 1:
            parts.append("1 heure")
        else:
            parts.append(f"{time_dict['hours']} heures")
    
    if time_dict['minutes'] > 0:
        if time_dict['minutes'] == 1:
            parts.append("1 minute")
        else:
            parts.append(f"{time_dict['minutes']} minutes")
    
    if not parts:
        return "moins d'une minute"
    
    return " et ".join(parts)


def format_time_remaining_english(time_dict: Dict[str, int]) -> str:
    """تنسيق الوقت المتبقي بالإنجليزية"""
    parts = []
    
    if time_dict['months'] > 0:
        if time_dict['months'] == 1:
            parts.append("1 month")
        else:
            parts.append(f"{time_dict['months']} months")
    
    if time_dict['days'] > 0:
        if time_dict['days'] == 1:
            parts.append("1 day")
        else:
            parts.append(f"{time_dict['days']} days")
    
    if time_dict['hours'] > 0:
        if time_dict['hours'] == 1:
            parts.append("1 hour")
        else:
            parts.append(f"{time_dict['hours']} hours")
    
    if time_dict['minutes'] > 0:
        if time_dict['minutes'] == 1:
            parts.append("1 minute")
        else:
            parts.append(f"{time_dict['minutes']} minutes")
    
    if not parts:
        return "less than a minute"
    
    return " and ".join(parts)


def get_time_remaining_message(target_datetime: datetime) -> str:
    """
    الحصول على رسالة الوقت المتبقي بـ 3 لغات مع إيموجي
    
    Args:
        target_datetime: تاريخ الموعد
        
    Returns:
        str: رسالة منسقة بـ 3 لغات
    """
    time_dict = calculate_time_remaining(target_datetime)
    
    ar = format_time_remaining_arabic(time_dict)
    fr = format_time_remaining_french(time_dict)
    en = format_time_remaining_english(time_dict)
    
    # اختيار إيموجي حسب الوقت المتبقي
    total_minutes = (time_dict['months'] * 30 * 24 * 60 + 
                     time_dict['days'] * 24 * 60 + 
                     time_dict['hours'] * 60 + 
                     time_dict['minutes'])
    
    if total_minutes <= 5:
        emoji = "🚨"  # عاجل جداً
        urgency = "⚠️ **عاجل! | Urgent! | Urgent!**"
    elif total_minutes <= 15:
        emoji = "⚡"  # قريب جداً
        urgency = "⚠️ **قريب! | Proche! | Soon!**"
    elif total_minutes <= 60:
        emoji = "⏰"  # خلال ساعة
        urgency = ""
    elif time_dict['days'] == 0:
        emoji = "🕐"  # اليوم
        urgency = ""
    elif time_dict['days'] <= 7:
        emoji = "📅"  # هذا الأسبوع
        urgency = ""
    else:
        emoji = "🗓️"  # بعد أسبوع
        urgency = ""
    
    message = f"""{urgency}
{emoji} **الوقت المتبقي | Temps restant | Time remaining:**
🇸🇦 {ar}
🇫🇷 {fr}
🇬🇧 {en}"""
    
    return message


# اختبار
if __name__ == "__main__":
    from datetime import timedelta
    
    print("🧪 اختبار حساب الوقت المتبقي\n")
    print("="*60)
    
    # اختبار 1: بعد 25 دقيقة
    test1 = datetime.now() + timedelta(minutes=25)
    print("\n📝 الاختبار 1: موعد بعد 25 دقيقة")
    print(get_time_remaining_message(test1))
    
    # اختبار 2: بعد 2 ساعة و 30 دقيقة
    test2 = datetime.now() + timedelta(hours=2, minutes=30)
    print("\n📝 الاختبار 2: موعد بعد 2 ساعة و 30 دقيقة")
    print(get_time_remaining_message(test2))
    
    # اختبار 3: بعد 3 أيام و 5 ساعات
    test3 = datetime.now() + timedelta(days=3, hours=5, minutes=15)
    print("\n📝 الاختبار 3: موعد بعد 3 أيام و 5 ساعات و 15 دقيقة")
    print(get_time_remaining_message(test3))
    
    # اختبار 4: بعد شهر و 5 أيام
    test4 = datetime.now() + timedelta(days=35, hours=2)
    print("\n📝 الاختبار 4: موعد بعد 35 يوماً")
    print(get_time_remaining_message(test4))
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار!")