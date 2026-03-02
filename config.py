import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-muito-secreta-123'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # SESSÃO / LOGIN
    # =========================
    REMEMBER_COOKIE_DURATION = timedelta(days=90)
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=90)

    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True

    REMEMBER_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SAMESITE = "Lax"

    # =========================
    # SENDGRID
    # =========================
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER")

    # =========================
    # TWILIO
    # =========================
    TWILIO_SID = os.environ.get("TWILIO_SID")
    TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
