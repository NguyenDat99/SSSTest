# CONFIG = {
#     'celery': {
#         'name': 'backend_worker',
#         'broker': 'pyamqp://guest@localhost//',
#         'backend': 'redis://localhost:6379/0',
#         'result_expires': 60 * 60 * 60  # 1h
#     },
#     'database': {
#         'url': 'postgresql://sssUser:sssPwd123@localhost/sssDb',
#         'service': 'sssDb'
#     }
# }

CONFIG = {
    'celery': {
        'name': 'backend_worker',
        'broker': 'pyamqp://SSS_user:SSS_pwd111@rabbit//',
        'backend': 'redis://redis:6379/0',
        'result_expires': 60 * 60 * 60  # 1h
    },
    'database': {
        'url': 'postgresql://sssUser:sssPwd123@postgresdb/sssDb',
        'service': 'sssDb'
    }
}


CELERY_REDIS_KEY = "celery-task-meta-"

REDIS_TIMEOUT = 300000  # 5m
REDIS_TRUSTED_DATA_LIMIT_BY_MINUTE = 1  # 10m
REDIS_EXPIRE_TIME_BY_THE_HOUR = 1  # 1H
REDIS_QUERY_KEY = "top_domain_logs"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SUCCESS = 'SUCCESS'
FAILURE = 'FAILURE'
MISS_DATA = 'MISS_DATA'

RESPONSE_STATUS = {
    'SUCCESS': 'Success',
    'FAILURE': 'Failure',
    'MISS_DATA': 'Missing data'
}


def get_new_domains_query_string(start_time):
    return f""" select logs.url , count(1) as count from logs where time>='{start_time}' and logs.url NOT IN
                (SELECT logs.url
                 FROM logs where time<'{start_time}')
            Group by logs.url
            Order BY count Desc;"""
