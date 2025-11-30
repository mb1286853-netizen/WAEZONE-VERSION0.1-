import random
from config import CHANCE_CONFIG

def calculate_attack_damage(base_damage, attacker_level, has_critical=False):
    """محاسبه دمیج حمله"""
    level_bonus = attacker_level * 2
    total_damage = base_damage + level_bonus
    
    if has_critical:
        total_damage *= 2
    
    return max(1, total_damage)

def calculate_xp_reward(damage, is_victory=True):
    """محاسبه XP جایزه"""
    base_xp = max(5, damage // 10)
    if is_victory:
        base_xp *= 2
    
    return base_xp

def calculate_miner_income(miner_level, hours_passed):
    """محاسبه درآمد ماینر"""
    base_income = miner_level * 100
    return base_income * hours_passed

def check_critical_hit():
    """بررسی حمله بحرانی"""
    return random.random() < CHANCE_CONFIG['critical_attack']

def check_block_success(defense_level):
    """بررسی موفقیت بلاک"""
    base_chance = CHANCE_CONFIG['block_missile']
    level_bonus = defense_level * 0.05
    return random.random() < (base_chance + level_bonus)
