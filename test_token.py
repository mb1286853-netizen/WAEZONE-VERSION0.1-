import os

# توکن جدید اینجا بگذار
NEW_TOKEN = "8214368054:AAF2sOmQNAzaoC743N1opDubkjykH4YPTDE"

# تست با curl (در ترمینان Railway Shell)
print("برای تست توکن در Railway Shell این دستور رو بزن:")
print(f"curl -s https://api.telegram.org/bot{NEW_TOKEN}/getMe")
print("\nاگر جواب داد:")
print('{"ok":true,"result":{...}}')
print("\nاگر خطا داد:")
print('{"ok":false,"error_code":401,"description":"Unauthorized"}')
