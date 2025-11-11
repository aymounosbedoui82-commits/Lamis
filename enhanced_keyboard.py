# enhanced_keyboard.py
"""
نظام Inline Keyboard محسّن ومتطور
✅ المرحلة 2: تحسينات واجهة المستخدم
✅ أزرار جميلة وتفاعلية بثلاث لغات
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnhancedKeyboard:
    """مولد لوحات مفاتيح تفاعلية محسّنة"""
    
    # Emojis
    EMOJIS = {
        'calendar': '📅',
        'add': '➕',
        'list': '📋',
        'delete': '🗑️',
        'edit': '✏️',
        'settings': '⚙️',
        'help': 'ℹ️',
        'back': '◀️',
        'next': '▶️',
        'home': '🏠',
        'today': '📆',
        'week': '📅',
        'month': '🗓️',
        'search': '🔍',
        'export': '💾',
        'stats': '📊',
        'reminder': '🔔',
        'priority': '⚡',
        'recurring': '🔄',
        'done': '✅',
        'cancel': '❌',
        'time': '⏰',
        'language': '🌍'
    }
    
    @classmethod
    def main_menu(cls, language: str = 'ar') -> InlineKeyboardMarkup:
        """
        القائمة الرئيسية المحسّنة
        
        Args:
            language: اللغة (ar/fr/en)
        """
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['add']} إضافة موعد",
                        callback_data='action_add'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['list']} مواعيدي",
                        callback_data='action_list'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['today']} اليوم",
                        callback_data='action_today'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['week']} الأسبوع",
                        callback_data='action_week'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['month']} الشهر",
                        callback_data='action_month'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['stats']} إحصائيات",
                        callback_data='action_stats'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['export']} تصدير",
                        callback_data='action_export'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['settings']} إعدادات",
                        callback_data='action_settings'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['help']} مساعدة",
                        callback_data='action_help'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['add']} Ajouter RDV",
                        callback_data='action_add'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['list']} Mes RDV",
                        callback_data='action_list'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['today']} Aujourd'hui",
                        callback_data='action_today'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['week']} Semaine",
                        callback_data='action_week'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['month']} Mois",
                        callback_data='action_month'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['stats']} Statistiques",
                        callback_data='action_stats'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['export']} Exporter",
                        callback_data='action_export'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['settings']} Paramètres",
                        callback_data='action_settings'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['help']} Aide",
                        callback_data='action_help'
                    )
                ]
            ]
        
        else:  # English
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['add']} Add Appointment",
                        callback_data='action_add'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['list']} My Appointments",
                        callback_data='action_list'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['today']} Today",
                        callback_data='action_today'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['week']} Week",
                        callback_data='action_week'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['month']} Month",
                        callback_data='action_month'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['stats']} Statistics",
                        callback_data='action_stats'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['export']} Export",
                        callback_data='action_export'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['settings']} Settings",
                        callback_data='action_settings'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['help']} Help",
                        callback_data='action_help'
                    )
                ]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def appointment_actions(
        cls,
        appointment_id: int,
        language: str = 'ar'
    ) -> InlineKeyboardMarkup:
        """
        أزرار الإجراءات لموعد محدد
        
        Args:
            appointment_id: معرف الموعد
            language: اللغة
        """
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['edit']} تعديل",
                        callback_data=f'edit_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['delete']} حذف",
                        callback_data=f'delete_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['reminder']} تذكيرات",
                        callback_data=f'remind_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['done']} تم",
                        callback_data=f'done_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['back']} رجوع",
                        callback_data='action_list'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['edit']} Modifier",
                        callback_data=f'edit_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['delete']} Supprimer",
                        callback_data=f'delete_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['reminder']} Rappels",
                        callback_data=f'remind_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['done']} Terminé",
                        callback_data=f'done_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['back']} Retour",
                        callback_data='action_list'
                    )
                ]
            ]
        
        else:  # English
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['edit']} Edit",
                        callback_data=f'edit_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['delete']} Delete",
                        callback_data=f'delete_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['reminder']} Reminders",
                        callback_data=f'remind_{appointment_id}'
                    ),
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['done']} Mark Done",
                        callback_data=f'done_{appointment_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['back']} Back",
                        callback_data='action_list'
                    )
                ]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def priority_selector(cls, language: str = 'ar') -> InlineKeyboardMarkup:
        """محدد الأولوية"""
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔴 عاجل",
                        callback_data='priority_1'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🟡 متوسط",
                        callback_data='priority_2'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🟢 منخفض",
                        callback_data='priority_3'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['cancel']} إلغاء",
                        callback_data='cancel'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [InlineKeyboardButton("🔴 Urgent", callback_data='priority_1')],
                [InlineKeyboardButton("🟡 Moyen", callback_data='priority_2')],
                [InlineKeyboardButton("🟢 Faible", callback_data='priority_3')],
                [InlineKeyboardButton(f"{cls.EMOJIS['cancel']} Annuler", callback_data='cancel')]
            ]
        
        else:  # English
            keyboard = [
                [InlineKeyboardButton("🔴 Urgent", callback_data='priority_1')],
                [InlineKeyboardButton("🟡 Medium", callback_data='priority_2')],
                [InlineKeyboardButton("🟢 Low", callback_data='priority_3')],
                [InlineKeyboardButton(f"{cls.EMOJIS['cancel']} Cancel", callback_data='cancel')]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def reminder_options(cls, language: str = 'ar') -> InlineKeyboardMarkup:
        """خيارات التذكير"""
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        "⏰ 15 دقيقة قبل",
                        callback_data='reminder_15'
                    ),
                    InlineKeyboardButton(
                        "⏰ 30 دقيقة قبل",
                        callback_data='reminder_30'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏰ 1 ساعة قبل",
                        callback_data='reminder_60'
                    ),
                    InlineKeyboardButton(
                        "⏰ 2 ساعة قبل",
                        callback_data='reminder_120'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏰ 24 ساعة قبل",
                        callback_data='reminder_1440'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"✏️ تذكير مخصص",
                        callback_data='reminder_custom'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['back']} رجوع",
                        callback_data='back'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [
                    InlineKeyboardButton("⏰ 15 min avant", callback_data='reminder_15'),
                    InlineKeyboardButton("⏰ 30 min avant", callback_data='reminder_30')
                ],
                [
                    InlineKeyboardButton("⏰ 1h avant", callback_data='reminder_60'),
                    InlineKeyboardButton("⏰ 2h avant", callback_data='reminder_120')
                ],
                [InlineKeyboardButton("⏰ 24h avant", callback_data='reminder_1440')],
                [InlineKeyboardButton("✏️ Personnalisé", callback_data='reminder_custom')],
                [InlineKeyboardButton(f"{cls.EMOJIS['back']} Retour", callback_data='back')]
            ]
        
        else:  # English
            keyboard = [
                [
                    InlineKeyboardButton("⏰ 15 min before", callback_data='reminder_15'),
                    InlineKeyboardButton("⏰ 30 min before", callback_data='reminder_30')
                ],
                [
                    InlineKeyboardButton("⏰ 1h before", callback_data='reminder_60'),
                    InlineKeyboardButton("⏰ 2h before", callback_data='reminder_120')
                ],
                [InlineKeyboardButton("⏰ 24h before", callback_data='reminder_1440')],
                [InlineKeyboardButton("✏️ Custom", callback_data='reminder_custom')],
                [InlineKeyboardButton(f"{cls.EMOJIS['back']} Back", callback_data='back')]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def recurring_pattern_selector(cls, language: str = 'ar') -> InlineKeyboardMarkup:
        """محدد نمط التكرار"""
        if language == 'ar':
            keyboard = [
                [InlineKeyboardButton("🔄 يومياً", callback_data='pattern_daily')],
                [InlineKeyboardButton("🔄 أسبوعياً", callback_data='pattern_weekly')],
                [InlineKeyboardButton("🔄 كل أسبوعين", callback_data='pattern_biweekly')],
                [InlineKeyboardButton("🔄 شهرياً", callback_data='pattern_monthly')],
                [InlineKeyboardButton("🔄 سنوياً", callback_data='pattern_yearly')],
                [InlineKeyboardButton(f"{cls.EMOJIS['cancel']} إلغاء", callback_data='cancel')]
            ]
        
        elif language == 'fr':
            keyboard = [
                [InlineKeyboardButton("🔄 Quotidien", callback_data='pattern_daily')],
                [InlineKeyboardButton("🔄 Hebdomadaire", callback_data='pattern_weekly')],
                [InlineKeyboardButton("🔄 Bihebdomadaire", callback_data='pattern_biweekly')],
                [InlineKeyboardButton("🔄 Mensuel", callback_data='pattern_monthly')],
                [InlineKeyboardButton("🔄 Annuel", callback_data='pattern_yearly')],
                [InlineKeyboardButton(f"{cls.EMOJIS['cancel']} Annuler", callback_data='cancel')]
            ]
        
        else:  # English
            keyboard = [
                [InlineKeyboardButton("🔄 Daily", callback_data='pattern_daily')],
                [InlineKeyboardButton("🔄 Weekly", callback_data='pattern_weekly')],
                [InlineKeyboardButton("🔄 Biweekly", callback_data='pattern_biweekly')],
                [InlineKeyboardButton("🔄 Monthly", callback_data='pattern_monthly')],
                [InlineKeyboardButton("🔄 Yearly", callback_data='pattern_yearly')],
                [InlineKeyboardButton(f"{cls.EMOJIS['cancel']} Cancel", callback_data='cancel')]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def export_options(cls, language: str = 'ar') -> InlineKeyboardMarkup:
        """خيارات التصدير"""
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        "💾 JSON",
                        callback_data='export_json'
                    ),
                    InlineKeyboardButton(
                        "📊 CSV",
                        callback_data='export_csv'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📄 PDF (قريباً)",
                        callback_data='export_pdf_soon'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['back']} رجوع",
                        callback_data='back'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [
                    InlineKeyboardButton("💾 JSON", callback_data='export_json'),
                    InlineKeyboardButton("📊 CSV", callback_data='export_csv')
                ],
                [InlineKeyboardButton("📄 PDF (bientôt)", callback_data='export_pdf_soon')],
                [InlineKeyboardButton(f"{cls.EMOJIS['back']} Retour", callback_data='back')]
            ]
        
        else:  # English
            keyboard = [
                [
                    InlineKeyboardButton("💾 JSON", callback_data='export_json'),
                    InlineKeyboardButton("📊 CSV", callback_data='export_csv')
                ],
                [InlineKeyboardButton("📄 PDF (soon)", callback_data='export_pdf_soon')],
                [InlineKeyboardButton(f"{cls.EMOJIS['back']} Back", callback_data='back')]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def confirmation(
        cls,
        action: str,
        item_id: int,
        language: str = 'ar'
    ) -> InlineKeyboardMarkup:
        """لوحة تأكيد"""
        if language == 'ar':
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['done']} نعم، متأكد",
                        callback_data=f'confirm_{action}_{item_id}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"{cls.EMOJIS['cancel']} لا، إلغاء",
                        callback_data='cancel'
                    )
                ]
            ]
        
        elif language == 'fr':
            keyboard = [
                [InlineKeyboardButton(
                    f"{cls.EMOJIS['done']} Oui, confirmer",
                    callback_data=f'confirm_{action}_{item_id}'
                )],
                [InlineKeyboardButton(
                    f"{cls.EMOJIS['cancel']} Non, annuler",
                    callback_data='cancel'
                )]
            ]
        
        else:  # English
            keyboard = [
                [InlineKeyboardButton(
                    f"{cls.EMOJIS['done']} Yes, confirm",
                    callback_data=f'confirm_{action}_{item_id}'
                )],
                [InlineKeyboardButton(
                    f"{cls.EMOJIS['cancel']} No, cancel",
                    callback_data='cancel'
                )]
            ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def pagination(
        cls,
        current_page: int,
        total_pages: int,
        callback_prefix: str = 'page'
    ) -> InlineKeyboardMarkup:
        """أزرار التنقل بين الصفحات"""
        keyboard = []
        
        nav_row = []
        
        # زر السابق
        if current_page > 1:
            nav_row.append(
                InlineKeyboardButton(
                    f"{cls.EMOJIS['back']} السابق",
                    callback_data=f'{callback_prefix}_{current_page - 1}'
                )
            )
        
        # الصفحة الحالية
        nav_row.append(
            InlineKeyboardButton(
                f"📄 {current_page}/{total_pages}",
                callback_data='page_info'
            )
        )
        
        # زر التالي
        if current_page < total_pages:
            nav_row.append(
                InlineKeyboardButton(
                    f"التالي {cls.EMOJIS['next']}",
                    callback_data=f'{callback_prefix}_{current_page + 1}'
                )
            )
        
        keyboard.append(nav_row)
        
        # زر الرجوع للقائمة
        keyboard.append([
            InlineKeyboardButton(
                f"{cls.EMOJIS['home']} القائمة الرئيسية",
                callback_data='action_home'
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار Enhanced Keyboard")
    print("="*70)
    
    kb = EnhancedKeyboard()
    
    print("\n📋 القوائم المتاحة:")
    print("-"*70)
    
    menus = [
        ("main_menu", "القائمة الرئيسية"),
        ("appointment_actions", "إجراءات الموعد"),
        ("priority_selector", "محدد الأولوية"),
        ("reminder_options", "خيارات التذكير"),
        ("recurring_pattern_selector", "أنماط التكرار"),
        ("export_options", "خيارات التصدير"),
        ("confirmation", "التأكيد"),
        ("pagination", "التنقل")
    ]
    
    for method_name, description in menus:
        print(f"  ✅ {description:30s} → {method_name}()")
    
    print("\n" + "="*70)
    print("✅ جميع لوحات المفاتيح جاهزة!")
    print("\n💡 استخدم هذه اللوحات في telegram_bot.py")