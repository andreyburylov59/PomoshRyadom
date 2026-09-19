#!/usr/bin/env python3
"""
Скрипт пересоздания БД с новой схемой
"""
import os
from app import app, db

# Удаляем старую БД
db_path = 'pomosh_ryadom.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️  Удалена старая БД: {db_path}")

# Создаем новую БД
with app.app_context():
    db.create_all()
    print("✅ БД создана с новой схемой!")
    
    # Проверяем наличие полей
    from models import Task
    from sqlalchemy import inspect
    
    inspector = inspect(db.engine)
    columns = inspector.get_columns('tasks')
    column_names = [col['name'] for col in columns]
    
    print(f"\n📋 Колонки таблицы tasks:")
    for col in column_names:
        print(f"   - {col}")
    
    if 'latitude' in column_names and 'longitude' in column_names:
        print("\n✅ Поля latitude и longitude присутствуют!")
    else:
        print("\n❌ Поля latitude и longitude отсутствуют!")
