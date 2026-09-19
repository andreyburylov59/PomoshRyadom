"""
Маршруты для системы оплаты
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Task, Payment, User
from datetime import datetime

# Создание Blueprint для платежей
payment = Blueprint('payment', __name__)


@payment.route('/task/<int:task_id>/pay')
@login_required
def pay_for_contact(task_id):
    """Страница оплаты за доступ к контакту"""
    
    # Получаем задание
    task = db.session.get(Task, task_id)
    if not task:
        flash('Задание не найдено', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: нельзя платить за собственное задание
    if task.user_id == current_user.id:
        flash('Это ваше собственное задание', 'warning')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Проверка: возможно, уже оплачено
    existing_payment = Payment.query.filter_by(
        task_id=task_id,
        executor_id=current_user.id,
        status='paid'
    ).first()
    
    if existing_payment:
        flash('Вы уже оплатили доступ к этому контакту', 'info')
        return redirect(url_for('tasks.task_detail', task_id=task_id))
    
    # Проверка: есть ли незавершенный платеж
    pending_payment = Payment.query.filter_by(
        task_id=task_id,
        executor_id=current_user.id,
        status='pending'
    ).first()
    
    if pending_payment:
        # Используем существующий платеж
        payment_obj = pending_payment
    else:
        # Создаем новый платеж
        payment_obj = Payment(
            task_id=task_id,
            executor_id=current_user.id,
            amount=50,  # Фиксированная цена из конфига
            status='pending'
        )
        db.session.add(payment_obj)
        db.session.commit()
    
    # Генерируем QR-код, если его еще нет
    if not payment_obj.qr_code_path:
        payment_obj.generate_qr_code()
    
    return render_template('pay.html',
                         task=task,
                         payment=payment_obj,
                         creator=task.creator)


@payment.route('/payment/<int:payment_id>/confirm', methods=['POST'])
@login_required
def confirm_payment(payment_id):
    """Подтверждение оплаты (в реальности это будет webhook от платежной системы)"""
    
    payment_obj = db.session.get(Payment, payment_id)
    
    if not payment_obj:
        flash('Платеж не найден', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: платеж принадлежит текущему пользователю
    if payment_obj.executor_id != current_user.id:
        flash('Это не ваш платеж', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: платеж еще не оплачен
    if payment_obj.status == 'paid':
        flash('Этот платеж уже оплачен', 'info')
        return redirect(url_for('tasks.task_detail', task_id=payment_obj.task_id))
    
    # Отмечаем платеж как оплаченный
    payment_obj.mark_as_paid()
    
    flash('Оплата подтверждена! Теперь вы можете видеть номер телефона заказчика.', 'success')
    return redirect(url_for('tasks.task_detail', task_id=payment_obj.task_id))


@payment.route('/payment/<int:payment_id>/simulate', methods=['POST'])
@login_required
def simulate_payment(payment_id):
    """
    Симуляция оплаты для тестирования (только для разработки!)
    В продакшене этот маршрут должен быть удален
    """
    
    payment_obj = db.session.get(Payment, payment_id)
    
    if not payment_obj:
        flash('Платеж не найден', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Проверка: платеж принадлежит текущему пользователю
    if payment_obj.executor_id != current_user.id:
        flash('Это не ваш платеж', 'danger')
        return redirect(url_for('tasks.tasks_list'))
    
    # Симулируем успешную оплату
    if payment_obj.status != 'paid':
        payment_obj.mark_as_paid()
        flash('✅ Оплата симулирована успешно! (только для разработки)', 'success')
    else:
        flash('Этот платеж уже оплачен', 'info')
    
    return redirect(url_for('tasks.task_detail', task_id=payment_obj.task_id))


@payment.route('/my-payments')
@login_required
def my_payments():
    """Список платежей пользователя"""
    
    # Платежи, которые пользователь совершил (как исполнитель)
    my_payments_list = Payment.query.filter_by(
        executor_id=current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    # Платежи, которые были совершены за задания пользователя (как заказчик)
    received_payments_list = Payment.query.join(Task).filter(
        Task.user_id == current_user.id,
        Payment.status == 'paid'
    ).order_by(Payment.created_at.desc()).all()
    
    return render_template('my_payments.html',
                         my_payments=my_payments_list,
                         received_payments=received_payments_list)
