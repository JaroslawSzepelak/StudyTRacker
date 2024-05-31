from flask import Flask
from flask_login import LoginManager
from models import Achievement, StudySession, db, User
from werkzeug.security import generate_password_hash 
from routes import init_routes
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inicjalizacja tras
init_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #db.session.query(User).delete()
        #db.session.query(StudySession).delete()
        #db.session.query(Achievement).delete()
        #db.session.commit()
        # Tworzenie konta administratora
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password=generate_password_hash('Admin123', method='pbkdf2:sha256'))
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)