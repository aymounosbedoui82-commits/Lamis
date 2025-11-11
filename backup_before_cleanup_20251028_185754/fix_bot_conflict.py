#!/usr/bin/env python3
# fix_bot_conflict.py
"""
حل مشكلة تعارض البوت
"""

import requests
import os

# ضع Token البوت هنا
BOT_TOKEN = "7547352296:AAH1tuIgQ2uGPx93bxCGWTRJUithRcwIhn0"

print("="*60)
print("🔧 إصلاح تعارض البوت")
print("="*60)

# 1. حذف الـ Webhook
print("\n1️⃣ حذف Webhook...")
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true")
print(f"   النتيجة: {response.json()}")

# 2. الحصول على معلومات البوت
print("\n2️⃣ فحص حالة البوت...")
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
if response.status_code == 200:
    bot_info = response.json()['result']
    print(f"   ✅ البوت: @{bot_info['username']}")
    print(f"   ID: {bot_info['id']}")
else:
    print(f"   ❌ خطأ: {response.text}")

# 3. فحص الـ Webhook
print("\n3️⃣ فحص Webhook...")
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
webhook_info = response.json()['result']
if webhook_info.get('url'):
    print(f"   ⚠️ Webhook مُفعّل: {webhook_info['url']}")
else:
    print(f"   ✅ لا يوجد Webhook")

print("\n" + "="*60)
print("✅ تم الإصلاح! الآن يمكنك تشغيل البوت")
print("="*60)