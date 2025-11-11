#!/usr/bin/env python3
# force_reset_bot.py
"""
إعادة تعيين البوت بالقوة
"""

import requests
import time
import subprocess
import os

BOT_TOKEN = "7547352296:AAH1tuIgQ2uGPx93bxCGWTRJUithRcwIhn0"

def kill_all_python():
    """قتل جميع عمليات Python"""
    print("🛑 إيقاف جميع عمليات Python...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(2)
        print("   ✅ تم")
    except:
        print("   ⚠️ لم يتم العثور على عمليات")

def force_webhook_delete():
    """حذف الـ Webhook بالقوة"""
    print("\n🔄 حذف Webhook بالقوة...")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    
    # محاولة 3 مرات
    for i in range(3):
        try:
            response = requests.post(url, 
                                    json={"drop_pending_updates": True},
                                    timeout=10)
            print(f"   محاولة {i+1}: {response.json()}")
            
            if response.status_code == 200:
                print("   ✅ نجح!")
                return True
        except Exception as e:
            print(f"   ❌ فشل: {e}")
        
        time.sleep(2)
    
    return False

def verify_bot():
    """التحقق من حالة البوت"""
    print("\n🔍 التحقق من حالة البوت...")
    
    try:
        # 1. معلومات البوت
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",
            timeout=10
        )
        bot_info = response.json()['result']
        print(f"   ✅ البوت: @{bot_info['username']}")
        
        # 2. حالة الـ Webhook
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo",
            timeout=10
        )
        webhook = response.json()['result']
        
        if webhook.get('url'):
            print(f"   ⚠️ Webhook مُفعّل: {webhook['url']}")
            print(f"      Pending updates: {webhook.get('pending_update_count', 0)}")
            return False
        else:
            print(f"   ✅ لا يوجد Webhook")
            print(f"      Pending updates: {webhook.get('pending_update_count', 0)}")
            return True
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔧 إعادة تعيين البوت بالقوة")
    print("="*60)
    
    # 1. قتل كل Python
    kill_all_python()
    
    # 2. حذف Webhook
    force_webhook_delete()
    
    # 3. التحقق
    time.sleep(3)
    is_ready = verify_bot()
    
    print("\n" + "="*60)
    if is_ready:
        print("✅ البوت جاهز للتشغيل!")
        print("\nالآن شغّل: python telegram_bot.py")
    else:
        print("⚠️ قد تحتاج لإعادة المحاولة")
        print("\nانتظر دقيقة ثم شغّل هذا السكريبت مرة أخرى")
    print("="*60)