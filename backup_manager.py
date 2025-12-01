# backup_manager.py - سیستم مدیریت بکاپ
import os
import shutil
import sqlite3
import time
from datetime import datetime
import threading
import json


class BackupManager:
    def __init__(self, db_path='warzone.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.setup_backup_dir()
        
    def setup_backup_dir(self):
        """ایجاد پوشه بکاپ"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 پوشه بکاپ ایجاد شد: {self.backup_dir}")
    
    def create_backup(self, backup_type='manual'):
        """ایجاد بکاپ از دیتابیس"""
        if not os.path.exists(self.db_path):
            print("❌ فایل دیتابیس پیدا نشد!")
            return None
        
        # نام فایل بکاپ
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"warzone_backup_{backup_type}_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # کپی کردن فایل دیتابیس
            shutil.copy2(self.db_path, backup_path)
            
            # ایجاد فایل اطلاعات بکاپ
            backup_info = {
                'backup_name': backup_filename,
                'backup_path': backup_path,
                'backup_type': backup_type,
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'size_mb': os.path.getsize(backup_path) / (1024 * 1024)
            }
            
            # ذخیره اطلاعات بکاپ
            info_path = backup_path + '.info.json'
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            print(f"✅ بکاپ ایجاد شد: {backup_filename} ({backup_info['size_mb']:.2f} MB)")
            return backup_info
            
        except Exception as e:
            print(f"❌ خطا در ایجاد بکاپ: {e}")
            return None
    
    def create_json_backup(self):
        """ایجاد بکاپ JSON از اطلاعات کاربران (خوانا برای انسان)"""
        if not os.path.exists(self.db_path):
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"users_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # دریافت تمام کاربران
            cursor.execute("SELECT * FROM users")
            users = [dict(row) for row in cursor.fetchall()]
            
            # دریافت تیکت‌ها
            cursor.execute("SELECT * FROM support_tickets")
            tickets = [dict(row) for row in cursor.fetchall()]
            
            # ایجاد ساختار بکاپ
            backup_data = {
                'metadata': {
                    'backup_type': 'json_export',
                    'timestamp': timestamp,
                    'created_at': datetime.now().isoformat(),
                    'total_users': len(users),
                    'total_tickets': len(tickets)
                },
                'users': users,
                'tickets': tickets
            }
            
            # ذخیره به صورت JSON
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            conn.close()
            
            print(f"✅ بکاپ JSON ایجاد شد: {backup_filename}")
            return backup_path
            
        except Exception as e:
            print(f"❌ خطا در ایجاد بکاپ JSON: {e}")
            return None
    
    def list_backups(self):
        """لیست تمام بکاپ‌ها"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                info_path = filepath + '.info.json'
                
                backup_info = {
                    'filename': filename,
                    'path': filepath,
                    'size_mb': os.path.getsize(filepath) / (1024 * 1024),
                    'created_at': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # خواندن اطلاعات اضافی
                if os.path.exists(info_path):
                    try:
                        with open(info_path, 'r', encoding='utf-8') as f:
                            extra_info = json.load(f)
                            backup_info.update(extra_info)
                    except:
                        pass
                
                backups.append(backup_info)
        
        # مرتب‌سازی بر اساس تاریخ
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def restore_backup(self, backup_filename):
        """بازیابی از بکاپ"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"❌ فایل بکاپ پیدا نشد: {backup_filename}")
            return False
        
        try:
            # بکاپ از فایل فعلی قبل از بازیابی
            self.create_backup('pre_restore')
            
            # جایگزینی فایل دیتابیس
            shutil.copy2(backup_path, self.db_path)
            
            print(f"✅ بازیابی موفق: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ خطا در بازیابی: {e}")
            return False
    
    def cleanup_old_backups(self, keep_last=10):
        """پاک‌سازی بکاپ‌های قدیمی"""
        backups = self.list_backups()
        
        if len(backups) <= keep_last:
            print(f"📊 تعداد بکاپ‌ها: {len(backups)} (نیاز به پاک‌سازی نیست)")
            return
        
        # نگه‌داشتن آخرین بکاپ‌ها
        to_keep = backups[:keep_last]
        to_delete = backups[keep_last:]
        
        for backup in to_delete:
            try:
                # حذف فایل دیتابیس
                os.remove(backup['path'])
                
                # حذف فایل اطلاعات
                info_path = backup['path'] + '.info.json'
                if os.path.exists(info_path):
                    os.remove(info_path)
                
                print(f"🗑️ بکاپ قدیمی حذف شد: {backup['filename']}")
                
            except Exception as e:
                print(f"⚠️ خطا در حذف {backup['filename']}: {e}")
        
        print(f"✅ پاک‌سازی انجام شد. {len(to_delete)} فایل حذف شد.")


# سیستم بکاپ خودکار
class AutoBackup:
    def __init__(self, backup_manager, interval_hours=24):
        self.backup_manager = backup_manager
        self.interval_seconds = interval_hours * 3600
        self.running = False
        self.thread = None
    
    def start(self):
        """شروع بکاپ خودکار"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.thread.start()
        print(f"🔄 سیستم بکاپ خودکار شروع شد (هر {self.interval_seconds//3600} ساعت)")
    
    def stop(self):
        """توقف بکاپ خودکار"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️ سیستم بکاپ خودکار متوقف شد")
    
    def _backup_loop(self):
        """حلقه بکاپ خودکار"""
        while self.running:
            time.sleep(self.interval_seconds)
            
            try:
                print("🔄 در حال ایجاد بکاپ خودکار...")
                self.backup_manager.create_backup('auto')
                self.backup_manager.cleanup_old_backups(keep_last=20)
            except Exception as e:
                print(f"❌ خطا در بکاپ خودکار: {e}")


# ایجاد نمونه جهانی
backup_mgr = BackupManager(db_path='warzone.db', backup_dir='/data/backups')
auto_backup = AutoBackup(backup_mgr, interval_hours=24)
