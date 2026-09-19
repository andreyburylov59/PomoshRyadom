# INDEX — Помощь Рядом

Канон продукта: этот каталог и репозиторий [andreyburylov59/PomoshRyadom](https://github.com/andreyburylov59/PomoshRyadom).

## Читать в таком порядке

1. `AGENT_CONTEXT.md` — что строим, чего не делать, текущий статус
2. `README.md` — установка и функции
3. `.cursorrules` — правила для агента
4. `models.py` + `app.py` — каркас
5. По задаче: `auth.py`, `routes.py`, `static/js/voice.js`, `static/js/geolocation.js`, `payment.py`, `reviews.py`, `moderation.py`

## Карта этапов

| Этап | Тема | Где смотреть |
|------|------|----------------|
| 1 | Каркас, БД, главная | `app.py`, `models.py`, `templates/index.html`, `static/css/style.css` |
| 2 | Регистрация и вход | `auth.py`, `templates/register.html`, `login.html`, `profile.html` |
| 3 | CRUD заданий | `routes.py`, `templates/tasks.html`, `create_task.html`, `task_detail.html` |
| 4 | Голосовой ввод | `static/js/voice.js` |
| 5 | Геолокация | `static/js/geolocation.js`, поля `latitude`/`longitude` в `Task` |
| 6 | Оплата контакта 50 ₽ | `payment.py`, `templates/pay.html` |
| 7 | Отзывы | `reviews.py` |
| 8 | Модерация | `moderation.py` |
| 9–10 | Адаптив, пожилые, СБП, доводка | ещё не отделены как готовый этап |

Отчёты `STAGE_*_COMPLETE.md` — история разработки, не источник истины по git-веткам.

## Запуск

```bash
pip install -r requirements.txt
python app.py
```

http://127.0.0.1:5000
