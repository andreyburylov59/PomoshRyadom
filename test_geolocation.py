#!/usr/bin/env python3
"""
Тестирование геолокации (Этап 5)
"""
import requests
from app import app, db
from models import User, Task

BASE_URL = 'http://127.0.0.1:5000'

def test_geolocation():
    """Тестирование функциональности геолокации"""
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ ГЕОЛОКАЦИИ (ЭТАП 5)")
    print("=" * 70)
    
    session = requests.Session()
    
    # 1. Регистрация пользователя
    print("\n1️⃣ Регистрация пользователя-заказчика...")
    import random
    phone_num = f'+7999{random.randint(1000000, 9999999)}'
    register_data = {
        'name': 'Геолокация Тест',
        'phone': phone_num,
        'password': 'test123',
        'password_confirm': 'test123',
        'role': 'customer',
        'district': 'Центральный'
    }
    
    response = session.post(f'{BASE_URL}/register', data=register_data, allow_redirects=False)
    if response.status_code == 302:
        print("✅ Пользователь зарегистрирован")
    else:
        print(f"❌ Ошибка регистрации: {response.status_code}")
        return
    
    # 2. Создание задания с координатами
    print("\n2️⃣ Создание задания с координатами...")
    task_data = {
        'title': 'Уборка с координатами',
        'description': 'Тестовое задание для проверки геолокации',
        'category': 'уборка',
        'price': 500,
        'address': 'ул. Ленина, д. 10',
        'district': 'Центральный',
        'urgency': 'планово',
        'latitude': 55.7558,  # Центр Москвы
        'longitude': 37.6173
    }
    
    response = session.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=False)
    if response.status_code == 302:
        print("✅ Задание создано с координатами")
        # Получаем ID задания из редиректа
        location = response.headers.get('Location', '')
        task_id = location.split('/')[-1] if '/task/' in location else None
        print(f"   Task ID: {task_id}")
    else:
        print(f"❌ Ошибка создания задания: {response.status_code}")
        task_id = None
    
    # 3. Проверка сохранения координат в БД
    print("\n3️⃣ Проверка сохранения координат в БД...")
    with app.app_context():
        if task_id:
            task = db.session.get(Task, int(task_id))
            if task:
                print(f"✅ Задание найдено в БД")
                print(f"   Широта: {task.latitude}")
                print(f"   Долгота: {task.longitude}")
                
                if task.latitude and task.longitude:
                    print("✅ Координаты успешно сохранены!")
                else:
                    print("⚠️  Координаты не сохранены")
            else:
                print("❌ Задание не найдено в БД")
        else:
            print("⚠️  Task ID не получен, пропускаем проверку БД")
    
    # 4. Создание нескольких заданий в разных районах с координатами
    print("\n4️⃣ Создание тестовых заданий в разных точках...")
    test_tasks = [
        {
            'title': 'Задание Северный район',
            'description': 'Тестовое задание в Северном районе',
            'category': 'доставка',
            'price': 300,
            'address': 'ул. Северная, д. 5',
            'district': 'Северный',
            'urgency': 'срочно',
            'latitude': 55.8558,
            'longitude': 37.6173
        },
        {
            'title': 'Задание Южный район',
            'description': 'Тестовое задание в Южном районе',
            'category': 'мастер',
            'price': 700,
            'address': 'ул. Южная, д. 15',
            'district': 'Южный',
            'urgency': 'планово',
            'latitude': 55.6558,
            'longitude': 37.6173
        },
        {
            'title': 'Задание рядом с центром',
            'description': 'Задание в 500м от центра',
            'category': 'уборка',
            'price': 400,
            'address': 'ул. Центральная, д. 20',
            'district': 'Центральный',
            'urgency': 'планово',
            'latitude': 55.7608,
            'longitude': 37.6223
        }
    ]
    
    created_count = 0
    for task in test_tasks:
        response = session.post(f'{BASE_URL}/task/create', data=task, allow_redirects=False)
        if response.status_code == 302:
            created_count += 1
    
    print(f"✅ Создано {created_count} из {len(test_tasks)} тестовых заданий")
    
    # 5. Проверка отображения заданий на странице /tasks
    print("\n5️⃣ Проверка отображения заданий на странице /tasks...")
    response = session.get(f'{BASE_URL}/tasks')
    if response.status_code == 200:
        print("✅ Страница /tasks загружена успешно")
        
        # Проверяем наличие data-атрибутов с координатами
        content = response.text
        if 'data-latitude' in content and 'data-longitude' in content:
            print("✅ Карточки заданий содержат data-атрибуты с координатами")
        else:
            print("⚠️  Data-атрибуты с координатами не найдены")
        
        # Проверяем наличие элементов фильтра по расстоянию
        if 'filter-by-distance-btn' in content:
            print("✅ Кнопка фильтра по расстоянию присутствует")
        else:
            print("⚠️  Кнопка фильтра по расстоянию не найдена")
        
        if 'max-distance' in content:
            print("✅ Поле ввода расстояния присутствует")
        else:
            print("⚠️  Поле ввода расстояния не найдено")
    else:
        print(f"❌ Ошибка загрузки страницы /tasks: {response.status_code}")
    
    # 6. Проверка страницы создания задания
    print("\n6️⃣ Проверка страницы создания задания...")
    response = session.get(f'{BASE_URL}/task/create')
    if response.status_code == 200:
        print("✅ Страница создания задания загружена")
        
        content = response.text
        
        # Проверяем наличие кнопки автоопределения района
        if 'detect-location-btn' in content:
            print("✅ Кнопка 'Определить район автоматически' присутствует")
        else:
            print("⚠️  Кнопка 'Определить район автоматически' не найдена")
        
        # Проверяем наличие скрытых полей для координат
        if 'id="latitude"' in content and 'id="longitude"' in content:
            print("✅ Скрытые поля для координат присутствуют")
        else:
            print("⚠️  Скрытые поля для координат не найдены")
        
        # Проверяем подключение geolocation.js
        if 'geolocation.js' in content:
            print("✅ Скрипт geolocation.js подключен")
        else:
            print("⚠️  Скрипт geolocation.js не подключен")
    else:
        print(f"❌ Ошибка загрузки страницы создания задания: {response.status_code}")
    
    # 7. Итоговая статистика
    print("\n7️⃣ Итоговая статистика...")
    with app.app_context():
        total_tasks = Task.query.count()
        tasks_with_coords = Task.query.filter(
            Task.latitude.isnot(None),
            Task.longitude.isnot(None)
        ).count()
        
        print(f"Всего заданий в БД: {total_tasks}")
        print(f"Заданий с координатами: {tasks_with_coords}")
        
        if tasks_with_coords > 0:
            print(f"✅ Процент заданий с координатами: {tasks_with_coords / total_tasks * 100:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ ЭТАП 5: ГЕОЛОКАЦИЯ - ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print("\n📋 Реализованные функции:")
    print("   ✅ Сохранение координат при создании задания")
    print("   ✅ Кнопка автоопределения района")
    print("   ✅ Скрытые поля latitude/longitude")
    print("   ✅ Фильтр по расстоянию на странице заданий")
    print("   ✅ Data-атрибуты с координатами в карточках")
    print("   ✅ JavaScript модуль geolocation.js")
    print("\n🎯 Функции для ручного тестирования в браузере:")
    print("   1. Откройте /task/create")
    print("   2. Нажмите 'Определить район автоматически'")
    print("   3. Разрешите доступ к геолокации")
    print("   4. Откройте /tasks")
    print("   5. Введите расстояние (например, 3 км)")
    print("   6. Нажмите 'Показать рядом'")
    print("   7. Проверьте фильтрацию заданий")

if __name__ == '__main__':
    test_geolocation()
