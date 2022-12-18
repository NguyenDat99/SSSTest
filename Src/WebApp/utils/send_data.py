from celery import Celery
from flask import request
from loguru import logger
from .log import LogModel
from .config import CONFIG


class SendData:
    __celery: Celery = Celery(CONFIG['name'], broker=CONFIG['broker'], backend=CONFIG['backend'])

    def send(self, _request: request):
        try:
            logs = LogModel(request).to_json()
            self.__celery.send_task('tasks.push_tracking_data', kwargs={'logs': logs})
            logger.info(f"SendData: {logs}")
        except Exception as ex:
            logger.error(f"Error: {ex}")


send_messages = SendData()
