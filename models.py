from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    whatsapp = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    notes = db.relationship('Note', backref='user', lazy=True)

    # 🔐 Gera hash da senha
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # 🔎 Verifica senha
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    cicloId = db.Column(db.Integer)
    diaCiclo = db.Column(db.Integer)
    tipoCiclo = db.Column(db.String(50))
    date = db.Column(db.String(20))  # Corresponde ao f-data

    feeling = db.Column(db.String(100))
    appearance = db.Column(db.String(100))
    regra = db.Column(db.String(10))
    temp = db.Column(db.Float)
    relacao = db.Column(db.Boolean)
    obs = db.Column(db.Text)
    selo_json = db.Column(db.Text)  # Guarda o objeto do selo (cor, ícone, texto)

    def to_dict(self):
        return {
            "id": self.id,
            "cicloId": self.cicloId,
            "diaCiclo": self.diaCiclo,
            "tipoCiclo": self.tipoCiclo,
            "data": self.date,
            "sinto": self.feeling,
            "vejo": self.appearance,
            "regra": self.regra,
            "temp": self.temp,
            "relacao": self.relacao,
            "obs": self.obs,
            "selo": json.loads(self.selo_json) if self.selo_json else None
        }