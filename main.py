from flask import Flask, request, jsonify, session
from flask import render_template
from models import db, User, Progress, ExerciseType
from flask import session, redirect, url_for, request
import hashlib
import random

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

@app.route('/tracker/<user_id>', methods=['GET', 'POST'])
def tracker_progress_page(user_id):
    user = User.query.get(user_id)

    if request.method == 'POST':
        exercise_type = request.form['exercise_type']
        sets_count = int(request.form['sets_count'])
        reps_count = int(request.form['reps_count'])
        weight = float(request.form['weight'])

        progress = Progress(
            exercise_type=ExerciseType[exercise_type],
            sets_count=sets_count,
            reps_count=reps_count,
            weight=weight,
            user_id=user.id
        )

        db.session.add(progress)
        db.session.commit()

        return redirect(url_for('tracker_progress_page', user_id=user_id))

    progress_records = Progress.query.filter_by(user_id=user.id).order_by(Progress.exercise_date).all()

    chart_labels = [record.exercise_date.strftime('%d.%m') for record in progress_records]
    chart_weights = [record.weight for record in progress_records]
    user = User.query.filter_by(id=user_id).first()
    return render_template(
        'tracker_progress_page.html',
        user_id=user_id,
        user=user,
        progress_records=progress_records,
        exercise_types=ExerciseType,
        chart_labels=chart_labels,
        chart_weights=chart_weights
    )


@app.route('/tracker_progress/delete/<int:record_id>/<int:user_id>', methods=['POST'])
def delete_progress_record(record_id, user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    record = Progress.query.filter_by(id=record_id, user_id=user_id).first()

    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect(url_for('tracker_progress_page', user_id=user_id))



@app.route('/ai/<user_id>')
def ai_page(user_id):
    # Проверка авторизации (опционально, но рекомендуется)
    if 'user_id' not in session or int(user_id) != session['user_id']:
        return redirect(url_for('login'))
    user = User.query.filter_by(id=user_id).first()
    return render_template('ai_page.html', user_id=user_id, user=user)

# Нейронка
@app.route('/ai/ask', methods=['POST'])
def ai_ask():
    data = request.get_json()
    question = data.get('question', '').lower()
    
    # Простая логика ответов (можно расширить или подключить реальное API)
    if 'жим' in question:
        answer = "Для улучшения жима лёжа: работай над техникой (своди лопатки), добавь вспомогательные упражнения (отжимания на брусьях, жим гантелей) и следи за прогрессией весов."
    elif 'присед' in question or 'приседания' in question:
        answer = "Ключевые моменты в приседе: держи спину прямой, не заваливай колени внутрь, опускайся до параллели. Регулярно делай румынскую тягу и гиперэкстензию."
    elif 'подтягивание' in question:
        answer = "Чтобы подтягиваться больше: используй негативные повторения, подтягивания с резинкой, укрепляй хват. Делай 3-4 подхода по 80% от максимума."
    elif 'планка' in question:
        answer = "Увеличивай время в планке постепенно, добавляй боковую планку, подъёмы ног. Держи пресс и ягодицы напряжёнными."
    elif 'еда' in question or 'питание' in question or 'бжу' in question:
        answer = "Сбалансированное питание: белок (1.8-2.2 г/кг веса), жиры (0.8-1 г/кг), углеводы — остальное. Не забывай про овощи и воду."
    elif 'похудеть' in question or 'жиросжигание' in question:
        answer = "Дефицит калорий + силовые тренировки + кардио 2-3 раза в неделю. Снижай калории постепенно, сохраняй белок высоким."
    elif 'набрать массу' in question:
        answer = "Набор массы: профицит 200-300 ккал, упор на базовые упражнения (жим, присед, тяга), 2-3 г белка на кг веса, сон 8 часов."
    else:
        answers = [
            "Регулярность важнее интенсивности. Лучше тренироваться 3 раза в неделю стабильно, чем разово на износ.",
            "Не забывай про разминку и заминку – это снижает риск травм.",
            "Пей воду до, во время и после тренировки. Обезвоживание снижает силу.",
            "Прогрессируй не за счёт веса, а за счёт качества повторений. Иногда снижай рабочий вес и делай больше повторений."
        ]
        answer = random.choice(answers)
    
    return {"answer": answer}

if __name__ == '__main__':
    app.run(debug=True)