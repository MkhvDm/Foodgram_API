[![foodgram_workflow](https://github.com/MkhvDm/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/MkhvDm/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

<h1><a href="http://51.250.31.8/">Foodgram</a></h1>

<h3>Кулинарный сервис.</h3>

## Возможности 
 - регистрируйся, подписывайся на авторов рецептов
 - публикуй собственные рецепты с набором нужных ингредиентов, отмечай рецепт тегом для поиска
 - сохраняй рецепт в избранное
 - добавляй рецепты в список покупок и скачивай PDF-файл с необходимыми ингредиентами

## Технологии
[![My Skills](https://skillicons.dev/icons?i=python,django,postgres,nginx,docker,react,git,github&theme=light)](https://skillicons.dev)


## Запуск проекта в Docker-контейнерах:
 ### Локально:
Клонировать репозиторий и перейти в него в командной строке:

```
either HTTPS:
git clone https://github.com/MkhvDm/foodgram-project-react.git
```
```
or SSH:
git clone git@github.com:MkhvDm/foodgram-project-react.git
```
В директории infra/ создать и заполнить файл .env. Пример: .env.default. 

Поднять контейнеры:
```
foodgram-project-react/ 
$ docker compose up --build -d
```
Далее в контейнере web небходимо выполнить команды:
```
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

###На удалённом сервере:

Проект подразумевает запуск в [Яндекс.Облаке]. 
Для успешного деплоя требуется запустить виртуальную машину (ВМ) на сервисе (ubuntu 22.04.1 LTS), 
установить на неё Docker, docker-compose.

В настройках проекта на GitHub требуется добавить необходимые секретные ключи для workflow:
- DB_ENGINE 
- DB_HOST
- DB_NAME
- DB_PORT
- DOCKER_USERNAME (required)
- DOCKER_PASSWORD (required)
- HOST_IP (публичный IP ВМ - required)
- POSTGRES_USER (user для работы с БД на ВМ)
- POSTGRES_PASSWORD
- SSH_KEY (секретный ключ локальной машины - required)
- SSH_PASSPHRASE (кодовая фраза, если есть - required)
- YCLOUD_USER (имя пользователя на сервисе Яндекс.Облако - required)
- TELEGRAM_BOT_TOKEN (ID Телеграм-бота для оповещения о успешном проходнении workflow)
- TELEGRAM_TO (ваш Telegram Token)

Если уведомления в телеграм не требуются, неоходимо отредактировать файл foodgram_workflow.yml - убрать job "send_message". 

Далее сделайте git push в ветку master.

При первом запуске после успешного прохождения всех стадий workflow,
находясь в директории с файлом docker-compose.yaml на ВМ
необходимо по очереди выполнить команды:
```
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Также необходимо заполнить базу данных ингредиентами и тегами:
```
sudo docker-compose exec web python manage.py load_ingredients
```

Сервис будет доступен на http://<HOST_IP>/.

Текущий адрес: http://51.250.31.8/
### DONE!

### Авторы
[Yandex Practicum Team] - frontend (React) \
[Дмитрий Михеев] - API, CI/CD, deploy - [Telegram] 

[Telegram]: <https://t.me/MkhvDm>
[Яндекс.Облаке]: <https://cloud.yandex.ru/>

[Yandex Practicum Team]: https://practicum.yandex.ru/
[Дмитрий Михеев]: <https://github.com/MkhvDm>
