# structured_logger.py
"""
نظام Logging محسّن ومنظم
✅ يدعم JSON format للتحليل السهل
✅ تدوير تلقائي للملفات
✅ مستويات logging مختلفة
✅ Metrics collection
"""

import logging
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import sys


class StructuredLogger:
    """Logger منظم مع دعم JSON"""
    
    def __init__(
        self,
        name: str = "LamisBot",
        log_level: str = "INFO",
        log_file: str = "lamis_bot.log",
        json_file: str = "lamis_bot.json",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """
        Args:
            name: اسم Logger
            log_level: مستوى التسجيل (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: ملف Log النصي
            json_file: ملف Log بصيغة JSON
            max_bytes: حجم الملف الأقصى قبل التدوير
            backup_count: عدد الملفات الاحتياطية
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # منع التكرار
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # إنشاء مجلد logs
        Path("logs").mkdir(exist_ok=True)
        
        # إعداد المعالجات
        self._setup_console_handler()
        self._setup_file_handler(f"logs/{log_file}", max_bytes, backup_count)
        self._setup_json_handler(f"logs/{json_file}", max_bytes, backup_count)
        self._setup_error_handler()
        
        # إحصائيات
        self.stats = {
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'debug': 0
        }
        
        self.logger.info("="*70)
        self.logger.info(f"✅ Structured Logger initialized: {name}")
        self.logger.info(f"   Log Level: {log_level}")
        self.logger.info(f"   Text Log: logs/{log_file}")
        self.logger.info(f"   JSON Log: logs/{json_file}")
        self.logger.info("="*70)
    
    def _setup_console_handler(self):
        """إعداد معالج Console (للشاشة)"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # تنسيق ملون
        console_format = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self, filename: str, max_bytes: int, backup_count: int):
        """إعداد معالج File (للملف النصي)"""
        file_handler = RotatingFileHandler(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(file_handler)
    
    def _setup_json_handler(self, filename: str, max_bytes: int, backup_count: int):
        """إعداد معالج JSON"""
        json_handler = RotatingFileHandler(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(json_handler)
    
    def _setup_error_handler(self):
        """إعداد معالج خاص بالأخطاء فقط"""
        error_handler = RotatingFileHandler(
            "logs/errors.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        error_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s\n"
            "File: %(pathname)s:%(lineno)d\n"
            "Function: %(funcName)s\n"
            "%(exc_info)s\n" + "="*70,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        error_handler.setFormatter(error_format)
        
        self.logger.addHandler(error_handler)
    
    def log(
        self,
        level: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        تسجيل رسالة مع بيانات إضافية
        
        Args:
            level: مستوى التسجيل
            message: الرسالة
            extra_data: بيانات إضافية
        """
        self.stats['total_logs'] += 1
        
        # تحديث الإحصائيات
        level_lower = level.lower()
        if level_lower in self.stats:
            self.stats[level_lower] += 1
        
        # إضافة البيانات الإضافية
        extra = extra_data or {}
        extra.update(kwargs)
        
        # التسجيل
        log_func = getattr(self.logger, level_lower)
        log_func(message, extra={'data': extra})
    
    def info(self, message: str, **kwargs):
        """تسجيل معلومة"""
        self.log("INFO", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """تسجيل debug"""
        self.log("DEBUG", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """تسجيل تحذير"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """تسجيل خطأ"""
        self.log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """تسجيل خطأ حرج"""
        self.log("CRITICAL", message, **kwargs)
    
    def log_appointment_added(self, user_id: int, appointment_id: int, title: str):
        """تسجيل إضافة موعد"""
        self.info(
            f"📅 Appointment added",
            event="appointment_added",
            user_id=user_id,
            appointment_id=appointment_id,
            title=title
        )
    
    def log_reminder_sent(self, user_id: int, appointment_id: int, reminder_type: str):
        """تسجيل إرسال تذكير"""
        self.info(
            f"🔔 Reminder sent",
            event="reminder_sent",
            user_id=user_id,
            appointment_id=appointment_id,
            reminder_type=reminder_type
        )
    
    def log_user_interaction(self, user_id: int, message: str, intent: str, language: str):
        """تسجيل تفاعل المستخدم"""
        self.info(
            f"💬 User interaction",
            event="user_interaction",
            user_id=user_id,
            message=message[:100],  # أول 100 حرف فقط
            intent=intent,
            language=language
        )
    
    def log_error_with_context(
        self,
        error_type: str,
        message: str,
        user_id: Optional[int] = None,
        traceback_info: Optional[str] = None
    ):
        """تسجيل خطأ مع سياق"""
        self.error(
            f"❌ Error: {error_type}",
            event="error",
            error_type=error_type,
            error_message=message,
            user_id=user_id,
            traceback=traceback_info
        )
    
    def get_stats(self) -> Dict[str, int]:
        """الحصول على إحصائيات التسجيل"""
        return self.stats.copy()
    
    def print_stats(self):
        """طباعة الإحصائيات"""
        print("\n" + "="*70)
        print("📊 إحصائيات Logging")
        print("="*70)
        for key, value in self.stats.items():
            print(f"  {key:20s}: {value:,}")
        print("="*70 + "\n")


class JSONFormatter(logging.Formatter):
    """محول JSON للتسجيل"""
    
    def format(self, record):
        """تحويل السجل إلى JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # إضافة البيانات الإضافية
        if hasattr(record, 'data'):
            log_data['data'] = record.data
        
        # إضافة معلومات الخطأ
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """محول ملون للـ Console"""
    
    # رموز الألوان ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """تطبيق الألوان"""
        # إضافة اللون
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)


# ==========================================
# Metrics Collector
# ==========================================

class MetricsCollector:
    """جامع المقاييس والإحصائيات"""
    
    def __init__(self):
        self.metrics = {
            'appointments_created': 0,
            'appointments_cancelled': 0,
            'reminders_sent': 0,
            'messages_processed': 0,
            'errors_occurred': 0,
            'users_active': set()
        }
    
    def increment(self, metric_name: str, value: int = 1):
        """زيادة مقياس"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def add_user(self, user_id: int):
        """إضافة مستخدم نشط"""
        self.metrics['users_active'].add(user_id)
    
    def get_metrics(self) -> Dict:
        """الحصول على المقاييس"""
        metrics = self.metrics.copy()
        metrics['users_active'] = len(self.metrics['users_active'])
        return metrics
    
    def print_metrics(self):
        """طباعة المقاييس"""
        print("\n" + "="*70)
        print("📈 Metrics")
        print("="*70)
        metrics = self.get_metrics()
        for key, value in metrics.items():
            if isinstance(value, int):
                print(f"  {key:30s}: {value:,}")
        print("="*70 + "\n")


# ==========================================
# Global Instance
# ==========================================

# إنشاء logger عام
app_logger = StructuredLogger()
metrics = MetricsCollector()


# ==========================================
# اختبار
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 اختبار Structured Logger")
    print("="*70)
    
    # إنشاء logger
    logger = StructuredLogger(
        name="TestLogger",
        log_level="DEBUG"
    )
    
    # اختبار مستويات مختلفة
    print("\n📝 اختبار مستويات التسجيل:\n")
    
    logger.debug("رسالة debug", key="value")
    logger.info("رسالة معلومات", user_id=123)
    logger.warning("تحذير", reason="test")
    logger.error("خطأ", error_code=500)
    
    # اختبار logging خاص
    print("\n📅 اختبار logging المخصص:\n")
    
    logger.log_appointment_added(
        user_id=123,
        appointment_id=1,
        title="موعد مع الطبيب"
    )
    
    logger.log_reminder_sent(
        user_id=123,
        appointment_id=1,
        reminder_type="1_hour_before"
    )
    
    logger.log_user_interaction(
        user_id=123,
        message="موعد غداً",
        intent="add_appointment",
        language="ar"
    )
    
    # عرض الإحصائيات
    logger.print_stats()
    
    # اختبار metrics
    print("📊 اختبار Metrics:\n")
    
    metrics_collector = MetricsCollector()
    metrics_collector.increment('appointments_created', 5)
    metrics_collector.increment('reminders_sent', 10)
    metrics_collector.add_user(123)
    metrics_collector.add_user(456)
    
    metrics_collector.print_metrics()
    
    print("="*70)
    print("✅ الاختبار اكتمل!")
    print(f"📂 تحقق من مجلد logs/ لرؤية الملفات")
    print("="*70)