#!/usr/bin/env python3
"""
Тестирование CRUD заданий для ЭТАПА 3
"""

import requests
from models import db, User, Task
from app import app

def test_database_tasks():
    """Тест 1: Проверка заданий в базе данных"""
    print("\n🧪 Тест 1: Проверка заданий в БД")
    with app.app_context():
        tasks = Task.query.all()
        print(f"   Найдено заданий: {len(tasks)}")
        for task in tasks[:3]:
            print(f"   - {task.title} ({task.price}₽) - {task.district}")
        print("   ✅ Тест пройден")
        return True


def test_tasks_list_page():
    """Тест 2: Доступность страницы списка заданий"""
    print("\n🧪 Тест 2: Страница списка заданий")
    response = requests.get('http://127.0.0.1:5000/tasks')
    if response.status_code == 200 and 'Все задания' in response.text:
        print("   ✅ Страница доступна")
        print(f"   ✅ Найдено заданий на странице")
        return True
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        return False


def test_task_detail_page():
    """Тест 3: Доступность страницы детали задания"""
    print("\n🧪 Тест 3: Страница детали задания")
    with app.app_context():
        task = Task.query.first()
        if task:
            response = requests.get(f'http://127.0.0.1:5000/task/{task.id}')
            if response.status_code == 200 and task.title in response.text:
                print(f"   ✅ Страница задания #{task.id} доступна")
                return True
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                return False
        else:
            print("   ⚠️ Нет заданий в БД")
            return False


def test_filters():
    """Тест 4: Фильтрация заданий"""
    print("\n🧪 Тест 4: Фильтрация заданий")
    
    # Тест фильтра по району
    response = requests.get('http://127.0.0.1:5000/tasks?district=Южный')
    if response.status_code == 200:
        print("   ✅ Фильтр по району работает")
    else:
        print("   ❌ Фильтр по району не работает")
        return False
    
    # Тест фильтра по категории
    response = requests.get('http://127.0.0.1:5000/tasks?category=уборка')
    if response.status_code == 200:
        print("   ✅ Фильтр по категории работает")
    else:
        print("   ❌ Фильтр по категории не работает")
        return False
    
    # Тест сортировки
    response = requests.get('http://127.0.0.1:5000/tasks?sort_by=price_asc')
    if response.status_code == 200:
        print("   ✅ Сортировка работает")
    else:
        print("   ❌ Сортировка не работает")
        return False
    
    return True


def test_task_creation_access():
    """Тест 5: Доступ к созданию задания"""
    print("\n🧪 Тест 5: Доступ к созданию задания")
    response = requests.get('http://127.0.0.1:5000/task/create', allow_redirects=False)
    
    # Должен быть редирект на логин для неавторизованных
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("   ✅ Неавторизованные пользователи перенаправляются на /login")
        return True
    else:
        print(f"   ❌ Неожиданное поведение: {response.status_code}")
        return False


def test_task_categories():
    """Тест 6: Категории заданий"""
    print("\n🧪 Тест 6: Категории заданий")
    with app.app_context():
        tasks = Task.query.all()
        categories = set(task.category for task in tasks)
        
        expected_categories = {
            'уборка', 'доставка', 'мастер', 'сантехника', 'электрика',
            'няня', 'репетитор', 'переезд', 'сборка мебели', 
            'компьютерная помощь', 'другое'
        }
        
        if categories.issubset(expected_categories):
            print(f"   ✅ Все категории корректны: {categories}")
            return True
        else:
            print(f"   ❌ Найдены некорректные категории: {categories - expected_categories}")
            return False


def test_task_urgency():
    """Тест 7: Срочность заданий"""
    print("\n🧪 Тест 7: Срочность заданий")
    with app.app_context():
        tasks = Task.query.all()
        urgencies = set(task.urgency for task in tasks)
        
        expected_urgencies = {'срочно', 'планово', 'навыки'}
        
        if urgencies.issubset(expected_urgencies):
            print(f"   ✅ Все уровни срочности корректны: {urgencies}")
            return True
        else:
            print(f"   ❌ Найдены некорректные уровни: {urgencies - expected_urgencies}")
            return False


def test_task_status():
    """Тест 8: Статусы заданий"""
    print("\n🧪 Тест 8: Статусы заданий")
    with app.app_context():
        tasks = Task.query.all()
        statuses = set(task.status for task in tasks)
        
        expected_statuses = {'active', 'completed', 'cancelled'}
        
        if statuses.issubset(expected_statuses):
            print(f"   ✅ Все статусы корректны: {statuses}")
            return True
        else:
            print(f"   ❌ Найдены некорректные статусы: {statuses - expected_statuses}")
            return False


def test_phone_masking():
    """Тест 9: Маскирование телефонов в заданиях"""
    print("\n🧪 Тест 9: Маскирование телефонов")
    with app.app_context():
        tasks = Task.query.all()
        all_masked = True
        
        for task in tasks:
            if '****' not in task.phone_hidden:
                print(f"   ❌ Телефон не маскирован в задании #{task.id}")
                all_masked = False
        
        if all_masked:
            print("   ✅ Все телефоны маскированы корректно")
            return True
        else:
            return False


def test_task_creator_relation():
    """Тест 10: Связь задания с создателем"""
    print("\n🧪 Тест 10: Связь задания с создателем")
    with app.app_context():
        tasks = Task.query.all()
        all_have_creator = True
        
        for task in tasks:
            if not task.creator:
                print(f"   ❌ Задание #{task.id} не имеет создателя")
                all_have_creator = False
        
        if all_have_creator:
            print("   ✅ Все задания имеют создателей")
            return True
        else:
            return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ ЭТАПА 3: CRUD ЗАДАНИЙ")
    print("=" * 60)
    
    tests = [
        test_database_tasks,
        test_tasks_list_page,
        test_task_detail_page,
        test_filters,
        test_task_creation_access,
        test_task_categories,
        test_task_urgency,
        test_task_status,
        test_phone_masking,
        test_task_creator_relation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Ошибка выполнения: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"✅ Успешно: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Процент успеха: {(passed / len(tests) * 100):.1f}%")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
