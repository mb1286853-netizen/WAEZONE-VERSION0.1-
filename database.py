import sqlite3  # این خط باید در بالای فایل باشد
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WarZoneDatabase:
    def __init__(self):
        self.db_path = 'warzone.db'
        self.conn = None
        self.init_db()
    
    def init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.create_tables()
            logger.info("✅ دیتابیس WarZone راه‌اندازی شد")
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
    
    # بقیه کد بدون تغییر...
