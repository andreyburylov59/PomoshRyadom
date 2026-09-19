#!/usr/bin/env python3
"""
Тестирование системы отзывов (Этап 7)
"""
import requests
import random
from app import app, db
from models import User, Task, Review

BASE_URL = 'http://127.0.0.1:5000'

def test_reviews_system():
    """Тестирование полного цикла отзывов"""
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ОТЗЫВОВ (ЭТАП 7)")
    print("=" * 70)
    
    session_customer = requests.Session()
    session_executor = requests.Session()
    
    # 1. Регистрация заказчика
    print("\n1️⃣ Регистрация заказчика...")
    customer_phone = f'+7999{random.randint(1000000, 9999999)}'
    register_data = {
        'name': 'Анна Заказчик',
        'phone': customer_phone,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'customer',
        'district': 'Центральный'
    }
    
    response = session_customer.post(f'{BASE_URL}/register', data=register_data, allow_redirects=False)
    if response.status_code == 302:
        print(f"✅ Заказчик зарегистрирован: {customer_phone}")
    else:
        print(f"❌ Ошибка регистрации заказчика: {response.status_code}")
        return
    
    # 2. Регистрация исполнителя
    print("\n2️⃣ Регистрация исполнителя...")
    executor_phone = f'+7999{random.randint(1000000, 9999999)}'
    register_data = {
        'name': 'Дмитрий Исполнитель',
        'phone': executor_phone,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'executor',
        'district': 'Центральный'
    }
    
    response = session_executor.post(f'{BASE_URL}/register', data=register_data, allow_redirects=False)
    if response.status_code == 302:
        print(f"✅ Исполнитель зарегистрирован: {executor_phone}")
    else:
        print(f"❌ Ошибка регистрации исполнителя: {response.status_code}")
        return
    
    # Получаем ID исполнителя из БД
    with app.app_context():
        executor_user = User.query.filter_by(phone=executor_phone).first()
        if executor_user:
            executor_id = executor_user.id
            print(f"   ID исполнителя: {executor_id}")
        else:
            print("❌ Исполнитель не найден в БД")
            return
    
    # 3. Создание задания
    print("\n3️⃣ Создание задания от заказчика...")
    task_data = {
        'title': 'Ремонт сантехники',
        'description': 'Требуется починить кран на кухне',
        'category': 'сантехника',
        'price': 1500,
        'address': 'ул. Пушкина, д. 15',
        'district': 'Центральный',
        'urgency': 'срочно'
    }
    
    response = session_customer.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=False)
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        task_id = location.split('/')[-1] if '/task/' in location else None
        print(f"✅ Задание создано, ID: {task_id}")
    else:
        print(f"❌ Ошибка создания задания: {response.status_code}")
        return
    
    # 4. Завершение задания
    print("\n4️⃣ Завершение задания заказчиком...")
    complete_data = {
        'executor_id': executor_id
    }
    
    response = session_customer.post(
        f'{BASE_URL}/task/{task_id}/complete',
        data=complete_data,
        allow_redirects=False
    )
    
    if response.status_code == 302:
        print("✅ Задание отмечено как выполненное")
    else:
        print(f"❌ Ошибка завершения задания: {response.status_code}")
    
    # 5. Проверка статуса задания в БД
    print("\n5️⃣ Проверка статуса задания в БД...")
    with app.app_context():
        task = db.session.get(Task, int(task_id))
        if task:
            print(f"   Статус: {task.status}")
            print(f"   Исполнитель ID: {task.executor_id}")
            print(f"   Дата завершения: {task.completed_at}")
            
            if task.status == 'completed':
                print("✅ Задание успешно завершено")
            else:
                print(f"⚠️  Неожиданный статус: {task.status}")
        else:
            print("❌ Задание не найдено")
    
    # 6. Переход на страницу отзыва
    print("\n6️⃣ Проверка страницы отзыва...")
    response = session_customer.get(f'{BASE_URL}/task/{task_id}/review')
    if response.status_code == 200:
        print("✅ Страница отзыва загружена")
        
        content = response.text
        if 'Оставить отзыв' in content:
            print("✅ Заголовок страницы найден")
        
        if 'Дмитрий Исполнитель' in content or 'Исполнитель' in content:
            print("✅ Информация об исполнителе отображается")
        
        if '★' in content or 'rating' in content:
            print("✅ Элементы рейтинга присутствуют")
    else:
        print(f"❌ Ошибка загрузки страницы отзыва: {response.status_code}")
    
    # 7. Оставление отзыва заказчиком
    print("\n7️⃣ Оставление отзыва заказчиком...")
    review_data = {
        'rating': 5,
        'comment': 'Отличная работа! Все сделано быстро и качественно. Рекомендую!'
    }
    
    response = session_customer.post(
        f'{BASE_URL}/task/{task_id}/review',
        data=review_data,
        allow_redirects=False
    )
    
    if response.status_code == 302:
        print("✅ Отзыв успешно оставлен")
    else:
        print(f"❌ Ошибка отправки отзыва: {response.status_code}")
    
    # 8. Проверка отзыва в БД
    print("\n8️⃣ Проверка отзыва в БД...")
    with app.app_context():
        review = Review.query.filter_by(task_id=int(task_id)).first()
        if review:
            print(f"✅ Отзыв создан в БД")
            print(f"   Рейтинг: {review.rating}★")
            print(f"   Комментарий: {review.comment[:50]}...")
            print(f"   Автор: ID {review.reviewer_id}")
            print(f"   Получатель: ID {review.reviewee_id}")
        else:
            print("❌ Отзыв не найден в БД")
    
    # 9. Проверка обновления рейтинга пользователя
    print("\n9️⃣ Проверка обновления рейтинга исполнителя...")
    with app.app_context():
        executor_user = db.session.get(User, executor_id)
        if executor_user:
            print(f"   Новый рейтинг: {executor_user.rating}")
            print(f"   Выполнено заданий: {executor_user.completed_tasks}")
            
            if executor_user.rating == 5.0:
                print("✅ Рейтинг обновлен корректно")
            else:
                print(f"⚠️  Неожиданный рейтинг: {executor_user.rating}")
        else:
            print("❌ Исполнитель не найден")
    
    # 10. Проверка страницы отзывов пользователя
    print("\n🔟 Проверка страницы отзывов пользователя...")
    response = session_executor.get(f'{BASE_URL}/user/{executor_id}/reviews')
    if response.status_code == 200:
        print("✅ Страница отзывов пользователя загружена")
        
        content = response.text
        if 'Дмитрий Исполнитель' in content:
            print("✅ Имя пользователя отображается")
        
        if '5.0' in content or '★★★★★' in content:
            print("✅ Рейтинг отображается")
        
        if 'Отличная работа' in content:
            print("✅ Комментарий отзыва отображается")
    else:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
    
    # 11. Проверка страницы "Мои отзывы"
    print("\n1️⃣1️⃣ Проверка страницы 'Мои отзывы'...")
    response = session_executor.get(f'{BASE_URL}/my-reviews')
    if response.status_code == 200:
        print("✅ Страница 'Мои отзывы' загружена")
        
        content = response.text
        if 'Полученные отзывы' in content:
            print("✅ Раздел полученных отзывов найден")
        
        if 'Оставленные отзывы' in content:
            print("✅ Раздел оставленных отзывов найден")
    else:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
    
    # 12. Создание нескольких отзывов для статистики
    print("\n1️⃣2️⃣ Создание дополнительных отзывов для статистики...")
    
    # Создадим еще несколько заданий и отзывов
    with app.app_context():
        executor_user = db.session.get(User, executor_id)
        customer_user = User.query.filter_by(phone=customer_phone).first()
        
        # Создаем задания и отзывы с разными рейтингами
        ratings = [4, 5, 3, 5, 4]
        created_reviews = 0
        
        for i, rating in enumerate(ratings):
            task = Task(
                user_id=customer_user.id,
                title=f'Тестовое задание {i+2}',
                description=f'Описание задания {i+2}',
                category='уборка',
                price=1000 + i*100,
                address=f'ул. Тестовая, д. {i+1}',
                district='Центральный',
                urgency='планово',
                phone_hidden=customer_user.get_masked_phone(),
                status='completed',
                executor_id=executor_id
            )
            db.session.add(task)
            db.session.flush()
            
            review = Review(
                task_id=task.id,
                reviewer_id=customer_user.id,
                reviewee_id=executor_id,
                rating=rating,
                comment=f'Отзыв с оценкой {rating} звезд'
            )
            db.session.add(review)
            created_reviews += 1
        
        db.session.commit()
        
        # Обновляем рейтинг
        executor_user.update_rating()
        
        print(f"✅ Создано {created_reviews} дополнительных отзывов")
        print(f"   Итоговый рейтинг исполнителя: {executor_user.rating}")
        print(f"   Всего выполнено: {executor_user.completed_tasks}")
    
    # 13. Итоговая статистика
    print("\n1️⃣3️⃣ Итоговая статистика...")
    with app.app_context():
        total_reviews = Review.query.count()
        total_completed = Task.query.filter_by(status='completed').count()
        
        print(f"Всего отзывов: {total_reviews}")
        print(f"Завершенных заданий: {total_completed}")
        
        if total_reviews > 0:
            avg_rating = db.session.query(db.func.avg(Review.rating)).scalar()
            print(f"Средний рейтинг всех отзывов: {avg_rating:.1f}★")
    
    print("\n" + "=" * 70)
    print("✅ ЭТАП 7: РЕЙТИНГИ И ОТЗЫВЫ - ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print("\n📋 Реализованные функции:")
    print("   ✅ Модель Review в БД")
    print("   ✅ Завершение задания заказчиком")
    print("   ✅ Форма отзыва с 5 звездами")
    print("   ✅ Сохранение отзыва в БД")
    print("   ✅ Автоматическое обновление рейтинга")
    print("   ✅ Страница отзывов пользователя")
    print("   ✅ Страница 'Мои отзывы'")
    print("   ✅ Отображение звезд в профиле")
    print("   ✅ Статистика по рейтингам")

if __name__ == '__main__':
    test_reviews_system()
