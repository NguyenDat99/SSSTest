from celery.utils.log import get_task_logger
from celery import Celery
from .config import CONFIG

celery_worker = Celery(CONFIG['celery']['name'],
                       broker=CONFIG['celery']['broker'],
                       backend=CONFIG['celery']['backend'])

celery_worker.conf.result_expires = CONFIG['celery']['result_expires']

celery_logger = get_task_logger(__name__)
