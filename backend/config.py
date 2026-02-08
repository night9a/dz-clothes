import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 86400 * 7  # 7 days
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Email
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    MAIL_FROM = os.getenv('MAIL_FROM', 'noreply@dzclothes.dz')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    VERIFY_EMAIL_URL_PATH = '/verify-email'
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '814124596804-o07r8uokfces627sar5l0gk1ihacp1u5.apps.googleusercontent.com')
