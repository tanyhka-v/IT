[README.md](https://github.com/user-attachments/files/27644389/README.md)
# GitHub User Finder

**Автор:** Зарвинова Татьяна

## Описание
GUI-приложение для поиска пользователей GitHub с использованием официального API. Отображает аватары, позволяет добавлять пользователей в избранное и сохранять список в JSON-файл.

## Установка и запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш_логин/github-user-finder.git
   cd github-user-finder
   
   Как использовать API
Приложение отправляет GET-запрос к https://api.github.com/search/users?q={username}.
Для загрузки аватаров используется дополнительный запрос к URL аватара.
API не требует аутентификации, ограничение: 60 запросов в час для неавторизованных.

Примеры использования
Введите torvalds → Search → выберите пользователя → Add to Favorites.

Во вкладке Favorites отобразятся сохранённые.

Кнопки Save/Load Favorites сохраняют/загружают список в favorites.json.
