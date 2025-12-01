# database.py - دیتابیس پیشرفته WarZone
import json
import time
import os
from datetime import datetime
from config import SHOP_ITEMS, ADMINS, DEFENSE_SYSTEM, BOXES

class AdvancedWarZoneDB:
    def __init__(self):
        self.data_file = "warzone_data.json"
        self.backup_folder = "backups/"
        self.users = {}
        self.support_tickets = {}
        self.ticket_counter = 1
        self.load_data()
        self.setup_admin()
        print("🗄️ دیتابیس پیشرفته WarZone راه‌اندازی شد")
    
    def load_data(self):
        """بارگذاری اطلاعات از فایل"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.support_tickets = data.get('support_tickets', {})
                    self.ticket_counter = data.get('ticket_counter', 1)
                print(f"✅ اطلاعات {len(self.users)} کاربر بارگذاری شد")
        except Exception as e:
            print(f"❌ خطا در بارگذاری: {e}")
            self.users = {}
            self.support_tickets = {}
    
    def save_data(self):
        """ذخیره اطلاعات در فایل"""
        try:
            data = {
                'users': self.users,
                'support_tickets': self.support_tickets,
                'ticket_counter': self.ticket_counter,
                'last_backup': time.time()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ اطلاعات ذخیره شد")
        except Exception as e:
            print(f"❌ خطا در ذخیره: {e}")
    
    def create_backup(self):
        """ایجاد بکاپ"""
        try:
            if not os.path.exists(self.backup_folder):
                os.makedirs(self.backup_folder)
            
            backup_file = f"{self.backup_folder}backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                'users': self.users,
                'support_tickets': self.support_tickets,
                'ticket_counter': self.ticket_counter,
                'backup_time': time.time()
            }
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ بکاپ ایجاد شد: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ خطا در بکاپ: {e}")
            return False
    
    def setup_admin(self):
        """ایجاد ادمین با امکانات کامل"""
        for admin_id in ADMINS:
            if str(admin_id) not in self.users:
                self.users[str(admin_id)] = {
                    'user_id': admin_id,
                    'username': f'admin_{admin_id}',
                    'level': 100,
                    'xp': 0,
                    'xp_needed': 0,
                    'zp': 999999999,
                    'gem': 9999999,
                    'power': 10000,
                    'health': 5000,
                    'defense_level': 20,
                    'cyber_level': 20,
                    'miner_level': 20,
                    'miner_balance': 1000000,
                    'miner_last_collect': 0,
                    'miner_income': 1000,
                    'total_attacks': 9999,
                    'total_damage': 9999999,
                    'defense_wins': 500,
                    'last_bronze_box': 0,
                    'last_silver_box': 0,
                    'last_gold_box': 0,
                    'last_diamond_box': 0,
                    'fighters': {fighter: 99 for fighter in SHOP_ITEMS["جنگنده‌ها"].keys()},
                    'missiles': {missile: 999 for missile in SHOP_ITEMS["موشک‌ها"].keys()},
                    'drones': {drone: 99 for drone in SHOP_ITEMS["پهپادها"].keys()},
                    'defenses': list(DEFENSE_SYSTEM.keys()),
                    'active_defense': 'پدافند افسانه‌ای',
                    'sabotage_level': 10,
                    'sabotage_teams': 10,
                    'sabotage_success_rate': 0.9,
                    'attack_combos': {
                        'combo1': {'name': 'رعدآسا', 'damage': 500},
                        'combo2': {'name': 'توفان', 'damage': 800},
                        'combo3': {'name': 'آپوکالیپس', 'damage': 1500}
                    },
                    'league': 'افسانه‌ای',
                    'league_points': 9999,
                    'league_reward_claimed': False,
                    'last_league_reward': 0,
                    'created_at': time.time(),
                    'last_login': time.time(),
                    'is_admin': True,
                    'is_premium': True,
                    'inventory_size': 500,
                    'max_combo_slots': 10,
                    'daily_reward_streak': 365,
                    'last_daily_reward': time.time(),
                    'security_level': 10,
                    'cyber_defense': True,
                    'auto_collect': True,
                    'notifications': True,
                    'language': 'fa'
                }
        self.save_data()
    
    def get_user(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            # کاربر جدید
            self.users[user_id_str] = {
                'user_id': user_id,
                'username': '',
                'level': 1,
                'xp': 0,
                'xp_needed': 100,
                'zp': 1000,
                'gem': 10,
                'power': 100,
                'health': 500,
                'defense_level': 1,
                'cyber_level': 1,
                'miner_level': 1,
                'miner_balance': 0,
                'miner_last_collect': 0,
                'miner_income': 10,
                'total_attacks': 0,
                'total_damage': 0,
                'defense_wins': 0,
                'last_bronze_box': 0,
                'last_silver_box': 0,
                'last_gold_box': 0,
                'last_diamond_box': 0,
                'fighters': {},
                'missiles': {missile: 0 for missile in SHOP_ITEMS["موشک‌ها"].keys()},
                'drones': {},
                'defenses': ['سپر-۹۵'],
                'active_defense': 'سپر-۹۵',
                'sabotage_level': 0,
                'sabotage_teams': 0,
                'sabotage_success_rate': 0.1,
                'attack_combos': {},
                'league': 'برنز',
                'league_points': 0,
                'league_reward_claimed': False,
                'last_league_reward': 0,
                'created_at': time.time(),
                'last_login': time.time(),
                'is_admin': user_id in ADMINS,
                'is_premium': False,
                'inventory_size': 50,
                'max_combo_slots': 3,
                'daily_reward_streak': 0,
                'last_daily_reward': 0,
                'security_level': 1,
                'cyber_defense': False,
                'auto_collect': False,
                'notifications': True,
                'language': 'fa'
            }
            self.save_data()
        
        # آپدیت زمان آخرین لاگین
        self.users[user_id_str]['last_login'] = time.time()
        return self.users[user_id_str]
    
    def is_admin(self, user_id):
        user = self.get_user(user_id)
        return user.get('is_admin', False) or user_id in ADMINS
    
    def update_user(self, user_id, updates):
        user_id_str = str(user_id)
        if user_id_str in self.users:
            self.users[user_id_str].update(updates)
            self.save_data()
            return True
        return False
    
    def collect_miner(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        
        if current_time - user['miner_last_collect'] >= 3600:
            income = user['miner_income'] * user['miner_level']
            user['miner_balance'] += income
            user['miner_last_collect'] = current_time
            self.save_data()
            return income
        return 0
    
    def upgrade_miner(self, user_id):
        user = self.get_user(user_id)
        cost = 1000 * user['miner_level']
        
        if user['zp'] >= cost:
            user['zp'] -= cost
            user['miner_level'] += 1
            user['miner_income'] += 10
            self.save_data()
            return True, user['miner_level']
        return False, user['miner_level']
    
    def get_miner_info(self, user_id):
        user = self.get_user(user_id)
        next_collect = max(0, 3600 - (time.time() - user['miner_last_collect']))
        hours = int(next_collect // 3600)
        minutes = int((next_collect % 3600) // 60)
        
        return {
            'level': user['miner_level'],
            'balance': user['miner_balance'],
            'income': user['miner_income'],
            'next_collect': f"{hours:02d}:{minutes:02d}",
            'next_upgrade_cost': 1000 * user['miner_level']
        }

# ایجاد نمونه دیتابیس
db = AdvancedWarZoneDB()
