"""
Маршруты для системы отзывов и рейтингов
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Task, User, Review
from datetime import datetime

# Создание Blueprint для отзывов
reviews = Blueprint('reviews', __name__)


@reviews.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Отметить задание как выполненное"""
    
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задание не найдено', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: только заказчик может завершить задание
    if task.user_id != current_user.id:
        flash('Только заказчик может завершить задание', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Проверка: задание должно быть активным
    if task.status != 'active':
        flash('Задание уже завершено или отменено', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Получаем ID исполнителя из формы
    executor_id = request.form.get('executor_id')
    if not executor_id:
        flash('Не указан исполнитель', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    try:
        executor_id = int(executor_id)
    except ValueError:
        flash('Некорректный ID исполнителя', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Проверка существования исполнителя
    executor = db.session.get(User, executor_id)
    if not executor:
        flash('Исполнитель не найден', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Завершаем задание
    task.mark_as_completed(executor_id)
    
    flash('Задание отмечено как выполненное! Теперь вы можете оставить отзыв об исполнителе.', 'success')
    return redirect(url_for('reviews.leave_review', task_id=task_id))


@reviews.route('/task/<int:task_id>/review', methods=['GET', 'POST'])
@login_required
def leave_review(task_id):
    """Оставить отзыв о выполненном задании"""
    
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задание не найдено', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: можно ли оставить отзыв
    if not task.can_review(current_user.id):
        flash('Вы не можете оставить отзыв для этого задания', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Получаем ID пользователя, которого нужно оценить
    reviewee_id = task.get_reviewee_id(current_user.id)
    if not reviewee_id:
        flash('Ошибка определения получателя отзыва', 'danger')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    reviewee = db.session.get(User, reviewee_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        # Валидация
        errors = []
        
        if not rating:
            errors.append('Выберите оценку (от 1 до 5 звезд)')
        else:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    errors.append('Оценка должна быть от 1 до 5')
            except ValueError:
                errors.append('Некорректная оценка')
        
        if comment and len(comment) > 1000:
            errors.append('Комментарий слишком длинный (максимум 1000 символов)')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('leave_review.html',
                                 task=task,
                                 reviewee=reviewee,
                                 rating=rating if isinstance(rating, int) else None,
                                 comment=comment)
        
        # Создаем отзыв
        review = Review(
            task_id=task_id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment if comment else None
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Обновляем рейтинг получателя отзыва
        reviewee.update_rating()
        
        flash(f'Спасибо за отзыв! Вы оценили {reviewee.name} на {rating} звезд.', 'success')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    return render_template('leave_review.html',
                         task=task,
                         reviewee=reviewee)


@reviews.route('/user/<int:user_id>/reviews')
def user_reviews(user_id):
    """Страница со всеми отзывами о пользователе"""
    
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))
    
    # Получаем все отзывы о пользователе
    user_reviews_list = Review.query.filter_by(
        reviewee_id=user_id
    ).order_by(Review.created_at.desc()).all()
    
    # Статистика по звездам
    rating_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in user_reviews_list:
        rating_stats[review.rating] += 1
    
    return render_template('user_reviews.html',
                         user=user,
                         reviews=user_reviews_list,
                         rating_stats=rating_stats,
                         total_reviews=len(user_reviews_list))


@reviews.route('/my-reviews')
@login_required
def my_reviews():
    """Страница с отзывами пользователя (полученные и оставленные)"""
    
    # Отзывы, полученные пользователем
    received_reviews = Review.query.filter_by(
        reviewee_id=current_user.id
    ).order_by(Review.created_at.desc()).all()
    
    # Отзывы, оставленные пользователем
    given_reviews = Review.query.filter_by(
        reviewer_id=current_user.id
    ).order_by(Review.created_at.desc()).all()
    
    return render_template('my_reviews.html',
                         received_reviews=received_reviews,
                         given_reviews=given_reviews)
