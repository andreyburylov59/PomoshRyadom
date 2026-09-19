from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Task, User
from datetime import datetime

# Создание Blueprint для маршрутов заданий
tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks')
def tasks_list():
    """Лента заданий с фильтрами"""
    
    # Получение параметров фильтрации
    district = request.args.get('district', '')
    category = request.args.get('category', '')
    urgency = request.args.get('urgency', '')
    sort_by = request.args.get('sort_by', 'date_desc')
    
    # Базовый запрос - только активные задания
    query = Task.query.filter_by(status='active')
    
    # Применение фильтров
    if district:
        query = query.filter_by(district=district)
    
    if category:
        query = query.filter_by(category=category)
    
    if urgency:
        query = query.filter_by(urgency=urgency)
    
    # Сортировка
    if sort_by == 'date_desc':
        query = query.order_by(Task.created_at.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Task.created_at.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Task.price.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Task.price.asc())
    
    # Получение заданий
    all_tasks = query.all()
    
    # Статистика
    total_tasks = len(all_tasks)
    
    return render_template('tasks.html',
                         tasks=all_tasks,
                         total_tasks=total_tasks,
                         district=district,
                         category=category,
                         urgency=urgency,
                         sort_by=sort_by)


@tasks.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Создание нового задания"""
    
    # Проверка роли: только customer и both могут создавать задания
    if current_user.role not in ['customer', 'both']:
        flash('Только заказчики могут создавать задания', 'warning')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка лимита активных заданий (максимум 5)
    active_tasks_count = current_user.get_active_tasks_count()
    if active_tasks_count >= 5:
        flash('Вы достигли лимита активных заданий (максимум 5). Завершите или отмените существующие задания.', 'warning')
        return redirect(url_for('tasks.my_tasks'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        price = request.form.get('price', '')
        address = request.form.get('address', '').strip()
        district = request.form.get('district', '')
        urgency = request.form.get('urgency', 'планово')
        latitude = request.form.get('latitude', '')
        longitude = request.form.get('longitude', '')
        
        # Валидация данных
        errors = []
        
        if not title or len(title) < 5:
            errors.append('Название должно содержать минимум 5 символов')
        
        if not description or len(description) < 10:
            errors.append('Описание должно содержать минимум 10 символов')
        
        if not category:
            errors.append('Выберите категорию')
        
        if not price:
            errors.append('Укажите цену')
        else:
            try:
                price = int(price)
                if price <= 0:
                    errors.append('Цена должна быть больше 0')
                elif price > 1000000:
                    errors.append('Цена не может быть больше 1 000 000 ₽')
            except ValueError:
                errors.append('Цена должна быть числом')
        
        if not address or len(address) < 5:
            errors.append('Укажите адрес (минимум 5 символов)')
        
        if not district:
            errors.append('Выберите район')
        
        if urgency not in ['срочно', 'планово', 'навыки']:
            errors.append('Некорректная срочность')
        
        # Если есть ошибки, отображаем их
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('create_task.html',
                                 title=title,
                                 description=description,
                                 category=category,
                                 price=price if isinstance(price, str) else '',
                                 address=address,
                                 district=district,
                                 urgency=urgency)
        
        # Антиспам: проверка на дублирование заданий
        from datetime import timedelta
        recent_time = datetime.utcnow() - timedelta(hours=1)
        similar_task = Task.query.filter(
            Task.user_id == current_user.id,
            Task.title == title,
            Task.created_at >= recent_time
        ).first()
        
        if similar_task:
            flash('Вы уже создали похожее задание в течение последнего часа. Пожалуйста, подождите.', 'warning')
            return render_template('create_task.html',
                                 title=title,
                                 description=description,
                                 category=category,
                                 price=price if isinstance(price, str) else '',
                                 address=address,
                                 district=district,
                                 urgency=urgency)
        
        # Создание маскированного номера телефона
        phone_hidden = current_user.get_masked_phone()
        
        # Обработка координат
        lat = None
        lon = None
        if latitude and longitude:
            try:
                lat = float(latitude)
                lon = float(longitude)
            except ValueError:
                pass
        
        # Создание задания
        try:
            new_task = Task(
                user_id=current_user.id,
                title=title,
                description=description,
                category=category,
                price=price,
                address=address,
                district=district,
                urgency=urgency,
                phone_hidden=phone_hidden,
                status='active',
                latitude=lat,
                longitude=lon
            )
            
            db.session.add(new_task)
            db.session.commit()
            
            flash(f'Задание "{title}" успешно создано!', 'success')
            return redirect(url_for('tasks.task_detail', task_id=new_task.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при создании задания. Попробуйте ещё раз.', 'danger')
            return render_template('create_task.html',
                                 title=title,
                                 description=description,
                                 category=category,
                                 price=price,
                                 address=address,
                                 district=district,
                                 urgency=urgency)
    
    # GET запрос - отображаем форму
    return render_template('create_task.html')


@tasks.route('/task/<int:task_id>')
def task_detail(task_id):
    """Детали задания"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверяем, может ли текущий пользователь видеть телефон
    can_see_phone = False
    if current_user.is_authenticated:
        can_see_phone = task.is_phone_unlocked_for(current_user.id)
    
    # Получаем отображаемый телефон
    display_phone = task.phone_hidden
    if can_see_phone:
        display_phone = task.creator.phone
    
    return render_template('task_detail.html',
                         task=task,
                         can_see_phone=can_see_phone,
                         display_phone=display_phone)


@tasks.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Редактирование задания"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверка прав: только создатель может редактировать
    if task.user_id != current_user.id:
        flash('Вы не можете редактировать чужое задание', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Нельзя редактировать завершённые или отменённые задания
    if task.status in ['completed', 'cancelled']:
        flash('Нельзя редактировать завершённое или отменённое задание', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        price = request.form.get('price', '')
        address = request.form.get('address', '').strip()
        district = request.form.get('district', '')
        urgency = request.form.get('urgency', 'планово')
        
        # Валидация (аналогично созданию)
        errors = []
        
        if not title or len(title) < 5:
            errors.append('Название должно содержать минимум 5 символов')
        
        if not description or len(description) < 10:
            errors.append('Описание должно содержать минимум 10 символов')
        
        if not category:
            errors.append('Выберите категорию')
        
        if not price:
            errors.append('Укажите цену')
        else:
            try:
                price = int(price)
                if price <= 0:
                    errors.append('Цена должна быть больше 0')
                elif price > 1000000:
                    errors.append('Цена не может быть больше 1 000 000 ₽')
            except ValueError:
                errors.append('Цена должна быть числом')
        
        if not address or len(address) < 5:
            errors.append('Укажите адрес (минимум 5 символов)')
        
        if not district:
            errors.append('Выберите район')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('edit_task.html', task=task)
        
        # Обновление задания
        try:
            task.title = title
            task.description = description
            task.category = category
            task.price = price
            task.address = address
            task.district = district
            task.urgency = urgency
            
            db.session.commit()
            
            flash(f'Задание "{title}" успешно обновлено!', 'success')
            return redirect(url_for('tasks.task_detail', task_id=task.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при обновлении задания.', 'danger')
            return render_template('edit_task.html', task=task)
    
    # GET запрос - отображаем форму с текущими данными
    return render_template('edit_task.html', task=task)


@tasks.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Удаление задания"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверка прав: только создатель может удалять
    if task.user_id != current_user.id:
        flash('Вы не можете удалить чужое задание', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Сохраняем название для сообщения
    title = task.title
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash(f'Задание "{title}" успешно удалено', 'success')
        return redirect(url_for('tasks.tasks_list'))
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при удалении задания', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))


@tasks.route('/task/<int:task_id>/cancel', methods=['POST'])
@login_required
def cancel_task(task_id):
    """Отмена задания (изменение статуса)"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверка прав
    if task.user_id != current_user.id:
        flash('Вы не можете отменить чужое задание', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    if task.status != 'active':
        flash('Это задание уже не активно', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    try:
        task.status = 'cancelled'
        db.session.commit()
        flash(f'Задание "{task.title}" отменено', 'info')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при отмене задания', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))


@tasks.route('/my-tasks')
@login_required
def my_tasks():
    """Мои задания"""
    
    # Получение заданий пользователя
    if current_user.role in ['customer', 'both']:
        created_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    else:
        created_tasks = []
    
    if current_user.role in ['executor', 'both']:
        executed_tasks = Task.query.filter_by(executor_id=current_user.id).order_by(Task.created_at.desc()).all()
    else:
        executed_tasks = []
    
    return render_template('my_tasks.html',
                         created_tasks=created_tasks,
                         executed_tasks=executed_tasks)
