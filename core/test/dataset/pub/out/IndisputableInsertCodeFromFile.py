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
