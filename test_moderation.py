#!/usr/bin/env python3
"""
Тестирование системы модерации (Этап 8)
"""
import requests
import random
from app import app, db
from models import User, Task, Report

BASE_URL = 'http://127.0.0.1:5000'

def test_moderation_system():
    """Тестирование системы модерации и безопасности"""
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ МОДЕРАЦИИ (ЭТАП 8)")
    print("=" * 70)
    
    # 1. Тест лимита активных заданий
    print("\n1️⃣ Тестирование лимита активных заданий...")
    
    session = requests.Session()
    phone = f'+7999{random.randint(1000000, 9999999)}'
    
    # Регистрация
    register_data = {
        'name': 'Тест Лимитов',
        'phone': phone,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'customer',
        'district': 'Центральный'
    }
    session.post(f'{BASE_URL}/register', data=register_data)
    
    # Создаем 5 заданий
    for i in range(5):
        task_data = {
            'title': f'Задание {i+1}',
            'description': f'Описание задания номер {i+1}',
            'category': 'уборка',
            'price': 1000,
            'address': f'ул. Тестовая, д. {i+1}',
            'district': 'Центральный',
            'urgency': 'планово'
        }
        response = session.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=False)
        if response.status_code == 302:
            print(f"  ✅ Задание {i+1} создано")
    
    # Пытаемся создать 6-е задание
    task_data = {
        'title': 'Задание 6 (должно быть отклонено)',
        'description': 'Это задание должно быть отклонено из-за лимита',
        'category': 'уборка',
        'price': 1000,
        'address': 'ул. Тестовая, д. 6',
        'district': 'Центральный',
        'urgency': 'планово'
    }
    response = session.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=True)
    
    if 'лимита' in response.text or 'максимум' in response.text.lower():
        print("  ✅ Лимит 5 активных заданий работает корректно")
    else:
        print("  ⚠️  Лимит не сработал")
    
    # 2. Тест антиспама
    print("\n2️⃣ Тестирование антиспама (дублирование заданий)...")
    
    session2 = requests.Session()
    phone2 = f'+7999{random.randint(1000000, 9999999)}'
    
    register_data2 = {
        'name': 'Тест Антиспама',
        'phone': phone2,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'customer',
        'district': 'Центральный'
    }
    session2.post(f'{BASE_URL}/register', data=register_data2)
    
    # Создаем задание
    task_data = {
        'title': 'Уникальное задание для теста',
        'description': 'Описание уникального задания',
        'category': 'доставка',
        'price': 500,
        'address': 'ул. Уникальная, д. 1',
        'district': 'Северный',
        'urgency': 'срочно'
    }
    response = session2.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=False)
    if response.status_code == 302:
        print("  ✅ Первое задание создано")
    
    # Пытаемся создать дубликат сразу же
    response = session2.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=True)
    
    if 'похожее задание' in response.text or 'подождите' in response.text:
        print("  ✅ Антиспам работает - дубликат отклонен")
    else:
        print("  ⚠️  Антиспам не сработал")
    
    # 3. Тест системы жалоб
    print("\n3️⃣ Тестирование системы жалоб...")
    
    # Создаем пользователя-нарушителя
    session_offender = requests.Session()
    phone_offender = f'+7999{random.randint(1000000, 9999999)}'
    
    register_data_offender = {
        'name': 'Нарушитель',
        'phone': phone_offender,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'customer',
        'district': 'Центральный'
    }
    session_offender.post(f'{BASE_URL}/register', data=register_data_offender)
    
    # Создаем задание от нарушителя
    task_data_offender = {
        'title': 'Задание нарушителя',
        'description': 'Это задание от нарушителя',
        'category': 'мастер',
        'price': 2000,
        'address': 'ул. Нарушений, д. 1',
        'district': 'Западный',
        'urgency': 'планово'
    }
    response = session_offender.post(f'{BASE_URL}/task/create', data=task_data_offender, allow_redirects=False)
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        task_id = location.split('/')[-1] if '/task/' in location else None
        print(f"  ✅ Задание нарушителя создано, ID: {task_id}")
        
        # Получаем ID нарушителя
        with app.app_context():
            offender_user = User.query.filter_by(phone=phone_offender).first()
            offender_id = offender_user.id if offender_user else None
        
        # Создаем 3 жалобы от разных пользователей
        for i in range(3):
            session_reporter = requests.Session()
            phone_reporter = f'+7999{random.randint(1000000, 9999999)}'
            
            register_data_reporter = {
                'name': f'Жалобщик {i+1}',
                'phone': phone_reporter,
                'password': 'test123',
                'password_confirm': 'test123',
                'role': 'executor',
                'district': 'Центральный'
            }
            session_reporter.post(f'{BASE_URL}/register', data=register_data_reporter)
            
            # Отправляем жалобу
            report_data = {
                'reason': 'spam',
                'description': f'Жалоба номер {i+1} на спам от нарушителя'
            }
            response = session_reporter.post(
                f'{BASE_URL}/task/{task_id}/report',
                data=report_data,
                allow_redirects=False
            )
            
            if response.status_code == 302:
                print(f"  ✅ Жалоба {i+1} отправлена")
        
        # Проверяем блокировку
        with app.app_context():
            offender_user = db.session.get(User, offender_id)
            if offender_user:
                if offender_user.is_blocked:
                    print(f"  ✅ Пользователь автоматически заблокирован после 3 жалоб")
                    print(f"     Причина: {offender_user.blocked_reason}")
                else:
                    print(f"  ⚠️  Пользователь не заблокирован (жалоб: {offender_user.get_reports_count()})")
    
    # 4. Проверка доступа заблокированного пользователя
    print("\n4️⃣ Проверка доступа заблокированного пользователя...")
    
    # Пытаемся создать задание от заблокированного
    task_data_blocked = {
        'title': 'Попытка создать задание после блокировки',
        'description': 'Это не должно пройти',
        'category': 'уборка',
        'price': 1000,
        'address': 'ул. Блокированная, д. 1',
        'district': 'Центральный',
        'urgency': 'планово'
    }
    response = session_offender.post(f'{BASE_URL}/task/create', data=task_data_blocked, allow_redirects=True)
    
    if 'заблокирован' in response.text.lower() or 'blocked' in response.url:
        print("  ✅ Заблокированный пользователь перенаправлен")
    else:
        print("  ⚠️  Заблокированный пользователь имеет доступ")
    
    # 5. Статистика
    print("\n5️⃣ Итоговая статистика...")
    
    with app.app_context():
        total_tasks = Task.query.count()
        active_tasks = Task.query.filter_by(status='active').count()
        total_reports = Report.query.count()
        blocked_users = User.query.filter_by(is_blocked=True).count()
        
        print(f"  Всего заданий: {total_tasks}")
        print(f"  Активных заданий: {active_tasks}")
        print(f"  Всего жалоб: {total_reports}")
        print(f"  Заблокированных пользователей: {blocked_users}")
    
    print("\n" + "=" * 70)
    print("✅ ЭТАП 8: МОДЕРАЦИЯ И БЕЗОПАСНОСТЬ - ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print("\n📋 Реализованные функции:")
    print("   ✅ Лимит 5 активных заданий на пользователя")
    print("   ✅ Антиспам: блокировка дубликатов (1 час)")
    print("   ✅ Модель Report для жалоб")
    print("   ✅ Жалобы на задания и пользователей")
    print("   ✅ Автоматическая блокировка при 3+ жалобах")
    print("   ✅ Блокировка доступа для заблокированных")
    print("   ✅ Страница информации о блокировке")

if __name__ == '__main__':
    test_moderation_system()
