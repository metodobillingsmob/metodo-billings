import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-muito-secreta-123'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SENDGRID
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER")

    # TWILIO
    TWILIO_SID = os.environ.get("TWILIO_SID")
    TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")


