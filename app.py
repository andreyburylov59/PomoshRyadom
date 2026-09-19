import os
import sys
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Task, Payment, Review, Report

# Консоль Windows (cp1251) не печатает emoji из логов запуска
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Создание экземпляра Flask-приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'warning'

# Создание папки для загрузок, если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Регистрация Blueprint для аутентификации
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# Регистрация Blueprint для заданий
from routes import tasks as tasks_blueprint
app.register_blueprint(tasks_blueprint)

# Регистрация Blueprint для платежей
from payment import payment as payment_blueprint
app.register_blueprint(payment_blueprint)

# Регистрация Blueprint для отзывов
from reviews import reviews as reviews_blueprint
app.register_blueprint(reviews_blueprint)

# Регистрация Blueprint для модерации
from moderation import moderation as moderation_blueprint
app.register_blueprint(moderation_blueprint)


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя для Flask-Login"""
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Главная страница приложения"""
    return render_template('index.html')


@app.context_processor
def inject_user():
    """Добавление current_user в контекст всех шаблонов"""
    return dict(current_user=current_user)


@app.errorhandler(404)
def not_found_error(error):
    """Обработчик ошибки 404"""
    flash('Страница не найдена', 'warning')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    db.session.rollback()
    flash('Произошла внутренняя ошибка сервера', 'danger')
    return redirect(url_for('index'))


def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        print('✅ База данных успешно инициализирована!')


if __name__ == '__main__':
    # Создание таблиц при первом запуске
    init_db()
    
    # Запуск приложения
    print('🚀 Запуск приложения "Помощь Рядом"...')
    print('📍 Адрес: http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
