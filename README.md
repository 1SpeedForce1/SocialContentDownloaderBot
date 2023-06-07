# SocialContentDownloaderBot

SocialContentDownloaderBot - это телеграм-бот, написанный на языке Python 3.10, который позволяет скачивать контент из социальных сетей: Instagram, TikTok, Pinterest, YouTube Shorts. Достаточно лишь отправить ссылку, и бот скачает и отправит вам запрашиваемый контент. Для скачивания используется web scraping, а также сервис [Lamadava SaaS](https://lamadava.com/).

![Скриншот 1](https://i.ibb.co/L6CcTcL/photo-2023-06-07-12-45-29.jpg)

## Установка

1. Убедитесь, что у вас установлен Python 3.10. Если нет, скачайте и установите его с [официального сайта](https://www.python.org/downloads/).

2. Склонируйте репозиторий:

```git clone https://github.com/yourusername/SocialContentDownloaderBot.git```


3. Перейдите в каталог проекта:

```cd SocialContentDownloaderBot```


4. Установите необходимые библиотеки:

```pip install -r requirements.txt```


## Настройка

1. В файле main.py вставьте токен от телеграм-бота в переменную token.

2. Вставьте API-ключ от сервиса Lamadava SaaS в переменную api_key_lamadava.

3. Вставьте ID администраторов бота в переменные tg1 и tg2.

## Запуск

Для запуска проекта нужно запустить файл run.bat.

## Использование

Отправьте ссылку на контент из одной из поддерживаемых социальных сетей, и бот скачает и отправит вам контент.

![Скриншот 2](https://i.ibb.co/vHbDp5m/photo-2023-06-07-12-49-07.jpg)
## Библиотеки

- PyTelegramBotAPI
- json
- math
- pathlib
- shutil
- time
- bs4 (BeautifulSoup)
- telebot
- telebot.types
- sqlite3
- re
- pytube
- tldextract
- Flask
- typing
- requests
- moviepy.editor
- pathlib.Path
- PIL (Image)
- urllib.parse
- os
- ast.literal_eval

# Использование Git Flow
Рекомендуется использовать Git Flow для улучшения процесса разработки и коллективной работы над проектом. Git Flow представляет собой набор правил и рекомендаций по ветвлению в Git, что помогает организовать процесс разработки и упростить его управление.
![Скриншот 2](https://i.ibb.co/MGc3xYr/04-Hotfix-branches.png)

Основные ветки в Git Flow включают:
- Main: это основная ветка, которая содержит стабильную версию проекта.
- Develop: это ветка разработки, где происходит интеграция новых функций и исправлений.

Кроме того, есть несколько дополнительных веток:
- Feature: это ветки для разработки новых функций. Они создаются от ветки Develop и после завершения работы вливаются обратно в неё.
- Release: эти ветки используются для подготовки релиза. Они создаются от ветки Develop и после завершения подготовки релиза вливаются как в Main, так и в Develop.
- Hotfix: эти ветки используются для исправления критических ошибок в основной ветке. Они создаются от ветки Main и после исправления ошибки вливаются как в Main, так и в Develop.

Для удобства работы с Git Flow рекомендуется использовать расширение для Git, которое автоматизирует большинство операций. Вы можете начать использовать его, выполнив команду ```git flow init```
