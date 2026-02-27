import os

class Config:
    # Chave secreta para proteger as sessões do usuário
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-muito-secreta-123'
    
    # Caminho do banco de dados SQLite (arquivo local)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de E-mail para Redefinição de Senha (Exemplo Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'metodobillings.mob@gmail.com'
    MAIL_PASSWORD = 'oxfugbpvsygydmhm' # Não é a senha comum, é a senha de app do Google

    # Configurações Twilio (WhatsApp)
    TWILIO_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    TWILIO_TOKEN = 'your_twilio_auth_token'

