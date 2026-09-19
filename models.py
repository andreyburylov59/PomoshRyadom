from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Модель пользователя (заказчик/исполнитель)"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    district = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, default=5.0)
    completed_tasks = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    blocked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    tasks_created = db.relationship('Task', backref='creator', lazy='dynamic', foreign_keys='Task.user_id')
    tasks_executed = db.relationship('Task', backref='executor_user', lazy='dynamic', foreign_keys='Task.executor_id')
    payments = db.relationship('Payment', backref='payer', lazy='dynamic')
    
    def set_password(self, password):
        """Установить хешированный пароль"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)
    
    def get_masked_phone(self):
        """Получить маскированный номер телефона"""
        if len(self.phone) >= 10:
            return self.phone[:2] + '****' + self.phone[-2:]
        return '***'
    
    def update_rating(self):
        """Обновить средний рейтинг пользователя на основе полученных отзывов"""
        reviews = Review.query.filter_by(reviewee_id=self.id).all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            self.rating = round(total_rating / len(reviews), 1)
            self.completed_tasks = len(reviews)
            db.session.commit()
    
    def get_reviews_count(self):
        """Получить количество отзывов"""
        return Review.query.filter_by(reviewee_id=self.id).count()
    
    def get_average_rating(self):
        """Получить средний рейтинг с одним знаком после запятой"""
        return round(self.rating, 1)
    
    def get_reports_count(self):
        """Получить количество жалоб на пользователя"""
        return Report.query.filter_by(reported_user_id=self.id, status='pending').count()
    
    def block_user(self, reason='Множественные жалобы'):
        """Заблокировать пользователя"""
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
        db.session.commit()
    
    def unblock_user(self):
        """Разблокировать пользователя"""
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_at = None
        db.session.commit()
    
    def get_active_tasks_count(self):
        """Получить количество активных заданий пользователя"""
        return Task.query.filter_by(user_id=self.id, status='active').count()
    
    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'


class Task(db.Model):
    """Модель задачи/заказа"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False, default='планово')
    status = db.Column(db.String(20), nullable=False, default='active')
    phone_hidden = db.Column(db.String(20), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Связи
    payments = db.relationship('Payment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_phone_unlocked_for(self, user_id):
        """Проверить, разблокирован ли телефон для конкретного пользователя"""
        if self.user_id == user_id:
            return True
        payment = Payment.query.filter_by(
            task_id=self.id,
            executor_id=user_id,
            status='paid'
        ).first()
        return payment is not None
    
    def get_display_phone(self, user_id):
        """Получить номер телефона (полный или маскированный)"""
        if self.is_phone_unlocked_for(user_id):
            return self.creator.phone
        return self.phone_hidden
    
    def mark_as_completed(self, executor_id):
        """Отметить задание как выполненное"""
        self.status = 'completed'
        self.executor_id = executor_id
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def can_review(self, user_id):
        """Проверить, может ли пользователь оставить отзыв"""
        # Проверяем, что задание выполнено
        if self.status != 'completed':
            return False
        
        # Проверяем, что пользователь участвовал в задании
        if user_id not in [self.user_id, self.executor_id]:
            return False
        
        # Проверяем, что отзыв еще не оставлен
        existing_review = Review.query.filter_by(
            task_id=self.id,
            reviewer_id=user_id
        ).first()
        
        return existing_review is None
    
    def get_reviewee_id(self, reviewer_id):
        """Получить ID пользователя, которого нужно оценить"""
        if reviewer_id == self.user_id:
            return self.executor_id  # Заказчик оценивает исполнителя
        elif reviewer_id == self.executor_id:
            return self.user_id  # Исполнитель оценивает заказчика
        return None
    
    def __repr__(self):
        return f'<Task {self.title} ({self.status})>'


class Payment(db.Model):
    """Модель платежа за доступ к номеру телефона"""
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False, default=50)
    qr_code_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    def generate_qr_code(self):
        """Генерация QR-кода для оплаты через СБП"""
        import qrcode
        import os
        from config import Config
        
        # Формируем данные для СБП (упрощенный формат)
        # В реальности нужно использовать официальный формат СБП
        payment_data = f"SPB|{self.id}|{self.amount}|Разблокировка контакта"
        
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_data)
        qr.make(fit=True)
        
        # Генерируем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем файл
        upload_folder = Config.UPLOAD_FOLDER
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"qr_payment_{self.id}.png"
        filepath = os.path.join(upload_folder, filename)
        img.save(filepath)
        
        # Сохраняем путь в БД
        self.qr_code_path = filename
        db.session.commit()
        
        return filepath
    
    def mark_as_paid(self):
        """Отметить платеж как оплаченный"""
        self.status = 'paid'
        self.paid_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Payment {self.id} for Task {self.task_id} ({self.status})>'


class Review(db.Model):
    """Модель отзыва о выполненном задании"""
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 звезд
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Связи
    task = db.relationship('Task', backref='reviews', foreign_keys=[task_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='reviews_received')
    
    def __repr__(self):
        return f'<Review {self.id} for Task {self.task_id} ({self.rating}★)>'


class Report(db.Model):
    """Модель жалобы на пользователя или задание"""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    reported_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True, index=True)
    reason = db.Column(db.String(50), nullable=False)  # spam, fraud, inappropriate, other
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, reviewed, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Связи
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_made')
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref='reports_received')
    reported_task = db.relationship('Task', foreign_keys=[reported_task_id], backref='reports')
    
    def __repr__(self):
        return f'<Report {self.id} ({self.reason}) - {self.status}>'
