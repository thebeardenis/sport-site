from flask import Flask
from flask import render_template

app = Flask(__name__)


# Домашняя страница для не зарегистрированных пользователей
@app.route('/')
def home_page_without_auth():
    return render_template('home_page_without_auth')

# Домашняя страница для зарегистрированных пользователей, получаем id пользователя через переменную пути
@app.route('/<user_id>')
def home_page():
    #Должен быть запрос к бд для получения данных о пользователе
    return render_template('home_page')

if __name__ == '__main__':
    app.run(debug=True)