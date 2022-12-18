import datetime
from flask import request
from .config import TIME_FORMAT


class LogModel:
    def __init__(self, _request: request):
        content_type = _request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            self.data = _request.json
            self.id = self.data.get('id')
            self.__time = str(self.data.get('time'))
            self.url = self.data.get('url')

    def to_json(self):
        return self.data


class QueryModel(LogModel):
    def __init__(self, _request: request):
        super().__init__(_request)
        self.time_by_the_hour = self.data.get('time_by_the_hour')
        self.start_time = None
        if self.time_by_the_hour:
            self.start_time = str(
                (datetime.datetime.now() - datetime.timedelta(hours=self.time_by_the_hour)).strftime(TIME_FORMAT))
        self.end_time = str(datetime.datetime.now().strftime(TIME_FORMAT))


class UpdateLogModel(LogModel):
    def __init__(self, _request: request):
        super().__init__(_request)
        self.new_log = self.data.get('new_log')


class ListLogModel:
    def __init__(self, _request: request):
        content_type = _request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            self.data = _request.json
            self.logs = self.data.get('logs')

    def get_list(self):
        return self.logs
