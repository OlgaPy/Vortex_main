# Капибара


## Getting started

Для того, чтобы начать работать с монолитом

1. Создайте файл `.env` в корневой директории проекта
```bash
cp .env.template .env
```
2. Запустите приложение

```bash
docker-compose up
```
3. Выполните миграцию базы данных
```bash
docker-compose exec kapibara-monolith ./manage.py migrate

```
4. Cоздайте администратора
```bash
docker-compose exec kapibara-monolith ./manage.py createsuperuser

```
5. Некоторые полезные страницы
   * Админка - http://localhost:8888/kapibar/
   * API документация
     * Swagger - http://localhost:8888/api/v1/schema/swagger-ui/
     * Redoc - http://localhost:8888/api/v1/schema/redoc/

## Ссылки
* Прямая линия с разработчиками - https://t.me/straight_line_nop
* Коммьюнити капибар - https://t.me/new_old_pikabu
* Капибара новое - https://t.me/new_kapibara
* Капибара лучшее - https://t.me/best_kapibara
* Бот для публикации контента - https://t.me/ContentAddBot
* Идейный вдохновитель проекта, Ольга - https://t.me/FreeDaSw
