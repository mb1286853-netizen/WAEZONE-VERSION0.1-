import time
from datetime import datetime

def format_number(number):
    """فرمت اعداد با جداکننده هزارگان"""
    return f"{number:,}"

def format_time(seconds):
    """فرمت زمان به صورت خوانا"""
    if seconds < 60:
        return f"{seconds} ثانیه"
    elif seconds < 3600:
        return f"{seconds // 60} دقیقه"
    elif seconds < 86400:
        return f"{seconds // 3600} ساعت"
    else:
        return f"{seconds // 86400} روز"

def get_time_until_next_hour():
    """زمان تا ساعت بعدی"""
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return int((next_hour - now).total_seconds())

def create_progress_bar(current, total, length=20):
    """ایجاد نوار پیشرفت"""
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    return f"{bar} {percent:.1%}"

def is_cooldown_passed(last_timestamp, cooldown_seconds):
    """بررسی گذشتن زمان کول‌داون"""
    if not last_timestamp:
        return True
    return (time.time() - last_timestamp) >= cooldown_seconds
