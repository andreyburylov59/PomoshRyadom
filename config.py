import os

class Config:
    """Конфигурация приложения Flask"""
    
    # Базовая директория проекта
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Секретный ключ для сессий и CSRF-защиты
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-pomosh-ryadom-2024-super-secure'
    
    # Настройки базы данных SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'pomosh_ryadom.db')
    
    # Отключаем отслеживание модификаций (экономия памяти)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Папка для загрузки файлов (QR-коды)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    
    # Максимальный размер загружаемого файла (16 МБ)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Стоимость доступа к номеру телефона
    PHONE_ACCESS_PRICE = 50
    
    # Список доступных районов
    DISTRICTS = [
        'Центральный',
        'Северный',
        'Южный',
        'Западный',
        'Восточный',
        'Ленинский',
        'Октябрьский',
        'Советский',
        'Железнодорожный',
        'Заречный'
    ]
    
    # Категории задач
    TASK_CATEGORIES = [
        'уборка',
        'доставка',
        'мастер',
        'сантехника',
        'электрика',
        'няня',
        'репетитор',
        'переезд',
        'сборка мебели',
        'компьютерная помощь',
        'другое'
    ]
    
    # Статусы срочности
    URGENCY_LEVELS = [
        'срочно',
        'планово',
        'навыки'
    ]
