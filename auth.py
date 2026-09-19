from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import re

# Создание Blueprint для аутентификации
auth = Blueprint('auth', __name__)


def validate_phone(phone):
    """Валидация номера телефона"""
    # Удаляем все символы кроме цифр и плюса
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем формат: должно быть 11 цифр для России или +7 и 10 цифр
    if len(cleaned) == 11 and cleaned.startswith('7'):
        return '+' + cleaned
    elif len(cleaned) == 11 and cleaned.startswith('8'):
        # Заменяем 8 на +7
        return '+7' + cleaned[1:]
    elif len(cleaned) == 10:
        return '+7' + cleaned
    elif len(cleaned) == 12 and cleaned.startswith('+7'):
        return cleaned
    else:
        return None


def format_phone_display(phone):
    """Форматирование телефона для отображения: +7 (902) 123-45-67"""
    cleaned = re.sub(r'[^\d]', '', phone)
    if len(cleaned) == 11:
        return f'+{cleaned[0]} ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}'
    return phone


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    
    # Если пользователь уже авторизован, перенаправляем на главную
    if current_user.is_authenticated:
        flash('Вы уже авторизованы', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        role = request.form.get('role', 'customer')
        district = request.form.get('district', '')
        
        # Валидация данных
        errors = []
        
        if not name or len(name) < 2:
            errors.append('Имя должно содержать минимум 2 символа')
        
        if not phone:
            errors.append('Номер телефона обязателен')
        else:
            validated_phone = validate_phone(phone)
            if not validated_phone:
                errors.append('Неверный формат номера телефона. Используйте: +7 (XXX) XXX-XX-XX')
            else:
                phone = validated_phone
                # Проверка на существование пользователя с таким телефоном
                existing_user = User.query.filter_by(phone=phone).first()
                if existing_user:
                    errors.append('Пользователь с таким номером телефона уже зарегистрирован')
        
        if not password or len(password) < 6:
            errors.append('Пароль должен содержать минимум 6 символов')
        
        if password != password_confirm:
            errors.append('Пароли не совпадают')
        
        if role not in ['customer', 'executor', 'both']:
            errors.append('Некорректная роль пользователя')
        
        # Если есть ошибки, отображаем их
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', 
                                 name=name, 
                                 phone=phone, 
                                 role=role,
                                 district=district)
        
        # Создание нового пользователя
        try:
            new_user = User(
                name=name,
                phone=phone,
                role=role,
                district=district if district else None
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Автоматический вход после регистрации
            login_user(new_user)
            
            flash(f'Добро пожаловать, {name}! Регистрация прошла успешно.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при регистрации. Попробуйте ещё раз.', 'danger')
            return render_template('register.html', 
                                 name=name, 
                                 phone=phone, 
                                 role=role,
                                 district=district)
    
    # GET запрос - отображаем форму
    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя"""
    
    # Если пользователь уже авторизован, перенаправляем на главную
    if current_user.is_authenticated:
        flash('Вы уже авторизованы', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Валидация
        if not phone or not password:
            flash('Заполните все поля', 'warning')
            return render_template('login.html', phone=phone)
        
        # Валидация и нормализация телефона
        validated_phone = validate_phone(phone)
        if not validated_phone:
            flash('Неверный формат номера телефона', 'danger')
            return render_template('login.html', phone=phone)
        
        # Поиск пользователя
        user = User.query.filter_by(phone=validated_phone).first()
        
        if not user:
            flash('Пользователь с таким номером не найден', 'danger')
            return render_template('login.html', phone=phone)
        
        # Проверка пароля
        if not user.check_password(password):
            flash('Неверный пароль', 'danger')
            return render_template('login.html', phone=phone)
        
        # Вход пользователя
        login_user(user, remember=remember)
        flash(f'Добро пожаловать, {user.name}!', 'success')
        
        # Перенаправление на страницу, с которой пришёл пользователь
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        return redirect(url_for('index'))
    
    # GET запрос - отображаем форму
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    """Выход пользователя"""
    name = current_user.name
    logout_user()
    flash(f'До свидания, {name}! Вы успешно вышли из системы.', 'info')
    return redirect(url_for('index'))


@auth.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    return render_template('profile.html', user=current_user)
