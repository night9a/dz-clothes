import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 86400 * 7  # 7 days
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Email - Mailjet
    MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
    MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY')
    MAIL_FROM = os.getenv('MAIL_FROM', 'noreply@dzclothes.dz')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://dz-clothes00.vercel.app/')
    VERIFY_EMAIL_URL_PATH = '/verify-email'
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '814124596804-o07r8uokfces627sar5l0gk1ihacp1u5.apps.googleusercontent.com')
