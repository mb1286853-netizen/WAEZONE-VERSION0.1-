# database.py - دیتابیس WarZone
import time
from config import SHOP_ITEMS, ADMINS

class WarZoneDB:
    def __init__(self):
        self.users = {}
        self.support_tickets = {}
        self.ticket_counter = 1
        # کاربر ادمین پیش‌فرض
        self.setup_admin()
        print("🗄️ دیتابیس WarZone راه‌اندازی شد")
    
    def setup_admin(self):
        """ایجاد کاربر ادمین پیش‌فرض"""
        for admin_id in ADMINS:
            if admin_id not in self.users:
                self.users[admin_id] = {
                    'user_id': admin_id,
                    'level': 100,
                    'xp': 0,
                    'zp': 999999,
                    'gem': 9999,
                    'power': 1000,
                    'defense_level': 10,
                    'cyber_level': 10,
                    'miner_level': 15,
                    'miner_balance': 0,
                    'miner_last_collect': 0,
                    'total_attacks': 0,
                    'total_damage': 0,
                    'last_bronze_box': 0,
                    'fighters': list(SHOP_ITEMS["جنگنده‌ها"].keys()),
                    'missiles': {missile: 999 for missile in SHOP_ITEMS["موشک‌ها"].keys()},
                    'drones': list(SHOP_ITEMS["پهپادها"].keys()),
                    'sabotage_teams': [],
                    'attack_combos': [{}, {}, {}],
                    'league': 'افسانه‌ای',
                    'league_reward_claimed': False,
                    'last_league_reward': 0,
                    'created_at': time.time(),
                    'is_admin': True
                }
    
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'level': 1,
                'xp': 0,
                'zp': 1000,
                'gem': 0,
                'power': 100,
                'defense_level': 1,
                'cyber_level': 1,
                'miner_level': 1,
                'miner_balance': 0,
                'miner_last_collect': 0,
                'total_attacks': 0,
                'total_damage': 0,
                'last_bronze_box': 0,
                'fighters': [],
                'missiles': {missile: 0 for missile in SHOP_ITEMS["موشک‌ها"].keys()},
                'drones': [],
                'sabotage_teams': [],
                'attack_combos': [{}, {}, {}],
                'league': 'برنز',
                'league_reward_claimed': False,
                'last_league_reward': 0,
                'created_at': time.time(),
                'is_admin': user_id in ADMINS
            }
        return self.users[user_id]
    
    def is_admin(self, user_id):
        user = self.get_user(user_id)
        return user.get('is_admin', False) or user_id in ADMINS
    
    def update_user_zp(self, user_id, amount):
        user = self.get_user(user_id)
        user['zp'] += amount
        return user['zp']
    
    def update_user_xp(self, user_id, amount):
        user = self.get_user(user_id)
        user['xp'] += amount
        xp_needed = user['level'] * 100
        if user['xp'] >= xp_needed:
            user['level'] += 1
            user['xp'] -= xp_needed
            user['power'] += 20
            return True, user['level']
        return False, user['level']
    
    def add_missile(self, user_id, missile_type, count=1):
        user = self.get_user(user_id)
        if missile_type in user['missiles']:
            user['missiles'][missile_type] += count
        else:
            user['missiles'][missile_type] = count
        return user['missiles'][missile_type]
    
    def add_fighter(self, user_id, fighter_type):
        user = self.get_user(user_id)
        if fighter_type not in user['fighters']:
            user['fighters'].append(fighter_type)
            return True
        return False
    
    def add_drone(self, user_id, drone_type):
        user = self.get_user(user_id)
        if drone_type not in user['drones']:
            user['drones'].append(drone_type)
            return True
        return False
    
    def can_afford(self, user_id, price, currency="zp"):
        user = self.get_user(user_id)
        return user.get(currency, 0) >= price
    
    def purchase_item(self, user_id, price, currency="zp"):
        user = self.get_user(user_id)
        if user[currency] >= price:
            user[currency] -= price
            return True
        return False
    
    def can_open_bronze_box(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        user = self.get_user(user_id)
        user['last_bronze_box'] = time.time()
    
    # سیستم پشتیبانی
    def create_ticket(self, user_id, message):
        ticket_id = self.ticket_counter
        self.ticket_counter += 1
        self.support_tickets[ticket_id] = {
            'user_id': user_id,
            'message': message,
            'status': 'open',
            'admin_response': '',
            'created_at': time.time(),
            'updated_at': time.time()
        }
        return ticket_id
    
    def get_user_tickets(self, user_id):
        user_tickets = []
        for ticket_id, ticket in self.support_tickets.items():
            if ticket['user_id'] == user_id:
                user_tickets.append((ticket_id, ticket))
        return user_tickets
    
    def get_all_tickets(self):
        return self.support_tickets
    
    # توابع ادمین
    def add_zp_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        user['zp'] += amount
        return user['zp']
    
    def add_gem_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        user['gem'] += amount
        return user['gem']
    
    def add_level_to_user(self, user_id, amount):
        user = self.get_user(user_id)
        user['level'] += amount
        user['power'] += amount * 20
        return user['level']
    
    def find_user_by_id(self, user_id):
        return self.get_user(user_id)
    
    def get_all_stats(self):
        total_users = len(self.users)
        total_attacks = sum(user['total_attacks'] for user in self.users.values())
        total_damage = sum(user['total_damage'] for user in self.users.values())
        total_tickets = len(self.support_tickets)
        open_tickets = len([t for t in self.support_tickets.values() if t['status'] == 'open'])
        
        return {
            'total_users': total_users,
            'total_attacks': total_attacks,
            'total_damage': total_damage,
            'total_tickets': total_tickets,
            'open_tickets': open_tickets
        }

# ایجاد نمونه دیتابیس
db = WarZoneDB()
