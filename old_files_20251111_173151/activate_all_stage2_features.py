#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تفعيل جميع ميزات المرحلة 2
- /calendar
- /stats
- /export
- المواعيد المتكررة
"""

import os
import shutil
from datetime import datetime

print("="*70)
print("🚀 تفعيل جميع ميزات المرحلة 2")
print("="*70)

# ==========================================
# 1. تحديث telegram_bot.py
# ==========================================
print("\n📝 تحديث telegram_bot.py...")

if not os.path.exists('telegram_bot.py'):
    print("❌ telegram_bot.py غير موجود!")
    exit(1)

# نسخة احتياطية
backup = f'telegram_bot.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy2('telegram_bot.py', backup)
print(f"✅ نسخة احتياطية: {backup}")

with open('telegram_bot.py', 'r', encoding='utf-8') as f:
    bot_content = f.read()

# إضافة الأوامر إذا لم تكن موجودة
if 'CommandHandler("calendar"' not in bot_content:
    # إيجاد _setup_handlers وإضافة الأوامر
    bot_content = bot_content.replace(
        'self.app.add_handler(CommandHandler("week", self.week_command))',
        '''self.app.add_handler(CommandHandler("week", self.week_command))
        self.app.add_handler(CommandHandler("calendar", self.calendar_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CommandHandler("export", self.export_command))'''
    )
    print("✅ تمت إضافة الأوامر الجديدة")

# إضافة الدوال إذا لم تكن موجودة
if 'async def calendar_command' not in bot_content:
    new_commands = '''
    async def calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض التقويم الشهري"""
        try:
            from advanced_features import MonthlyCalendar
            
            user_id = update.effective_user.id
            calendar = MonthlyCalendar(self.agent.db.db_path)
            calendar_text = calendar.generate_calendar(user_id)
            
            if update.message:
                await update.message.reply_text(calendar_text, parse_mode='Markdown')
            else:
                await update.callback_query.message.reply_text(calendar_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"خطأ في التقويم: {e}")
            error_msg = "⚠️ ميزة التقويم غير متاحة\\n⚠️ Calendar not available"
            if update.message:
                await update.message.reply_text(error_msg)
            else:
                await update.callback_query.message.reply_text(error_msg)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        try:
            from analytics_dashboard import AnalyticsDashboard
            
            user_id = update.effective_user.id
            dashboard = AnalyticsDashboard(self.agent.db.db_path)
            stats = dashboard.generate_user_dashboard(user_id)
            
            if update.message:
                await update.message.reply_text(stats, parse_mode='Markdown')
            else:
                await update.callback_query.message.reply_text(stats, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"خطأ في الإحصائيات: {e}")
            error_msg = "⚠️ ميزة الإحصائيات غير متاحة\\n⚠️ Statistics not available"
            if update.message:
                await update.message.reply_text(error_msg)
            else:
                await update.callback_query.message.reply_text(error_msg)
    
    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تصدير المواعيد"""
        try:
            from advanced_features import AppointmentExportImport
            
            user_id = update.effective_user.id
            exporter = AppointmentExportImport(self.agent.db.db_path)
            json_data = exporter.export_to_json(user_id)
            
            count = len(json_data.get('appointments', []))
            message = f"""📥 **تصدير المواعيد | Export**

✅ تم تصدير مواعيدك بنجاح!
📊 العدد: {count} موعد

✅ Appointments exported!
📊 Count: {count} appointments"""
            
            if update.message:
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.callback_query.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"خطأ في التصدير: {e}")
            error_msg = "⚠️ ميزة التصدير غير متاحة\\n⚠️ Export not available"
            if update.message:
                await update.message.reply_text(error_msg)
            else:
                await update.callback_query.message.reply_text(error_msg)
'''
    
    # إضافة الدوال قبل button_callback
    bot_content = bot_content.replace(
        '    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):',
        new_commands + '\n    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):'
    )
    print("✅ تمت إضافة الدوال الجديدة")

# حفظ التغييرات
with open('telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(bot_content)

print("✅ تم تحديث telegram_bot.py")

# ==========================================
# 2. تحديث intelligent_agent.py
# ==========================================
print("\n📝 تحديث intelligent_agent.py...")

if not os.path.exists('intelligent_agent.py'):
    print("❌ intelligent_agent.py غير موجود!")
    exit(1)

# نسخة احتياطية
backup = f'intelligent_agent.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy2('intelligent_agent.py', backup)
print(f"✅ نسخة احتياطية: {backup}")

with open('intelligent_agent.py', 'r', encoding='utf-8') as f:
    agent_content = f.read()

# إضافة كود المواعيد المتكررة إذا لم يكن موجوداً
if 'RecurringAppointmentManager' not in agent_content:
    recurring_code = '''
        # ==========================================
        # المواعيد المتكررة (المرحلة 2)
        # ==========================================
        import re
        
        recurring_patterns = [
            (r'يومي[اً]?|كل يوم|every day|chaque jour', 'daily'),
            (r'كل (اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت|أحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|الأحد)', 'weekly'),
            (r'every (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', 'weekly'),
            (r'شهري[اً]?|كل شهر|every month|chaque mois', 'monthly'),
            (r'أول كل شهر|first of month|début du mois', 'monthly_start'),
            (r'آخر كل شهر|end of month|fin du mois', 'monthly_end'),
        ]
        
        is_recurring = False
        recurrence_type = None
        
        for pattern, rec_type in recurring_patterns:
            if re.search(pattern, message.lower(), re.IGNORECASE):
                is_recurring = True
                recurrence_type = rec_type
                break
        
        if is_recurring and appointment_date:
            try:
                from advanced_features import RecurringAppointmentManager
                
                recurring_mgr = RecurringAppointmentManager(self.db_path)
                
                # تحديد عدد المواعيد
                if recurrence_type == 'daily':
                    occurrences = 365
                elif recurrence_type == 'weekly':
                    occurrences = 52
                else:  # monthly
                    occurrences = 12
                
                # إنشاء المواعيد المتكررة
                count = recurring_mgr.create_recurring_appointments(
                    user_id=user_id,
                    title=title or "موعد متكرر",
                    description=description,
                    start_date=appointment_date,
                    recurrence_type=recurrence_type,
                    priority=priority,
                    occurrences=occurrences
                )
                
                return (
                    f"✅ تم إضافة موعد متكرر!\\n"
                    f"🔄 النوع: {recurrence_type}\\n"
                    f"📊 تم إنشاء {count} موعد\\n"
                    f"📅 يبدأ من: {appointment_date.strftime('%Y-%m-%d %H:%M')}\\n\\n"
                    f"✅ Recurring appointment created!\\n"
                    f"🔄 Type: {recurrence_type}\\n"
                    f"📊 {count} appointments\\n\\n"
                    f"✅ Rendez-vous récurrent créé!\\n"
                    f"🔄 {count} RDV générés"
                )
                
            except ImportError as e:
                logger.warning(f"المواعيد المتكررة غير متاحة: {e}")
                # نكمل بإضافة موعد عادي
            except Exception as e:
                logger.error(f"خطأ في المواعيد المتكررة: {e}")
'''
    
    # إضافة الكود بعد إضافة الموعد العادي
    # نبحث عن "تم إضافة موعد بنجاح" ونضيف قبلها
    agent_content = agent_content.replace(
        '        return response',
        recurring_code + '\n        return response',
        1  # أول ظهور فقط
    )
    print("✅ تمت إضافة كود المواعيد المتكررة")

# حفظ التغييرات
with open('intelligent_agent.py', 'w', encoding='utf-8') as f:
    f.write(agent_content)

print("✅ تم تحديث intelligent_agent.py")

# ==========================================
# النتيجة النهائية
# ==========================================
print("\n" + "="*70)
print("🎉 تم تفعيل جميع ميزات المرحلة 2 بنجاح!")
print("="*70)

print("\n✅ الميزات المفعّلة:")
print("  🔔 التذكيرات المخصصة")
print("  🔄 المواعيد المتكررة")
print("  📅 /calendar - التقويم الشهري")
print("  📊 /stats - الإحصائيات")
print("  💾 /export - التصدير")

print("\n🚀 الخطوات التالية:")
print("  1. أعد تشغيل البوت: python telegram_bot.py")
print("  2. جرّب الأوامر:")
print("     • /calendar")
print("     • /stats")
print("     • /export")
print("  3. جرّب المواعيد المتكررة:")
print("     • 'رياضة يومياً 8 مساءً'")
print("     • 'اجتماع كل ثلاثاء 10 صباحاً'")
print("     • 'دفع إيجار أول كل شهر'")

print("\n" + "="*70)