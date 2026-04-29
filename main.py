from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Конфигурация БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_site.db'
db = SQLAlchemy(app)

# Модель юзера (создание таблицы) для дальнейшего использования в функциях
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    subscription = db.Column(db.Boolean, default=False)
    is_coach = db.Column(db.Boolean, default=False)

# Инициализация БД на "сервере"
with app.app_context():
    db.create_all()



# Домашняя страница для не зарегистрированных пользователей
@app.route('/')
def home_page_without_auth():
    return render_template('home_page_without_auth.html')

# Домашняя страница для зарегистрированных пользователей, получаем id пользователя через переменную пути
@app.route('/<user_id>')
def home_page(user_id):
    #id используется для подтверждения авторизованности и для ссылок
    return render_template('home_page.html')

# Страница профиля пользователя
@app.route('/profile/<user_id>')
def profile_page(user_id):
    #Должен быть запрос к бд для получения данных о пользователе
    return render_template('profile_page.html')

# Страница списка упражнений
@app.route('/exercises/<user_id>')
def exercises_page(user_id):
    #id передается только для использования в дальнейших ссылках на другие ручки
    return render_template('exercises_page.html')

@app.route('/programs/<user_id>')
def programs_page(user_id):
    #id передается для использования в дальнейших ссылках на другие ручки
    return render_template('programs_page.html')

# КБЖУ страница, в целом у нас будет просто заглушка не рабочая
@app.route('/nutritional/<user_id>')
def nutritional_page(user_id):
    #id передается для подтверждения авторизованности пользователя и использования в дальнейших ссылках на ручки
    return render_template('nutritional_page.html')

# Нейронка
@app.route('/ai/<user_id>')
def ai_page(user_id):
    return render_template('ai_page.html')



if __name__ == '__main__':
    app.run(debug=True)