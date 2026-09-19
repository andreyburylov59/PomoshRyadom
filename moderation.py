"""
Маршруты для системы модерации и безопасности
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Task, User, Report
from datetime import datetime

# Создание Blueprint для модерации
moderation = Blueprint('moderation', __name__)


@moderation.route('/task/<int:task_id>/report', methods=['GET', 'POST'])
@login_required
def report_task(task_id):
    """Пожаловаться на задание"""
    
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задание не найдено', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Нельзя пожаловаться на собственное задание
    if task.user_id == current_user.id:
        flash('Вы не можете пожаловаться на собственное задание', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    if request.method == 'POST':
        reason = request.form.get('reason', '')
        description = request.form.get('description', '').strip()
        
        # Валидация
        errors = []
        
        valid_reasons = ['spam', 'fraud', 'inappropriate', 'other']
        if not reason or reason not in valid_reasons:
            errors.append('Выберите причину жалобы')
        
        if not description or len(description) < 10:
            errors.append('Опишите причину жалобы (минимум 10 символов)')
        
        if len(description) > 500:
            errors.append('Описание слишком длинное (максимум 500 символов)')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('report_task.html',
                                 task=task,
                                 reason=reason,
                                 description=description)
        
        # Проверяем, не жаловался ли уже пользователь на это задание
        existing_report = Report.query.filter_by(
            reporter_id=current_user.id,
            reported_task_id=task_id
        ).first()
        
        if existing_report:
            flash('Вы уже пожаловались на это задание', 'warning')
            return redirect(url_for('tasks.task_detail', task_id=task_id))
        
        # Создаем жалобу
        report = Report(
            reporter_id=current_user.id,
            reported_task_id=task_id,
            reported_user_id=task.user_id,
            reason=reason,
            description=description,
            status='pending'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Проверяем количество жалоб на пользователя
        reports_count = task.creator.get_reports_count()
        
        # Автоматическая блокировка при 3+ жалобах
        if reports_count >= 3 and not task.creator.is_blocked:
            task.creator.block_user(f'Автоматическая блокировка: {reports_count} жалоб')
            flash(f'Пользователь {task.creator.name} заблокирован из-за множественных жалоб', 'info')
        
        flash('Жалоба отправлена. Спасибо за помощь в поддержании безопасности сервиса!', 'success')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    return render_template('report_task.html', task=task)


@moderation.route('/user/<int:user_id>/report', methods=['GET', 'POST'])
@login_required
def report_user(user_id):
    """Пожаловаться на пользователя"""
    
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))
    
    # Нельзя пожаловаться на себя
    if user.id == current_user.id:
        flash('Вы не можете пожаловаться на себя', 'warning')
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST':
        reason = request.form.get('reason', '')
        description = request.form.get('description', '').strip()
        
        # Валидация
        errors = []
        
        valid_reasons = ['spam', 'fraud', 'inappropriate', 'other']
        if not reason or reason not in valid_reasons:
            errors.append('Выберите причину жалобы')
        
        if not description or len(description) < 10:
            errors.append('Опишите причину жалобы (минимум 10 символов)')
        
        if len(description) > 500:
            errors.append('Описание слишком длинное (максимум 500 символов)')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('report_user.html',
                                 user=user,
                                 reason=reason,
                                 description=description)
        
        # Проверяем, не жаловался ли уже пользователь
        existing_report = Report.query.filter_by(
            reporter_id=current_user.id,
            reported_user_id=user_id,
            reported_task_id=None
        ).first()
        
        if existing_report:
            flash('Вы уже пожаловались на этого пользователя', 'warning')
            return redirect(url_for('reviews.user_reviews', user_id=user_id))
        
        # Создаем жалобу
        report = Report(
            reporter_id=current_user.id,
            reported_user_id=user_id,
            reason=reason,
            description=description,
            status='pending'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Проверяем количество жалоб
        reports_count = user.get_reports_count()
        
        # Автоматическая блокировка при 3+ жалобах
        if reports_count >= 3 and not user.is_blocked:
            user.block_user(f'Автоматическая блокировка: {reports_count} жалоб')
            flash(f'Пользователь {user.name} заблокирован из-за множественных жалоб', 'info')
        
        flash('Жалоба отправлена. Спасибо за помощь в поддержании безопасности сервиса!', 'success')
        return redirect(url_for('reviews.user_reviews', user_id=user_id))
    
    return render_template('report_user.html', user=user)


@moderation.route('/my-reports')
@login_required
def my_reports():
    """Мои жалобы"""
    
    # Жалобы, которые подал пользователь
    reports_made = Report.query.filter_by(
        reporter_id=current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    # Жалобы на пользователя
    reports_received = Report.query.filter_by(
        reported_user_id=current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    return render_template('my_reports.html',
                         reports_made=reports_made,
                         reports_received=reports_received)


@moderation.before_app_request
def check_if_blocked():
    """Проверка блокировки пользователя перед каждым запросом"""
    if current_user.is_authenticated and current_user.is_blocked:
        # Разрешаем доступ только к страницам выхода и информации о блокировке
        allowed_endpoints = ['moderation.blocked_info', 'auth.logout', 'static']
        if request.endpoint and request.endpoint not in allowed_endpoints:
            return redirect(url_for('moderation.blocked_info'))


@moderation.route('/blocked')
@login_required
def blocked_info():
    """Информация о блокировке"""
    if not current_user.is_blocked:
        return redirect(url_for('index'))
    
    return render_template('blocked_info.html')
