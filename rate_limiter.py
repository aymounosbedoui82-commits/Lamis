# rate_limiter.py
"""
نظام Rate Limiting للتحكم في عدد الطلبات
✅ يمنع إساءة الاستخدام ويحمي السيرفر
"""

from functools import wraps
import time
from typing import Dict, Callable
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    نظام التحكم في معدل الطلبات
    
    يتتبع عدد الطلبات لكل مستخدم ويمنع تجاوز الحد المسموح
    """
    
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        """
        Args:
            max_requests: الحد الأقصى للطلبات
            time_window: النافذة الزمنية بالثواني
        """
        self.max_requests = max_requests
        self.time_window = time_window
        
        # تخزين: {user_id: [(timestamp1, timestamp2, ...)]}
        self.requests: Dict[int, list] = defaultdict(list)
        
        logger.info(f"✅ Rate Limiter مفعّل: {max_requests} طلب/{time_window}ث")
    
    def is_allowed(self, user_id: int) -> tuple[bool, int]:
        """
        فحص ما إذا كان المستخدم يمكنه إرسال طلب جديد
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            tuple: (مسموح؟, الوقت المتبقي للانتظار)
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # حذف الطلبات القديمة (خارج النافذة الزمنية)
        cutoff_time = now - self.time_window
        user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
        
        # فحص العدد
        if len(user_requests) >= self.max_requests:
            # حساب الوقت المتبقي
            oldest_request = user_requests[0]
            time_until_allowed = int(oldest_request + self.time_window - now) + 1
            
            logger.warning(
                f"⚠️ Rate limit reached for user {user_id}: "
                f"{len(user_requests)}/{self.max_requests} requests"
            )
            
            return False, time_until_allowed
        
        # إضافة الطلب الجديد
        user_requests.append(now)
        return True, 0
    
    def get_remaining_requests(self, user_id: int) -> int:
        """
        عدد الطلبات المتبقية للمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            int: عدد الطلبات المتبقية
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # حذف الطلبات القديمة
        cutoff_time = now - self.time_window
        user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
        
        return max(0, self.max_requests - len(user_requests))
    
    def reset_user(self, user_id: int):
        """إعادة تعيين عداد المستخدم"""
        if user_id in self.requests:
            del self.requests[user_id]
            logger.info(f"🔄 Reset rate limit for user {user_id}")
    
    def get_stats(self, user_id: int) -> Dict:
        """
        إحصائيات الاستخدام للمستخدم
        
        Returns:
            dict: إحصائيات مفصلة
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # حذف الطلبات القديمة
        cutoff_time = now - self.time_window
        user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
        
        return {
            'current_requests': len(user_requests),
            'max_requests': self.max_requests,
            'remaining': self.max_requests - len(user_requests),
            'time_window': self.time_window,
            'percentage_used': (len(user_requests) / self.max_requests) * 100
        }


# Decorator لسهولة الاستخدام
def rate_limit(max_requests: int = 30, time_window: int = 60):
    """
    Decorator للتحكم في معدل الطلبات
    
    Usage:
        @rate_limit(max_requests=30, time_window=60)
        async def my_handler(update, context):
            ...
    """
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            
            # فحص Rate Limit
            allowed, wait_time = limiter.is_allowed(user_id)
            
            if not allowed:
                # رسالة تحذير بثلاث لغات
                warning_message = f"""⏰ **الكثير من الطلبات! | Trop de requêtes! | Too many requests!**

🇸🇦 انتظر {wait_time} ثانية من فضلك
🇫🇷 Attendez {wait_time} secondes s'il vous plaît
🇬🇧 Please wait {wait_time} seconds

💡 الحد المسموح: {limiter.max_requests} طلب/{limiter.time_window}ث
💡 Limite: {limiter.max_requests} req/{limiter.time_window}s"""
                
                await update.message.reply_text(warning_message, parse_mode='Markdown')
                
                logger.warning(
                    f"⛔ Rate limit blocked user {user_id}. "
                    f"Wait {wait_time}s"
                )
                return
            
            # تنفيذ الدالة
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    
    return decorator


# ==========================================
# مثال على الاستخدام
# ==========================================

if __name__ == "__main__":
    import asyncio
    
    print("="*70)
    print("🧪 اختبار Rate Limiter")
    print("="*70)
    
    # إنشاء limiter
    limiter = RateLimiter(max_requests=5, time_window=10)
    
    # محاكاة طلبات مستخدم
    user_id = 123456
    
    print(f"\n📊 المستخدم {user_id}:")
    print(f"   الحد الأقصى: {limiter.max_requests} طلبات/{limiter.time_window}ث\n")
    
    # إرسال 7 طلبات
    for i in range(1, 8):
        allowed, wait_time = limiter.is_allowed(user_id)
        
        if allowed:
            remaining = limiter.get_remaining_requests(user_id)
            print(f"  ✅ طلب #{i}: مسموح ({remaining} متبقي)")
        else:
            print(f"  ⛔ طلب #{i}: مرفوض (انتظر {wait_time}ث)")
        
        time.sleep(0.5)
    
    # عرض الإحصائيات
    print(f"\n📈 الإحصائيات:")
    stats = limiter.get_stats(user_id)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   • {key}: {value:.1f}")
        else:
            print(f"   • {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ الاختبار اكتمل!")