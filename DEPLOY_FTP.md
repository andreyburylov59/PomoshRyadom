# 🚀 ДЕПЛОЙ НА FTP СЕРВЕР (ПРОДАКШН)

## Полная инструкция по размещению проекта на удаленном сервере

---

## 📋 ЧТО ВАМ ПОНАДОБИТСЯ

### 1. FTP доступы
- Хост (например: `ftp.yoursite.com`)
- Порт (обычно `21`)
- Логин
- Пароль

### 2. Доступ к серверу по SSH (желательно)
- IP адрес или домен
- SSH порт (обычно `22`)
- Логин (обычно `root` или ваше имя)
- Пароль или SSH ключ

### 3. Технические требования сервера

**Минимальные:**
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.10+
- 1 GB RAM
- 10 GB дискового пространства

**Рекомендуемые:**
- Ubuntu 22.04 LTS
- Python 3.11
- 2 GB RAM
- 20 GB SSD

---

## 🎯 ПЛАН ДЕПЛОЯ

### Этап 1: Подготовка проекта для продакшена ✅
### Этап 2: Настройка сервера
### Этап 3: Загрузка файлов через FTP
### Этап 4: Установка зависимостей на сервере
### Этап 5: Настройка базы данных (PostgreSQL)
### Этап 6: Настройка Gunicorn (WSGI сервер)
### Этап 7: Настройка Nginx (веб-сервер)
### Этап 8: Настройка SSL (HTTPS)
### Этап 9: Автозапуск через systemd
### Этап 10: Мониторинг и логи

---

## 📝 ЭТАП 1: ПОДГОТОВКА ПРОЕКТА

### 1.1 Создайте файл конфигурации для продакшена

**Файл: `config_production.py`**

```python
import os

class ProductionConfig:
    # Безопасность
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ЗАМЕНИТЕ_НА_СЛУЧАЙНУЮ_СТРОКУ_50+_СИМВОЛОВ'
    
    # База данных PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/pomosh_ryadom'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Загрузка файлов
    UPLOAD_FOLDER = '/var/www/pomosh_ryadom/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Оплата
    PHONE_ACCESS_PRICE = 50
    
    # Районы (можно расширить)
    DISTRICTS = [
        'Центральный', 'Северный', 'Южный', 'Западный', 'Восточный',
        'Заречный', 'Промышленный', 'Нагорный', 'Октябрьский', 'Приморский'
    ]
    
    # Категории
    TASK_CATEGORIES = [
        'уборка', 'доставка', 'сантехника', 'электрика', 'ремонт',
        'няня', 'уход', 'грузчики', 'переезд', 'мастер', 'прочее'
    ]
    
    # Срочность
    URGENCY_LEVELS = ['срочно', 'планово', 'навыки']
    
    # Prodакшн режим
    DEBUG = False
    TESTING = False
```

### 1.2 Создайте файл WSGI для Gunicorn

**Файл: `wsgi.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app

if __name__ == "__main__":
    app.run()
```

### 1.3 Создайте requirements для продакшена

**Файл: `requirements_production.txt`**

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
qrcode==7.4.2
Pillow==10.1.0
Werkzeug==3.0.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 1.4 Создайте файл .env для переменных окружения

**Файл: `.env.example`** (скопируйте в `.env` и заполните)

```bash
# Секретный ключ Flask (сгенерируйте случайный)
SECRET_KEY=ваш_случайный_секретный_ключ_минимум_50_символов

# База данных PostgreSQL
DATABASE_URL=postgresql://pomosh_user:strong_password@localhost/pomosh_ryadom

# Режим
FLASK_ENV=production

# Домен
DOMAIN=yoursite.com
```

---

## 🖥️ ЭТАП 2: НАСТРОЙКА СЕРВЕРА

### 2.1 Подключитесь к серверу по SSH

```bash
ssh root@your_server_ip
```

### 2.2 Обновите систему

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.3 Установите необходимые пакеты

```bash
# Python и pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Nginx
sudo apt install nginx -y

# Дополнительные пакеты
sudo apt install git curl wget build-essential libpq-dev -y
```

### 2.4 Создайте пользователя для приложения

```bash
sudo useradd -m -s /bin/bash pomosh
sudo passwd pomosh
```

### 2.5 Создайте структуру папок

```bash
sudo mkdir -p /var/www/pomosh_ryadom
sudo chown -R pomosh:pomosh /var/www/pomosh_ryadom
```

---

## 📤 ЭТАП 3: ЗАГРУЗКА ФАЙЛОВ ЧЕРЕЗ FTP

### Способ 1: FTP клиент (FileZilla)

1. **Скачайте FileZilla**: https://filezilla-project.org/

2. **Подключитесь к серверу:**
   - Хост: `ftp.yoursite.com`
   - Порт: `21`
   - Логин: ваш логин
   - Пароль: ваш пароль

3. **Загрузите файлы:**
   - Локальная папка: `E:\Cursor\PomoshRyadom\`
   - Удаленная папка: `/var/www/pomosh_ryadom/`
   
4. **НЕ загружайте:**
   - `venv/` (создадим на сервере)
   - `instance/` (база данных SQLite)
   - `__pycache__/`
   - `*.pyc`
   - `.git/` (если есть)

### Способ 2: Через командную строку (lftp)

На сервере:

```bash
cd /var/www/pomosh_ryadom
lftp -u username,password ftp.yoursite.com
> mirror /path/to/remote/folder /var/www/pomosh_ryadom
> quit
```

### Способ 3: Git (если на сервере есть доступ)

```bash
cd /var/www/pomosh_ryadom
git clone https://github.com/andreyburylov59/PomoshRyadom.git .
```

---

## 📦 ЭТАП 4: УСТАНОВКА ЗАВИСИМОСТЕЙ

### 4.1 Перейдите в папку проекта

```bash
cd /var/www/pomosh_ryadom
```

### 4.2 Создайте виртуальное окружение

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4.3 Установите зависимости

```bash
pip install --upgrade pip
pip install -r requirements_production.txt
```

---

## 🗄️ ЭТАП 5: НАСТРОЙКА POSTGRESQL

### 5.1 Подключитесь к PostgreSQL

```bash
sudo -u postgres psql
```

### 5.2 Создайте базу данных и пользователя

```sql
CREATE DATABASE pomosh_ryadom;
CREATE USER pomosh_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE pomosh_ryadom TO pomosh_user;
\q
```

### 5.3 Обновите config.py

Замените SQLite на PostgreSQL в `config.py`:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://pomosh_user:strong_password_here@localhost/pomosh_ryadom'
```

### 5.4 Инициализируйте базу данных

```bash
source venv/bin/activate
python recreate_db.py
```

---

## 🔧 ЭТАП 6: НАСТРОЙКА GUNICORN

### 6.1 Создайте конфигурацию Gunicorn

**Файл: `gunicorn_config.py`**

```python
import multiprocessing

# Сервер
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Логирование
accesslog = "/var/log/pomosh_ryadom/access.log"
errorlog = "/var/log/pomosh_ryadom/error.log"
loglevel = "info"

# Daemon
daemon = False
pidfile = "/var/run/pomosh_ryadom/gunicorn.pid"
user = "pomosh"
group = "pomosh"
```

### 6.2 Создайте папки для логов

```bash
sudo mkdir -p /var/log/pomosh_ryadom
sudo mkdir -p /var/run/pomosh_ryadom
sudo chown -R pomosh:pomosh /var/log/pomosh_ryadom
sudo chown -R pomosh:pomosh /var/run/pomosh_ryadom
```

### 6.3 Проверьте запуск Gunicorn

```bash
cd /var/www/pomosh_ryadom
source venv/bin/activate
gunicorn -c gunicorn_config.py wsgi:app
```

Если работает, нажмите `Ctrl+C` и переходите к следующему шагу.

---

## 🌐 ЭТАП 7: НАСТРОЙКА NGINX

### 7.1 Создайте конфигурацию Nginx

**Файл: `/etc/nginx/sites-available/pomosh_ryadom`**

```nginx
server {
    listen 80;
    server_name yoursite.com www.yoursite.com;

    # Логи
    access_log /var/log/nginx/pomosh_ryadom_access.log;
    error_log /var/log/nginx/pomosh_ryadom_error.log;

    # Статические файлы
    location /static {
        alias /var/www/pomosh_ryadom/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Загруженные файлы
    location /uploads {
        alias /var/www/pomosh_ryadom/static/uploads;
        expires 30d;
    }

    # Проксирование на Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Максимальный размер загружаемого файла
    client_max_body_size 16M;
}
```

### 7.2 Активируйте конфигурацию

```bash
sudo ln -s /etc/nginx/sites-available/pomosh_ryadom /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 ЭТАП 8: НАСТРОЙКА SSL (HTTPS)

### 8.1 Установите Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 8.2 Получите SSL сертификат

```bash
sudo certbot --nginx -d yoursite.com -d www.yoursite.com
```

Следуйте инструкциям Certbot.

### 8.3 Автообновление сертификата

```bash
sudo certbot renew --dry-run
```

Certbot автоматически настроит cron для обновления.

---

## ⚙️ ЭТАП 9: АВТОЗАПУСК ЧЕРЕЗ SYSTEMD

### 9.1 Создайте systemd сервис

**Файл: `/etc/systemd/system/pomosh_ryadom.service`**

```ini
[Unit]
Description=Pomosh Ryadom Gunicorn daemon
After=network.target postgresql.service

[Service]
Type=notify
User=pomosh
Group=pomosh
WorkingDirectory=/var/www/pomosh_ryadom
Environment="PATH=/var/www/pomosh_ryadom/venv/bin"
ExecStart=/var/www/pomosh_ryadom/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9.2 Запустите сервис

```bash
sudo systemctl daemon-reload
sudo systemctl start pomosh_ryadom
sudo systemctl enable pomosh_ryadom
sudo systemctl status pomosh_ryadom
```

---

## 📊 ЭТАП 10: МОНИТОРИНГ И ЛОГИ

### 10.1 Просмотр логов

```bash
# Логи приложения
sudo tail -f /var/log/pomosh_ryadom/error.log
sudo tail -f /var/log/pomosh_ryadom/access.log

# Логи Nginx
sudo tail -f /var/log/nginx/pomosh_ryadom_error.log

# Логи systemd
sudo journalctl -u pomosh_ryadom -f
```

### 10.2 Перезапуск сервисов

```bash
# Перезапуск приложения
sudo systemctl restart pomosh_ryadom

# Перезапуск Nginx
sudo systemctl restart nginx

# Перезагрузка конфигурации без простоя
sudo systemctl reload pomosh_ryadom
```

---

## 🔧 ОБНОВЛЕНИЕ ПРОЕКТА

### Способ 1: Через FTP

1. Загрузите обновленные файлы через FileZilla
2. Перезапустите сервис:
   ```bash
   sudo systemctl restart pomosh_ryadom
   ```

### Способ 2: Через Git (если настроен)

```bash
cd /var/www/pomosh_ryadom
git pull origin main
source venv/bin/activate
pip install -r requirements_production.txt
sudo systemctl restart pomosh_ryadom
```

### Способ 3: Скрипт автодеплоя

Создайте `deploy.sh`:

```bash
#!/bin/bash
cd /var/www/pomosh_ryadom
git pull origin main
source venv/bin/activate
pip install -r requirements_production.txt
sudo systemctl restart pomosh_ryadom
echo "✅ Деплой завершен!"
```

Запуск:
```bash
bash deploy.sh
```

---

## ❓ ЧАСТЫЕ ПРОБЛЕМЫ

### Проблема 1: "502 Bad Gateway"

**Причина:** Gunicorn не запущен или упал

**Решение:**
```bash
sudo systemctl status pomosh_ryadom
sudo systemctl restart pomosh_ryadom
sudo tail -f /var/log/pomosh_ryadom/error.log
```

### Проблема 2: Статические файлы не загружаются

**Причина:** Неправильные права доступа

**Решение:**
```bash
sudo chown -R pomosh:www-data /var/www/pomosh_ryadom/static
sudo chmod -R 755 /var/www/pomosh_ryadom/static
```

### Проблема 3: База данных не подключается

**Причина:** Неправильные креденшиалы PostgreSQL

**Решение:**
Проверьте `.env` и config.py, убедитесь что:
- Пользователь создан
- Пароль правильный
- База данных создана
- Есть права доступа

### Проблема 4: "Permission denied" при записи файлов

**Решение:**
```bash
sudo chown -R pomosh:pomosh /var/www/pomosh_ryadom
sudo chmod -R 755 /var/www/pomosh_ryadom
```

---

## 🔐 БЕЗОПАСНОСТЬ

### Обязательно сделайте:

1. ✅ Смените SECRET_KEY на случайный
2. ✅ Используйте сильные пароли для PostgreSQL
3. ✅ Настройте firewall (ufw)
4. ✅ Отключите root SSH вход
5. ✅ Настройте fail2ban
6. ✅ Регулярно обновляйте систему
7. ✅ Настройте бэкапы базы данных

### Firewall (ufw)

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
sudo ufw status
```

### Fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📦 БЭКАПЫ

### Автоматический бэкап PostgreSQL

Создайте скрипт `/usr/local/bin/backup_pomosh.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/pomosh_ryadom"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U pomosh_user pomosh_ryadom > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql
# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Добавьте в cron (ежедневно в 2:00):

```bash
sudo crontab -e
0 2 * * * /usr/local/bin/backup_pomosh.sh
```

---

## ✅ ЧЕКЛИСТ ДЕПЛОЯ

- [ ] Сервер настроен (Ubuntu, Python, PostgreSQL, Nginx)
- [ ] Проект загружен на сервер
- [ ] Виртуальное окружение создано
- [ ] Зависимости установлены
- [ ] PostgreSQL настроен
- [ ] `.env` файл создан и заполнен
- [ ] SECRET_KEY сгенерирован
- [ ] Gunicorn запускается
- [ ] Nginx настроен
- [ ] SSL сертификат установлен
- [ ] Systemd сервис создан и запущен
- [ ] Firewall настроен
- [ ] Бэкапы настроены
- [ ] Логи проверены
- [ ] Сайт доступен по HTTPS

---

## 📞 ПОДДЕРЖКА

Если что-то не работает:

1. Проверьте логи: `/var/log/pomosh_ryadom/error.log`
2. Проверьте статус сервиса: `sudo systemctl status pomosh_ryadom`
3. Проверьте Nginx: `sudo nginx -t`
4. Проверьте PostgreSQL: `sudo systemctl status postgresql`

---

**Готово! Ваше приложение развернуто на продакшн сервере! 🎉**

---

**Дата:** 18 сентября 2026  
**Версия:** 1.0  
**Для:** Ubuntu 22.04 LTS
