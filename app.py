from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from models import db, User, Note
import json
import config

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- SUAS ROTAS DE LOGIN EXISTENTES ---
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            # 🔥 Recuperação automática de admin
            admin_existente = User.query.filter_by(is_admin=True).first()

            if not admin_existente:
                user.is_admin = True
                db.session.commit()

            return redirect(url_for('dashboard'))

        flash('E-mail ou senha inválidos.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.')
            return redirect(url_for('register'))

        user = User(
            name=name,
            email=email,
            whatsapp=whatsapp
        )
        user.set_password(password)

        # 🔥 Primeiro usuário vira admin
        admin_existente = User.query.filter_by(is_admin=True).first()
        if not admin_existente:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROTA DO DASHBOARD (Onde fica seu HTML MOB) ---
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html') # Renomeie seu index.html para dashboard.html

# --- API PARA O JAVASCRIPT ---

@app.route('/api/anotacoes', methods=['GET'])
@login_required
def get_anotacoes():
    # Busca apenas as notas do usuário logado
    notas = Note.query.filter_by(user_id=current_user.id).order_by(Note.date).all()
    return jsonify([n.to_dict() for n in notas])

@app.route('/api/anotacoes', methods=['POST'])
@login_required
def save_note():
    data = request.json
    
    # Se estiver editando uma nota existente
    nota_id = data.get('id')
    if nota_id:
        nota = Note.query.filter_by(id=nota_id, user_id=current_user.id).first()
    else:
        # Verifica se já existe nota para este dia/ciclo para evitar duplicidade
        nota = Note.query.filter_by(user_id=current_user.id, cicloId=data['cicloId'], diaCiclo=data['diaCiclo']).first()

    if not nota:
        nota = Note(user_id=current_user.id)

    nota.cicloId = data['cicloId']
    nota.diaCiclo = data['diaCiclo']
    nota.tipoCiclo = data.get('tipoCiclo')
    nota.date = data['data']
    nota.feeling = data['sinto']
    nota.appearance = data['vejo']
    nota.regra = data.get('regra')
    nota.temp = data['temp'] if data['temp'] else None
    nota.relacao = data['relacao']
    nota.obs = data['obs']
    nota.selo_json = json.dumps(data['selo'])

    db.session.add(nota)
    db.session.commit()
    return jsonify({"status": "success", "id": nota.id})

@app.route('/api/anotacoes/limpar', methods=['DELETE'])
@login_required
def limpar_tudo():
    Note.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/anotacoes/<int:id>', methods=['DELETE'])
@login_required
def deletar_nota(id):
    nota = Note.query.filter_by(id=id, user_id=current_user.id).first()
    if nota:
        db.session.delete(nota)
        db.session.commit()
    return jsonify({"status": "success"})

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_user.name = request.form['name']
    current_user.whatsapp = request.form['whatsapp']

    db.session.commit()

    flash('Perfil atualizado com sucesso!')
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if not current_user.check_password(old_password):
        flash('Senha atual incorreta.')
        return redirect(url_for('profile'))

    current_user.set_password(new_password)
    db.session.commit()

    flash('Senha alterada com sucesso!')
    return redirect(url_for('profile'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                msg = Message(
                    subject="Teste envio",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email]
                )
                msg.body = "Teste de envio"
                mail.send(msg)
                print("EMAIL ENVIADO COM SUCESSO")
            except Exception as e:
                print("ERRO AO ENVIAR EMAIL:", e)

        return redirect(url_for('login'))

    return render_template('forgot.html')
    
@app.route('/restore', methods=['POST'])
@login_required
def restore():
    file = request.files['file']
    data = json.load(file)

    for item in data.get('anotacoes', []):
        note = Note(
            user_id=current_user.id,
            cicloId=item.get('cicloId'),
            diaCiclo=item.get('diaCiclo'),
            tipoCiclo=item.get('tipoCiclo'),
            date=item.get('data'),
            feeling=item.get('sinto'),
            appearance=item.get('vejo'),
            regra=item.get('regra'),
            temp=item.get('temp'),
            relacao=item.get('relacao'),
            obs=item.get('obs'),
            selo_json=json.dumps(item.get('selo'))
        )

        db.session.add(note)

    db.session.commit()

    return "Restauração concluída com sucesso"

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return "Acesso negado", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users)

from flask import Response
import json

@app.route('/admin/export/<int:user_id>')
@login_required
@admin_required
def export_user(user_id):
    user = User.query.get_or_404(user_id)
    notes = Note.query.filter_by(user_id=user.id).all()

    data = {
        "usuario": {
            "id": user.id,
            "nome": user.name,
            "email": user.email,
            "whatsapp": user.whatsapp
        },
        "anotacoes": [n.to_dict() for n in notes]
    }

    response = Response(
        json.dumps(data, indent=2),
        mimetype="application/json"
    )
    response.headers["Content-Disposition"] = f"attachment; filename=backup_user_{user.id}.json"

    return response

@app.route('/admin/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    # 🔥 Impedir exclusão do último admin
    total_admins = User.query.filter_by(is_admin=True).count()

    if user.is_admin and total_admins == 1:
        return "Não é possível excluir o último administrador.", 400

    Note.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin_panel'))

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        whatsapp = request.form.get('whatsapp')

        # Validação simples
        if not name or not email:
            return "Nome e Email são obrigatórios", 400

        # Verifica se o email já pertence a outro usuário
        email_existente = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if email_existente:
            return "Este e-mail já está em uso por outro usuário", 400

        # Atualiza dados
        user.name = name
        user.email = email
        user.whatsapp = whatsapp

        db.session.commit()

        return redirect(url_for('admin_panel'))

    return render_template('admin_edit.html', user=user)

@app.route('/admin/promover/<int:user_id>')
@login_required
@admin_required
def promover(user_id):
    user = User.query.get_or_404(user_id)

    if user.is_admin:
        return redirect(url_for('admin_panel'))

    user.is_admin = True
    db.session.commit()

    return redirect(url_for('admin_panel'))

@app.route('/admin/remover-admin/<int:user_id>')
@login_required
@admin_required
def remover_admin(user_id):

    user = User.query.get_or_404(user_id)

    # 🔥 Impedir remover o último admin
    total_admins = User.query.filter_by(is_admin=True).count()

    if total_admins <= 1:
        return "Não é possível remover o último administrador.", 400

    # 🔥 Impedir admin remover ele mesmo se for único
    if user.id == current_user.id and total_admins == 1:
        return "Você não pode remover seu próprio acesso de administrador.", 400

    user.is_admin = False
    db.session.commit()

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)