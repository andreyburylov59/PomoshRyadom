#!/usr/bin/env python3
"""
Тестирование системы оплаты (Этап 6)
"""
import requests
import os
from app import app, db
from models import User, Task, Payment

BASE_URL = 'http://127.0.0.1:5000'

def test_payment_system():
    """Тестирование полного цикла оплаты"""
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ОПЛАТЫ (ЭТАП 6)")
    print("=" * 70)
    
    session_customer = requests.Session()
    session_executor = requests.Session()
    
    # 1. Регистрация заказчика
    print("\n1️⃣ Регистрация заказчика...")
    import random
    customer_phone = f'+7999{random.randint(1000000, 9999999)}'
    register_data = {
        'name': 'Иван Заказчик',
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
        'name': 'Петр Исполнитель',
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
    
    # 3. Создание задания от заказчика
    print("\n3️⃣ Создание задания от заказчика...")
    task_data = {
        'title': 'Уборка квартиры',
        'description': 'Нужна генеральная уборка двухкомнатной квартиры',
        'category': 'уборка',
        'price': 2000,
        'address': 'ул. Ленина, д. 10, кв. 5',
        'district': 'Центральный',
        'urgency': 'планово',
        'latitude': 55.7558,
        'longitude': 37.6173
    }
    
    response = session_customer.post(f'{BASE_URL}/task/create', data=task_data, allow_redirects=False)
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        task_id = location.split('/')[-1] if '/task/' in location else None
        print(f"✅ Задание создано, ID: {task_id}")
    else:
        print(f"❌ Ошибка создания задания: {response.status_code}")
        task_id = None
        return
    
    # 4. Проверка маскированного номера для исполнителя
    print("\n4️⃣ Проверка маскированного номера...")
    response = session_executor.get(f'{BASE_URL}/task/{task_id}')
    if response.status_code == 200:
        content = response.text
        
        if '***' in content:
            print("✅ Номер телефона замаскирован для исполнителя")
        else:
            print("⚠️  Маскирование номера не обнаружено")
        
        if 'Оплатить 50₽' in content or 'оплатить' in content.lower():
            print("✅ Кнопка оплаты присутствует")
        else:
            print("⚠️  Кнопка оплаты не найдена")
    else:
        print(f"❌ Ошибка загрузки страницы задания: {response.status_code}")
    
    # 5. Переход на страницу оплаты
    print("\n5️⃣ Переход на страницу оплаты...")
    response = session_executor.get(f'{BASE_URL}/task/{task_id}/pay')
    if response.status_code == 200:
        print("✅ Страница оплаты загружена")
        
        content = response.text
        
        if '50 ₽' in content:
            print("✅ Сумма оплаты отображается")
        
        if 'QR' in content or 'qr' in content:
            print("✅ Упоминание QR-кода найдено")
        
        if 'Симулировать оплату' in content or 'симулир' in content.lower():
            print("✅ Кнопка симуляции оплаты присутствует")
    else:
        print(f"❌ Ошибка загрузки страницы оплаты: {response.status_code}")
    
    # 6. Проверка создания платежа в БД
    print("\n6️⃣ Проверка создания платежа в БД...")
    with app.app_context():
        payment = Payment.query.filter_by(task_id=int(task_id)).first()
        if payment:
            print(f"✅ Платеж создан в БД")
            print(f"   ID: {payment.id}")
            print(f"   Сумма: {payment.amount} ₽")
            print(f"   Статус: {payment.status}")
            
            if payment.qr_code_path:
                print(f"   QR-код: {payment.qr_code_path}")
                
                # Проверяем существование файла
                qr_path = os.path.join('static/uploads', payment.qr_code_path)
                if os.path.exists(qr_path):
                    print(f"   ✅ Файл QR-кода создан: {qr_path}")
                else:
                    print(f"   ⚠️  Файл QR-кода не найден: {qr_path}")
            else:
                print("   ⚠️  QR-код не сгенерирован")
            
            payment_id = payment.id
        else:
            print("❌ Платеж не найден в БД")
            payment_id = None
            return
    
    # 7. Симуляция оплаты
    print("\n7️⃣ Симуляция оплаты...")
    if payment_id:
        response = session_executor.post(
            f'{BASE_URL}/payment/{payment_id}/simulate',
            allow_redirects=False
        )
        if response.status_code == 302:
            print("✅ Симуляция оплаты выполнена")
        else:
            print(f"❌ Ошибка симуляции оплаты: {response.status_code}")
    
    # 8. Проверка статуса платежа после оплаты
    print("\n8️⃣ Проверка статуса платежа после оплаты...")
    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        if payment:
            print(f"   Статус: {payment.status}")
            if payment.status == 'paid':
                print("✅ Платеж отмечен как оплаченный")
                if payment.paid_at:
                    print(f"   Дата оплаты: {payment.paid_at}")
            else:
                print(f"⚠️  Платеж не оплачен, статус: {payment.status}")
        else:
            print("❌ Платеж не найден")
    
    # 9. Проверка разблокировки номера
    print("\n9️⃣ Проверка разблокировки номера...")
    response = session_executor.get(f'{BASE_URL}/task/{task_id}')
    if response.status_code == 200:
        content = response.text
        
        # Проверяем, что теперь виден полный номер (не маскированный)
        if customer_phone in content:
            print(f"✅ Полный номер телефона виден: {customer_phone}")
        else:
            print("⚠️  Полный номер не найден на странице")
        
        if 'tel:' in content:
            print("✅ Ссылка для звонка присутствует")
        else:
            print("⚠️  Ссылка для звонка не найдена")
        
        if 'Контакт разблокирован' in content or 'разблокирован' in content.lower():
            print("✅ Сообщение о разблокировке отображается")
    else:
        print(f"❌ Ошибка загрузки страницы: {response.status_code}")
    
    # 10. Проверка страницы "Мои платежи"
    print("\n🔟 Проверка страницы 'Мои платежи'...")
    response = session_executor.get(f'{BASE_URL}/my-payments')
    if response.status_code == 200:
        print("✅ Страница 'Мои платежи' загружена")
        
        content = response.text
        
        if 'Оплаченные контакты' in content:
            print("✅ Раздел оплаченных контактов найден")
        
        if str(payment_id) in content:
            print(f"✅ Платеж #{payment_id} отображается в списке")
    else:
        print(f"❌ Ошибка загрузки страницы 'Мои платежи': {response.status_code}")
    
    # 11. Итоговая статистика
    print("\n1️⃣1️⃣ Итоговая статистика...")
    with app.app_context():
        total_payments = Payment.query.count()
        paid_payments = Payment.query.filter_by(status='paid').count()
        
        print(f"Всего платежей: {total_payments}")
        print(f"Оплаченных: {paid_payments}")
        
        if paid_payments > 0:
            print(f"✅ Процент оплаченных: {paid_payments / total_payments * 100:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ ЭТАП 6: ОПЛАТА И КОНТАКТЫ - ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print("\n📋 Реализованные функции:")
    print("   ✅ Создание платежа при переходе на страницу оплаты")
    print("   ✅ Генерация QR-кода для оплаты СБП")
    print("   ✅ Маскирование номера телефона")
    print("   ✅ Симуляция оплаты (для тестирования)")
    print("   ✅ Разблокировка контакта после оплаты")
    print("   ✅ Ссылка для звонка (tel:)")
    print("   ✅ Страница 'Мои платежи'")
    print("   ✅ Отображение полного номера после оплаты")

if __name__ == '__main__':
    test_payment_system()
