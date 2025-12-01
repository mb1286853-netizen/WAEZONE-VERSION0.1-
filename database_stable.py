# database_stable.py - دیتابیس پایدار برای WarZone
import sqlite3
import json
import time
import os
from config import SHOP_ITEMS, ADMINS


class WarZoneDB:
    def __init__(self):
        # ایجاد دیتابیس در مسیر پایدار
        db_path = self.get_db_path()
        print(f"📁 مسیر دیتابیس: {db_path}")
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.ticket_counter = self.get_last_ticket_id() + 1
        self.setup_admin()
        print("✅ دیتابیس پایدار راه‌اندازی شد")
    
    def get_db_path(self):
        """تعیین مسیر ذخیره‌سازی فایل دیتابیس"""
        # اولویت با volume در Railway
        volume_path = '/data/warzone.db'
        if os.path.exists('/data'):
            print("📁 استفاده از volume Railway")
            return volume_path
        # اگر نه، در پوشه جاری
        return 'warzone.db'
    
    def get_last_ticket_id(self):
        """دریافت آخرین شماره تیکت از دیتابیس"""
        try:
            cursor = self.conn.execute("SELECT MAX(id) as max_id FROM support_tickets")
            row = cursor.fetchone()
            return row['max_id'] if row and row['max_id'] else 0
        except:
            return 0
    
    def create_tables(self):
        with self.conn:
            # 1. جدول کاربران
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    zp INTEGER DEFAULT 1000,
                    gem INTEGER DEFAULT 0,
                    power INTEGER DEFAULT 100,
                    defense_level INTEGER DEFAULT 1,
                    cyber_level INTEGER DEFAULT 1,
                    miner_level INTEGER DEFAULT 1,
                    miner_balance INTEGER DEFAULT 0,
                    miner_last_collect INTEGER DEFAULT 0,
                    total_attacks INTEGER DEFAULT 0,
                    total_damage INTEGER DEFAULT 0,
                    last_bronze_box INTEGER DEFAULT 0,
                    fighters TEXT DEFAULT '[]',
                    missiles TEXT DEFAULT '{}',
                    drones TEXT DEFAULT '[]',
                    sabotage_teams TEXT DEFAULT '[]',
                    attack_combos TEXT DEFAULT '[{}, {}, {}]',
                    league TEXT DEFAULT 'برنز',
                    league_reward_claimed BOOLEAN DEFAULT FALSE,
                    last_league_reward INTEGER DEFAULT 0,
                    created_at INTEGER,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            
            # 2. جدول تیکت‌ها
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    admin_response TEXT DEFAULT '',
                    created_at INTEGER,
                    updated_at INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # 3. جدول لاگ فعالیت‌ها
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp INTEGER
                )
            """)
    
    def setup_admin(self):
        """ایجاد/بروزرسانی کاربران ادمین"""
        for admin_id in ADMINS:
            cursor = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (admin_id,))
            if cursor.fetchone() is None:
                # ادمین جدید
                fighters_json = json.dumps(list(SHOP_ITEMS["جنگنده‌ها"].keys()))
                missiles_json = json.dumps({missile: 9999 for missile in SHOP_ITEMS["موشک‌ها"].keys()})
                drones_json = json.dumps(list(SHOP_ITEMS["پهپادها"].keys()))
                sabotage_teams_json = json.dumps([10])  # لول 10
                
                self.conn.execute("""
                    INSERT INTO users (
                        user_id, level, xp, zp, gem, power, defense_level, cyber_level,
                        miner_level, total_attacks, total_damage,
                        fighters, missiles, drones, sabotage_teams,
                        league, created_at, is_admin
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    admin_id, 100, 0, 999999999, 999999999, 10000, 
                    10, 10, 20, 9999, 9999999,
                    fighters_json, missiles_json, drones_json, sabotage_teams_json,
                    "افسانه‌ای", int(time.time()), True
                ))
            else:
                # آپدیت ادمین موجود
                self.conn.execute("""
                    UPDATE users SET 
                        level = 100,
                        zp = 999999999,
                        gem = 999999999,
                        power = 10000,
                        defense_level = 10,
                        cyber_level = 10,
                        miner_level = 20,
                        is_admin = TRUE
                    WHERE user_id = ?
                """, (admin_id,))
        
        self.conn.commit()
    
    def get_user(self, user_id):
        """دریافت یا ایجاد کاربر"""
        cursor = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row is None:
            # ایجاد کاربر جدید
            self.conn.execute("""
                INSERT INTO users (user_id, created_at, is_admin) 
                VALUES (?, ?, ?)
            """, (user_id, int(time.time()), user_id in ADMINS))
            self.conn.commit()
            return self.get_user(user_id)
        
        # تبدیل داده‌ها از JSON
        return {
            'user_id': row['user_id'],
            'level': row['level'],
            'xp': row['xp'],
            'zp': row['zp'],
            'gem': row['gem'],
            'power': row['power'],
            'defense_level': row['defense_level'],
            'cyber_level': row['cyber_level'],
            'miner_level': row['miner_level'],
            'miner_balance': row['miner_balance'],
            'miner_last_collect': row['miner_last_collect'],
            'total_attacks': row['total_attacks'],
            'total_damage': row['total_damage'],
            'last_bronze_box': row['last_bronze_box'],
            'fighters': json.loads(row['fighters']),
            'missiles': json.loads(row['missiles']),
            'drones': json.loads(row['drones']),
            'sabotage_teams': json.loads(row['sabotage_teams']),
            'attack_combos': json.loads(row['attack_combos']),
            'league': row['league'],
            'league_reward_claimed': bool(row['league_reward_claimed']),
            'last_league_reward': row['last_league_reward'],
            'created_at': row['created_at'],
            'is_admin': bool(row['is_admin'])
        }
    
    def update_user(self, user_id, updates):
        """آپدیت اطلاعات کاربر"""
        if not updates:
            return
        
        set_clause = []
        values = []
        
        for key, value in updates.items():
            # تبدیل لیست‌ها و دیکشنری‌ها به JSON
            if key in ['fighters', 'drones', 'sabotage_teams', 'attack_combos']:
                value = json.dumps(value)
            elif key in ['missiles']:
                value = json.dumps(value)
            
            set_clause.append(f"{key} = ?")
            values.append(value)
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clause)} WHERE user_id = ?"
        
        self.conn.execute(query, tuple(values))
        self.conn.commit()
    
    def is_admin(self, user_id):
        user = self.get_user(user_id)
        return user['is_admin']
    
    def update_user_zp(self, user_id, amount):
        user = self.get_user(user_id)
        new_zp = user['zp'] + amount
        
        self.conn.execute(
            "UPDATE users SET zp = ? WHERE user_id = ?",
            (new_zp, user_id)
        )
        self.conn.commit()
        return new_zp
    
    def update_user_xp(self, user_id, amount):
        user = self.get_user(user_id)
        new_xp = user['xp'] + amount
        new_level = user['level']
        
        xp_needed = user['level'] * 100
        leveled_up = False
        
        if new_xp >= xp_needed:
            new_level += 1
            new_xp -= xp_needed
            new_power = user['power'] + 20
            leveled_up = True
            
            self.conn.execute(
                "UPDATE users SET level = ?, xp = ?, power = ? WHERE user_id = ?",
                (new_level, new_xp, new_power, user_id)
            )
        else:
            self.conn.execute(
                "UPDATE users SET xp = ? WHERE user_id = ?",
                (new_xp, user_id)
            )
        
        self.conn.commit()
        return leveled_up, new_level
    
    def add_missile(self, user_id, missile_type, count=1):
        user = self.get_user(user_id)
        missiles = user['missiles']
        missiles[missile_type] = missiles.get(missile_type, 0) + count
        
        self.conn.execute(
            "UPDATE users SET missiles = ? WHERE user_id = ?",
            (json.dumps(missiles), user_id)
        )
        self.conn.commit()
        return missiles[missile_type]
    
    def add_fighter(self, user_id, fighter_type):
        user = self.get_user(user_id)
        fighters = user['fighters']
        
        if fighter_type not in fighters:
            fighters.append(fighter_type)
            self.conn.execute(
                "UPDATE users SET fighters = ? WHERE user_id = ?",
                (json.dumps(fighters), user_id)
            )
            self.conn.commit()
            return True
        return False
    
    def add_drone(self, user_id, drone_type):
        user = self.get_user(user_id)
        drones = user['drones']
        
        if drone_type not in drones:
            drones.append(drone_type)
            self.conn.execute(
                "UPDATE users SET drones = ? WHERE user_id = ?",
                (json.dumps(drones), user_id)
            )
            self.conn.commit()
            return True
        return False
    
    def add_sabotage_team(self, user_id, team_level=1):
        user = self.get_user(user_id)
        teams = user['sabotage_teams']
        teams.append(team_level)
        
        self.conn.execute(
            "UPDATE users SET sabotage_teams = ? WHERE user_id = ?",
            (json.dumps(teams), user_id)
        )
        self.conn.commit()
        return len(teams)
    
    def upgrade_sabotage_team(self, user_id, team_index):
        user = self.get_user(user_id)
        teams = user['sabotage_teams']
        
        if 0 <= team_index < len(teams):
            current_level = teams[team_index]
            if current_level < 10:
                teams[team_index] += 1
                self.conn.execute(
                    "UPDATE users SET sabotage_teams = ? WHERE user_id = ?",
                    (json.dumps(teams), user_id)
                )
                self.conn.commit()
                return True, teams[team_index]
        
        return False, current_level
    
    def upgrade_cyber_tower(self, user_id):
        user = self.get_user(user_id)
        
        if user['cyber_level'] < 10:
            new_level = user['cyber_level'] + 1
            self.conn.execute(
                "UPDATE users SET cyber_level = ? WHERE user_id = ?",
                (new_level, user_id)
            )
            self.conn.commit()
            return True, new_level
        
        return False, user['cyber_level']
    
    def can_afford(self, user_id, price, currency="zp"):
        user = self.get_user(user_id)
        return user.get(currency, 0) >= price
    
    def purchase_item(self, user_id, price, currency="zp"):
        user = self.get_user(user_id)
        
        if user.get(currency, 0) >= price:
            new_balance = user[currency] - price
            self.conn.execute(
                f"UPDATE users SET {currency} = ? WHERE user_id = ?",
                (new_balance, user_id)
            )
            self.conn.commit()
            return True
        return False
    
    def can_open_bronze_box(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        current_time = int(time.time())
        self.conn.execute(
            "UPDATE users SET last_bronze_box = ? WHERE user_id = ?",
            (current_time, user_id)
        )
        self.conn.commit()
    
    # سیستم پشتیبانی
    def create_ticket(self, user_id, message):
        current_time = int(time.time())
        
        self.conn.execute("""
            INSERT INTO support_tickets (user_id, message, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, message, current_time, current_time))
        self.conn.commit()
        
        cursor = self.conn.execute("SELECT last_insert_rowid() as id")
        ticket_id = cursor.fetchone()['id']
        
        return ticket_id
    
    def get_user_tickets(self, user_id):
        cursor = self.conn.execute("""
            SELECT id, user_id, message, status, admin_response, created_at, updated_at 
            FROM support_tickets 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        tickets = []
        for row in cursor.fetchall():
            tickets.append((row['id'], dict(row)))
        
        return tickets
    
    def get_all_tickets(self):
        cursor = self.conn.execute("""
            SELECT id, user_id, message, status, admin_response, created_at, updated_at 
            FROM support_tickets 
            ORDER BY created_at DESC
        """)
        
        tickets = {}
        for row in cursor.fetchall():
            tickets[row['id']] = dict(row)
        
        return tickets
    
    # توابع ادمین
    def add_zp_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        new_zp = user['zp'] + amount
        
        self.conn.execute(
            "UPDATE users SET zp = ? WHERE user_id = ?",
            (new_zp, user_id)
        )
        self.conn.commit()
        return new_zp
    
    def add_gem_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        new_gem = user['gem'] + amount
        
        self.conn.execute(
            "UPDATE users SET gem = ? WHERE user_id = ?",
            (new_gem, user_id)
        )
        self.conn.commit()
        return new_gem
    
    def add_level_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        new_level = user['level'] + amount
        new_power = user['power'] + (amount * 20)
        
        self.conn.execute(
            "UPDATE users SET level = ?, power = ? WHERE user_id = ?",
            (new_level, new_power, user_id)
        )
        self.conn.commit()
        return new_level
    
    def find_user_by_id(self, user_id):
        return self.get_user(user_id)
    
    def get_all_stats(self):
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(total_attacks) as total_attacks,
                SUM(total_damage) as total_damage
            FROM users
        """)
        row = cursor.fetchone()
        
        cursor2 = self.conn.execute("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_tickets
            FROM support_tickets
        """)
        row2 = cursor2.fetchone()
        
        return {
            'total_users': row['total_users'] or 0,
            'total_attacks': row['total_attacks'] or 0,
            'total_damage': row['total_damage'] or 0,
            'total_tickets': row2['total_tickets'] or 0,
            'open_tickets': row2['open_tickets'] or 0
        }


# ایجاد نمونه دیتابیس
db = WarZoneDB()
