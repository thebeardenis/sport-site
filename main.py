from flask import Flask, request, jsonify, session
from flask import render_template
from models import db, User
from flask import session, redirect, url_for, request
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_site.db'

# Связываем наше приложение с БД из другого файла
db.init_app(app)

# Инициализация таблиц БД на "сервере"
with app.app_context():
    db.create_all()
#Регистрация пользователя
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверяем, отмечен ли чекбокс (значение 'true' если отмечен, иначе None)
        is_coach = request.form.get('is_coach') == 'true'
        
        if User.query.filter_by(username=username).first():
            return "Пользователь уже существует"
        user = User(username=username, password=hash_password(password), is_coach=is_coach, subscription=False)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('home_page', user_id=user.id))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == hash_password(password):
            session['user_id'] = user.id
            return redirect(url_for('home_page', user_id=user.id))
        return "Неверные данные"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home_page_without_auth'))
# Домашняя страница для не зарегистрированных пользователей
# На странице: кнопка домашней страницы, кнопка профиля, окошки (большая кнопка) - упражнения, программы, бжу(закрыто без подписки),
# ИИ(закрыто без подписки), Отслеживание прогресса(закрыто без регистрации), новости(до низа страницы и еще немного), тренера(запрос из БД)
@app.route('/')
def home_page_without_auth():
    return render_template('home_page_without_auth.html')
    
# Домашняя страница для зарегистрированных пользователей, все как выше, но зная о регистрации и подписке, получаем id через переменную пути
@app.route('/<user_id>')
def home_page(user_id):
    if 'user_id' not in session or int(user_id) != session['user_id']:
        return redirect(url_for('login'))
#id используется для подтверждения авторизованности и для ссылок
    user = User.query.get(int(user_id))
    if not user:
        return render_template('home_page_without_auth.html')
    return render_template('home_page.html', user_id=user_id)

# Страница профиля пользователя
@app.route('/profile/<user_id>')
def profile_page(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user.is_coach:
        return render_template('profile_trainer_page.html', user_id=user_id, user=user)
    else:
        return render_template('profile_page.html', user_id=user_id, user=user)

# Страница списка упражнений
@app.route('/exercises/<user_id>')
def exercises_page(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('exercises_page.html', user_id=user_id, user=user)

# Страница программ тренировок
@app.route('/programs/<user_id>')
def programs_page(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('programs_page.html', user_id=user_id, user=user)

# КБЖУ страница, в целом у нас будет просто заглушка не рабочая
@app.route('/nutritional/<user_id>')
def nutritional_page(user_id):
    if 'user_id' not in session or int(user_id) != session['user_id']:
        return "Доступ запрещён. Пожалуйста, войдите.", 403
    user = User.query.get(user_id)
    return render_template('nutritional_page.html', user=user, user_id=user_id)

# Отслеживание прогресса упражнений
@app.route('/tracker/<user_id>')
def tracker_progress_page(user_id):
    return render_template('tracker_progress_page.html', user_id=user_id)

# Нейронка
@app.route('/ai/<user_id>')
def ai_page(user_id):
    return render_template('ai_page.html', user_id=user_id)


@app.route('/create_test_data')
def create_test_data():
    # Создаем тестовых пользователей
    users = [
        User(username='alex', is_coach=False, subscription=True),
        User(username='maria', is_coach=True, subscription=False),
        User(username='john', is_coach=False, subscription=False),
        User(username='sarah', is_coach=True, subscription=True),
        User(username='denis', is_coach=False, subscription=False),
        User(username='coach_peter', is_coach=True, subscription=False),
    ]

    for user in users:
        existing = User.query.filter_by(username=user.username).first()
        if not existing:
            db.session.add(user)

    db.session.commit()
    return redirect(url_for('home_page_without_auth'))

if __name__ == '__main__':
    app.run(debug=True)