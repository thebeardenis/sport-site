from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime

db = SQLAlchemy()

# Перечисление типов упражнений (для нашего примера хватит четырех)
class ExerciseType(Enum):
    BENCH_PRESS = "Жим лёжа"
    SQUATS = "Присед"
    PULL_UPS = "Подтягивания"
    PLANK = "Планка"

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

# Модель юзера (создание таблицы) для дальнейшего использования в функциях
from datetime import datetime
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    subscription = db.Column(db.Boolean, default=False)
    is_coach = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(100), nullable=False, default='')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress_records = db.relationship('Progress', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}: coach-{self.is_coach}, subscription-{self.subscription}>'
# Таблица с прогрессом упражнений
class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)

    # Тип упражнения
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)

    # Количество подходов, повторений, вес, дата
    sets_count = db.Column(db.Integer, nullable=False)
    reps_count = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    exercise_date = db.Column(db.DateTime, nullable=False, default=datetime.now())

    # Внешний ключ на пользователя
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Progress {self.exercise_type.value}: {self.weight}[kg]x{self.reps_count}[reps]x{self.sets_count}[sets] on {self.exercise_date.date()}>'