import sqlite3
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
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                zp INTEGER DEFAULT 1000,
                gem INTEGER DEFAULT 0,
                power INTEGER DEFAULT 100,
                defense_level INTEGER DEFAULT 1,
                cyber_level INTEGER DEFAULT 1,
                miner_level INTEGER DEFAULT 1,
                miner_balance INTEGER DEFAULT 0,
                last_miner_claim INTEGER DEFAULT 0,
                last_bronze_box INTEGER DEFAULT 0,
                total_attacks INTEGER DEFAULT 0,
                total_damage INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # موشک‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missiles (
                user_id INTEGER,
                missile_type TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, missile_type),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جنگنده‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fighters (
                user_id INTEGER,
                fighter_type TEXT,
                equipped BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (user_id, fighter_type),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # پهپادها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drones (
                user_id INTEGER,
                drone_type TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, drone_type),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # حملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attacker_id INTEGER,
                defender_id INTEGER,
                damage INTEGER,
                reward INTEGER,
                attack_type TEXT,
                is_critical BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (attacker_id) REFERENCES users (user_id),
                FOREIGN KEY (defender_id) REFERENCES users (user_id)
            )
        ''')
        
        # لاگ فعالیت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def get_connection(self):
        if self.conn is None:
            self.init_db()
        return self.conn

    # متدهای کاربر
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            logger.info(f"✅ کاربر جدید ایجاد شد: {user_id}")
            return self.get_user(user_id)
        return user

    def update_user_zp(self, user_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET zp = zp + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

    def update_user_xp(self, user_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET xp = xp + ? WHERE user_id = ?', (amount, user_id))
        
        user = self.get_user(user_id)
        xp_needed = user[2] * 100
        if user[3] >= xp_needed:
            cursor.execute('UPDATE users SET level = level + 1, xp = xp - ? WHERE user_id = ?', 
                          (xp_needed, user_id))
            conn.commit()
            logger.info(f"🎉 کاربر {user_id} به سطح {user[2] + 1} ارتقا یافت")
            return True
        conn.commit()
        return False

    def add_missile(self, user_id, missile_type, quantity=1):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT quantity FROM missiles WHERE user_id = ? AND missile_type = ?', 
                      (user_id, missile_type))
        result = cursor.fetchone()
        
        if result:
            cursor.execute('UPDATE missiles SET quantity = quantity + ? WHERE user_id = ? AND missile_type = ?', 
                          (quantity, user_id, missile_type))
        else:
            cursor.execute('INSERT INTO missiles (user_id, missile_type, quantity) VALUES (?, ?, ?)', 
                          (user_id, missile_type, quantity))
        conn.commit()

    def get_user_missiles(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT missile_type, quantity FROM missiles WHERE user_id = ? AND quantity > 0', (user_id,))
        return cursor.fetchall()

    def add_fighter(self, user_id, fighter_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO fighters (user_id, fighter_type) VALUES (?, ?)', 
                      (user_id, fighter_type))
        conn.commit()

    def get_user_fighters(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT fighter_type FROM fighters WHERE user_id = ?', (user_id,))
        return [row[0] for row in cursor.fetchall()]

    # متدهای آمار
    def get_total_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

    def get_total_attacks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM attacks')
        return cursor.fetchone()[0]

    def log_activity(self, user_id, activity_type, details=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO activity_log (user_id, activity_type, details) VALUES (?, ?, ?)',
            (user_id, activity_type, details)
        )
        conn.commit()

    def get_user_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(damage) FROM attacks WHERE attacker_id = ?', (user_id,))
        result = cursor.fetchone()
        return {
            'total_attacks': result[0] or 0,
            'total_damage': result[1] or 0
        }

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("✅ اتصال دیتابیس بسته شد")
