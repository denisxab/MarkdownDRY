Пример `env` файла:

<pre>
# (!) - обозначает что нельзя изменять имя ПО, так как его используют официальное образы.

## Django
# Ключ для расшифровки сессии
DJANGO_SECRET_KEY="{{ secret_key }}"
# Имя проекта
NAME_PROJ="{{ project_name }}"
# Режим работы (true/false)
DEBUG=true


### Docker
# Путь к рабочей директории
WORK_DIR="/usr/src/{{ project_name }}"
# Путь к переемным окружениям
PATH_ENV="./__env.env"
# Внешний порт <!Изменить значения на свои>
EXTERNAL_WEB_PORT=8081
# Внешний и Внутренний порт для `nginx`. EXTERNAL_WEB_PORT != NGINX_PORT <!Изменить значеня на свои>
NGINX_PORT=8080


### Postgres
#  Имя БД (!) <!Изменить значения на свои>
POSTGRES_DB="postgres"
# Имя пользователя (!) <!Изменить значения на свои>
POSTGRES_USER="postgres"
# Пароль от пользователя (!) <!Изменить значения на свои>
POSTGRES_PASSWORD="postgres"
# Имя сервиса(контейнера)
POSTGRES_HOST="db"
# Порт подключения к БД. (По умолчанию 5432)
POSTGRES_PORT=5432
# Путь к зеркальной папке с БД
POSTGRES_VOLUMES="./db/pg_data"
</pre>

После парсинга этого файла получим `Python` словарь:

```
res = {
    'DJANGO_SECRET_KEY': '{{secret_key}}',
    'NAME_PROJ': '{{project_name}}',
    'DEBUG': 'true',
    'WORK_DIR': '/usr/src/{{project_name}}',
    'PATH_ENV': './__env.env',
    'EXTERNAL_WEB_PORT': '8081',
    'NGINX_PORT': '8080',
    'POSTGRES_DB': 'postgres',
    'POSTGRES_USER': 'postgres',
    'POSTGRES_PASSWORD': 'postgres',
    'POSTGRES_HOST': 'db',
    'POSTGRES_PORT': '5432',
    'POSTGRES_VOLUMES': './db/pg_data'
}

```

Код скрипта:

```
import os
import re
from pprint import pprint


def read_env_file_and_set_from_venv(file_name: str):
	"""Чтение переменных окружения из указанного файла, и добавление их в ПО `python`"""
	with open(file_name, 'r', encoding='utf-8') as _file:
		res = {}
		for line in _file:
			tmp = re.sub(r'^#[\s\w\d\W\t]*|[\t\s]', '', line)
			if tmp:
				k, v = tmp.split('=', 1)
				# Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
				if v.startswith('"') and v.endswith('"'):
					v = v[1:-1]

				res[k] = v
	os.environ.update(res)
	pprint(res)

```
