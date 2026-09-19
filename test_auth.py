#!/usr/bin/env python3
"""
Тестирование аутентификации для ЭТАПА 2
"""

import requests
from models import db, User
from app import app

def test_database_users():
    """Тест 1: Проверка пользователей в базе данных"""
    print("\n🧪 Тест 1: Проверка пользователей в БД")
    with app.app_context():
        users = User.query.all()
        print(f"   Найдено пользователей: {len(users)}")
        for user in users:
            print(f"   - {user.name} ({user.phone}) - {user.role}")
        print("   ✅ Тест пройден")
        return True


def test_registration_page():
    """Тест 2: Доступность страницы регистрации"""
    print("\n🧪 Тест 2: Страница регистрации")
    response = requests.get('http://127.0.0.1:5000/register')
    if response.status_code == 200 and 'Регистрация' in response.text:
        print("   ✅ Страница регистрации доступна")
        return True
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        return False


def test_login_page():
    """Тест 3: Доступность страницы входа"""
    print("\n🧪 Тест 3: Страница входа")
    response = requests.get('http://127.0.0.1:5000/login')
    if response.status_code == 200 and 'Вход в систему' in response.text:
        print("   ✅ Страница входа доступна")
        return True
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        return False


def test_phone_validation():
    """Тест 4: Валидация номера телефона"""
    print("\n🧪 Тест 4: Валидация телефона")
    from auth import validate_phone
    
    test_cases = [
        ('+79021234567', '+79021234567'),
        ('89021234567', '+79021234567'),
        ('9021234567', '+79021234567'),
        ('+7 (902) 123-45-67', '+79021234567'),
        ('invalid', None),
        ('123', None),
    ]
    
    all_passed = True
    for input_phone, expected in test_cases:
        result = validate_phone(input_phone)
        if result == expected:
            print(f"   ✅ {input_phone} → {result}")
        else:
            print(f"   ❌ {input_phone} → {result} (ожидалось {expected})")
            all_passed = False
    
    return all_passed


def test_password_hashing():
    """Тест 5: Хеширование паролей"""
    print("\n🧪 Тест 5: Хеширование паролей")
    with app.app_context():
        test_user = User(name="Test", phone="+79999999999", role="customer")
        test_user.set_password("testpass123")
        
        # Проверяем, что пароль хешируется
        if test_user.password_hash and test_user.password_hash != "testpass123":
            print(f"   ✅ Пароль хеширован")
            
            # Проверяем правильный пароль
            if test_user.check_password("testpass123"):
                print("   ✅ Проверка правильного пароля работает")
            else:
                print("   ❌ Ошибка проверки правильного пароля")
                return False
            
            # Проверяем неправильный пароль
            if not test_user.check_password("wrongpassword"):
                print("   ✅ Проверка неправильного пароля работает")
            else:
                print("   ❌ Ошибка: неправильный пароль принят")
                return False
            
            return True
        else:
            print("   ❌ Пароль не хеширован")
            return False


def test_user_roles():
    """Тест 6: Роли пользователей"""
    print("\n🧪 Тест 6: Роли пользователей")
    with app.app_context():
        users = User.query.all()
        roles = set(user.role for user in users)
        valid_roles = {'customer', 'executor', 'both'}
        
        if roles.issubset(valid_roles):
            print(f"   ✅ Все роли корректны: {roles}")
            return True
        else:
            print(f"   ❌ Найдены некорректные роли: {roles - valid_roles}")
            return False


def test_protected_route():
    """Тест 7: Защита маршрутов @login_required"""
    print("\n🧪 Тест 7: Защита маршрутов")
    response = requests.get('http://127.0.0.1:5000/profile', allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("   ✅ Неавторизованные пользователи перенаправляются на /login")
        return True
    else:
        print(f"   ❌ Ошибка защиты маршрута: {response.status_code}")
        return False


def test_masked_phone():
    """Тест 8: Маскирование телефона"""
    print("\n🧪 Тест 8: Маскирование телефона")
    with app.app_context():
        test_user = User(name="Test", phone="+79021234567", role="customer")
        masked = test_user.get_masked_phone()
        
        if masked == "+7****67":
            print(f"   ✅ Телефон маскирован: +79021234567 → {masked}")
            return True
        else:
            print(f"   ❌ Неверное маскирование: {masked}")
            return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ ЭТАПА 2: АУТЕНТИФИКАЦИЯ")
    print("=" * 60)
    
    tests = [
        test_database_users,
        test_registration_page,
        test_login_page,
        test_phone_validation,
        test_password_hashing,
        test_user_roles,
        test_protected_route,
        test_masked_phone,
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
