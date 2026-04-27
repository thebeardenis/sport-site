from flask import Flask
from flask import render_template

app = Flask(__name__)


# Домашняя страница для не зарегистрированных пользователей
@app.route('/')
def home_page_without_auth():
    return render_template('home_page_without_auth')

# Домашняя страница для зарегистрированных пользователей, получаем id пользователя через переменную пути
@app.route('/<user_id>')
def home_page(user_id):
    #id используется для подтверждения авторизованности и для ссылок
    return render_template('home_page')

# Страница профиля пользователя
@app.route('/profile/<user_id>')
def profile_page(user_id):
    #Должен быть запрос к бд для получения данных о пользователе
    return render_template('profile_page')

# Страница списка упражнений
@app.route('/exercises/<user_id>')
def exercises_page(user_id):
    #id передается только для использования в дальнейших ссылках на другие ручки
    return render_template('exercises_page')

# КБЖУ страница, в целом у нас будет просто заглушка не рабочая
@app.route('/nutritional/<user_id>')
def nutritional_page(user_id):
    #id передается для подтверждения авторизованности пользователя и использования в дальнейших ссылках на ручки
    return render_template('nutritional_page')

# Нейронка
@app.route('/ai/<user_id>')
def ai_page(user_id):
    return render_template('ai_page')


if __name__ == '__main__':
    app.run(debug=True)