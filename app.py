from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cfam-msaken-2024-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cfam.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql+psycopg://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgresql+psycopg://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ═══════════════════════════════════════════
#  MODELS
# ═══════════════════════════════════════════

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    centre_name = db.Column(db.String(200), default='Centre de Formation et d\'Apprentissage MSAKEN')
    centre_code = db.Column(db.String(20), default='51542')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(10), default='📅')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stagiaires = db.relationship('Stagiaire', backref='promotion', lazy=True, cascade='all, delete-orphan')

class Stagiaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    cin = db.Column(db.String(30))
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    nom_ar = db.Column(db.String(100))
    prenom_ar = db.Column(db.String(100))
    genre = db.Column(db.String(10), default='Garçon')
    date_naiss = db.Column(db.String(20))
    lieu_naiss = db.Column(db.String(100))
    date_entree = db.Column(db.String(20))
    date_sortie = db.Column(db.String(20))
    specialite = db.Column(db.String(200))
    adresse = db.Column(db.String(200))
    telephone = db.Column(db.String(20))
    niveau = db.Column(db.String(100))
    groupe = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'cin': self.cin or '',
            'nom': self.nom or '',
            'prenom': self.prenom or '',
            'nom_ar': self.nom_ar or '',
            'prenom_ar': self.prenom_ar or '',
            'genre': self.genre or 'Garçon',
            'date_naiss': self.date_naiss or '',
            'lieu_naiss': self.lieu_naiss or '',
            'date_entree': self.date_entree or '',
            'date_sortie': self.date_sortie or '',
            'specialite': self.specialite or '',
            'adresse': self.adresse or '',
            'telephone': self.telephone or '',
            'niveau': self.niveau or '',
            'groupe': self.groupe or '',
        }

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ═══════════════════════════════════════════
#  ROUTES AUTH
# ═══════════════════════════════════════════

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        error = 'Identifiant ou mot de passe incorrect'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ═══════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    promotions = Promotion.query.order_by(Promotion.id.desc()).all()
    promo_key = request.args.get('promo')
    if not promo_key and promotions:
        promo_key = promotions[0].key
    current_promo = Promotion.query.filter_by(key=promo_key).first() if promo_key else None
    stagiaires = current_promo.stagiaires if current_promo else []
    # Convert to dicts for JSON serialization
    stagiaires_dicts = [s.to_dict() for s in stagiaires]
    groups = sorted(set(s.groupe for s in stagiaires if s.groupe))
    specs = sorted(set(s.specialite for s in stagiaires if s.specialite))
    return render_template('dashboard.html',
        promotions=promotions,
        current_promo=current_promo,
        stagiaires=stagiaires_dicts,
        groups=groups,
        specs=specs,
        user=current_user
    )

# ═══════════════════════════════════════════
#  API STAGIAIRES
# ═══════════════════════════════════════════

@app.route('/api/stagiaires')
@login_required
def api_stagiaires():
    promo_key = request.args.get('promo', '')
    q = request.args.get('q', '').strip().lower()
    groupe = request.args.get('groupe', '')
    spec = request.args.get('spec', '')

    promo = Promotion.query.filter_by(key=promo_key).first()
    if not promo:
        return jsonify([])

    results = promo.stagiaires
    if q:
        results = [s for s in results if
            q in (s.nom or '').lower() or
            q in (s.prenom or '').lower() or
            q in (s.cin or '').lower() or
            q in (s.nom_ar or '') or
            q in (s.prenom_ar or '')]
    if groupe:
        results = [s for s in results if s.groupe == groupe]
    if spec:
        results = [s for s in results if s.specialite == spec]

    return jsonify([s.to_dict() for s in results])

@app.route('/api/stagiaire/<int:sid>')
@login_required
def api_stagiaire(sid):
    s = db.session.get(Stagiaire, sid)
    if not s: return jsonify({'error': 'not found'}), 404
    return jsonify(s.to_dict())

@app.route('/api/stagiaire/add', methods=['POST'])
@login_required
def api_add_stagiaire():
    data = request.json
    promo = Promotion.query.filter_by(key=data.get('promotion_key')).first()
    if not promo:
        return jsonify({'error': 'Promotion introuvable'}), 404
    s = Stagiaire(
        promotion_id=promo.id,
        cin=data.get('cin',''),
        nom=data.get('nom','').upper(),
        prenom=data.get('prenom','').upper(),
        nom_ar=data.get('nom_ar',''),
        prenom_ar=data.get('prenom_ar',''),
        genre=data.get('genre','Garçon'),
        date_naiss=data.get('date_naiss',''),
        lieu_naiss=data.get('lieu_naiss',''),
        date_entree=data.get('date_entree',''),
        date_sortie=data.get('date_sortie',''),
        specialite=data.get('specialite',''),
        adresse=data.get('adresse',''),
        telephone=data.get('telephone',''),
        niveau=data.get('niveau',''),
        groupe=data.get('groupe','')
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({'success': True, 'id': s.id})

@app.route('/api/stagiaire/edit/<int:sid>', methods=['POST'])
@login_required
def api_edit_stagiaire(sid):
    s = db.session.get(Stagiaire, sid)
    if not s: return jsonify({'error': 'not found'}), 404
    data = request.json
    for field in ['cin','nom','prenom','nom_ar','prenom_ar','genre','date_naiss',
                  'lieu_naiss','date_entree','date_sortie','specialite','adresse','telephone','niveau','groupe']:
        if field in data:
            val = data[field]
            if field in ('nom','prenom'): val = val.upper()
            setattr(s, field, val)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stagiaire/delete/<int:sid>', methods=['POST'])
@login_required
def api_delete_stagiaire(sid):
    s = db.session.get(Stagiaire, sid)
    if not s: return jsonify({'error': 'not found'}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({'success': True})

# ═══════════════════════════════════════════
#  API PROMOTIONS
# ═══════════════════════════════════════════

@app.route('/api/promotions')
@login_required
def api_promotions():
    promos = Promotion.query.order_by(Promotion.id.desc()).all()
    return jsonify([{
        'id': p.id, 'key': p.key, 'label': p.label,
        'emoji': p.emoji, 'count': len(p.stagiaires)
    } for p in promos])

@app.route('/api/promotion/add', methods=['POST'])
@login_required
def api_add_promotion():
    data = request.json
    key = data.get('key','').strip().upper().replace(' ','')
    label = data.get('label','').strip().upper()
    emoji = data.get('emoji','📅')
    if not key or not label:
        return jsonify({'error': 'Champs manquants'}), 400
    if Promotion.query.filter_by(key=key).first():
        return jsonify({'error': 'Clé déjà existante'}), 400
    p = Promotion(key=key, label=label, emoji=emoji)
    db.session.add(p)
    db.session.commit()
    return jsonify({'success': True, 'key': key})

@app.route('/api/promotion/edit/<int:pid>', methods=['POST'])
@login_required
def api_edit_promotion(pid):
    p = db.session.get(Promotion, pid)
    if not p: return jsonify({'error': 'not found'}), 404
    data = request.json
    if 'label' in data: p.label = data['label'].upper()
    if 'emoji' in data: p.emoji = data['emoji']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/promotion/delete/<int:pid>', methods=['POST'])
@login_required
def api_delete_promotion(pid):
    p = db.session.get(Promotion, pid)
    if not p: return jsonify({'error': 'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True})

# ═══════════════════════════════════════════
#  INIT DB + SEED
# ═══════════════════════════════════════════

def seed_db():
    if User.query.count() == 0:
        u = User(username='51541', centre_name='Centre de Formation et d\'Apprentissage MSAKEN', centre_code='51542')
        u.set_password('r51541')
        db.session.add(u)
        db.session.commit()

    if Promotion.query.count() == 0:
        seed_file = os.path.join(os.path.dirname(__file__), 'seed_data.json')
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                seed = json.load(f)
            for promo_data in seed:
                p = Promotion(
                    key=promo_data['key'],
                    label=promo_data['label'],
                    emoji=promo_data.get('emoji','📅')
                )
                db.session.add(p)
                db.session.flush()
                for s in promo_data.get('stagiaires', []):
                    stag = Stagiaire(promotion_id=p.id, **s)
                    db.session.add(stag)
            db.session.commit()
            print(f"Seeded {Promotion.query.count()} promotions")

with app.app_context():
    db.create_all()
    seed_db()

if __name__ == '__main__':
    app.run(debug=False)
