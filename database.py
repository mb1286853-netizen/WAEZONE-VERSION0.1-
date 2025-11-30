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
 # اضافه کردن این متدها به کلاس WarZoneDatabase:

def add_sabotage_team(self, user_id, team_type):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO sabotage_teams (user_id, team_type, level) VALUES (?, ?, 1)', 
                  (user_id, team_type))
    conn.commit()

def get_sabotage_teams(self, user_id):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT team_type, level FROM sabotage_teams WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def upgrade_sabotage_team(self, user_id, team_type):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE sabotage_teams SET level = level + 1 WHERE user_id = ? AND team_type = ?', 
                  (user_id, team_type))
    conn.commit()           logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
    
    # بقیه کد بدون تغییر...
