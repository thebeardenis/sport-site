from flask import Flask, request, jsonify, session
from flask import render_template
from models import db, User
app = Flask(__name__)
# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_site.db'

# Связываем наше приложение с БД из другого файла
db.init_app(app)

# Инициализация таблиц БД на "сервере"
with app.app_context():
    db.create_all()



# Домашняя страница для не зарегистрированных пользователей
# На странице: кнопка домашней страницы, кнопка профиля, окошки (большая кнопка) - упражнения, программы, бжу(закрыто без подписки),
# ИИ(закрыто без подписки), Отслеживание прогресса(закрыто без регистрации), новости(до низа страницы и еще немного), тренера(запрос из БД)
@app.route('/')
def home_page_without_auth():
    return render_template('home_page_without_auth.html')

# Домашняя страница для зарегистрированных пользователей, все как выше, но зная о регистрации и подписке, получаем id через переменную пути
@app.route('/<user_id>')
def home_page(user_id):
    #id используется для подтверждения авторизованности и для ссылок
    user = User.query.filter_by(id = user_id).first()
    if not user:
        return render_template('home_page_without_auth.html')
    return render_template('home_page.html', user_id=user_id)

# Страница профиля пользователя
@app.route('/profile/<user_id>')
def profile_page(user_id):
    user = User.query.filter_by(id = user_id).first()
    if user.is_coach:
        return render_template('profile_trainer_page.html')
    else:
        return render_template('profile_page.html')

# Страница списка упражнений
@app.route('/exercises/<user_id>')
def exercises_page(user_id):
    #id передается только для использования в дальнейших ссылках на другие ручки
    return render_template('exercises_page.html')

# Страница программ тренировок
@app.route('/programs/<user_id>')
def programs_page(user_id):
    #id передается для использования в дальнейших ссылках на другие ручки
    return render_template('programs_page.html')

# КБЖУ страница, в целом у нас будет просто заглушка не рабочая
@app.route('/nutritional/<user_id>')
def nutritional_page(user_id):
    #id передается для подтверждения авторизованности пользователя и использования в дальнейших ссылках на ручки
    return render_template('nutritional_page.html')

# Отслеживание прогресса упражнений
@app.route('/tracker/<user_id>')
def tracker_progress_page(user_id):
    #Из бд берем информацию о прогрессе конкретного пользователя
    return render_template('tracker_progress_page.html')

# Нейронка
@app.route('/ai/<user_id>')
def ai_page(user_id):
    return render_template('ai_page.html')


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
    return render_template('home_page.html')

if __name__ == '__main__':
    app.run(debug=True)