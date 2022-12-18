import datetime
from flask import request as flask__request
from .config import TIME_FORMAT


class LogModel:
    def __init__(self, request: flask__request):
        self.__url = request.url
        self.__ip = request.remote_addr
        self.__path = request.path
        self.__datetime = str(datetime.datetime.now().strftime(TIME_FORMAT))

    def to_json(self):
        return {
            "url": self.__url,
            "ip": self.__ip,
            "path": self.__path,
            "datetime": self.__datetime
        }
