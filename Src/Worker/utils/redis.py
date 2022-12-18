import datetime
from typing import List

from loguru import logger
import redis
import json
from .config import CELERY_REDIS_KEY, REDIS_TIMEOUT, REDIS_TRUSTED_DATA_LIMIT_BY_MINUTE, TIME_FORMAT, \
    REDIS_EXPIRE_TIME_BY_THE_HOUR, RESPONSE_STATUS, FAILURE, SUCCESS

from .log_model import QueryModel

redis_cache = redis.Redis(host='localhost', port=6379, db=0)


def redis_get_data(key: str, clean_cache=True) -> dict:
    data = None
    for i in range(0, REDIS_TIMEOUT):
        data = redis_cache.get(key)
        if data:
            try:
                data = json.loads(data)
                break
            except Exception as ex:
                if clean_cache:
                    redis_cache.delete(key)
                logger.error(f"Error :{ex}")
    if clean_cache:
        redis_cache.delete(key)
    return data if data else {}


def get_celery_redis_data(celery_task_id: str, clean_cache=True) -> dict:
    return redis_get_data(CELERY_REDIS_KEY + celery_task_id, clean_cache)


def push_redis_data(key, value):
    try:
        redis_cache.expire(key, datetime.timedelta(hours=REDIS_EXPIRE_TIME_BY_THE_HOUR))
        redis_cache.lpush(key, str(value))
    except Exception as ex:
        logger.error(ex)


def pop_redis_data(key: str, start_index: int, end_index: int):
    try:
        return redis_cache.lrange(key, start_index, end_index)
    except Exception as ex:
        logger.error(ex)


def get_cache_query_data(key, query: QueryModel):
    length = - int(redis_cache.llen(key))
    new_query_db = []
    new_query_cache = []
    miss_data_flag = False
    if length == 0:
        new_query_db.append({'start_time': str(query.start_time), 'end_time': query.end_time})
        return {
            'data': None,
            'query_string': get_query_string(new_query_db)
        }

    try:
        for index in range(length, 0):
            cache = eval(pop_redis_data(key, index, index)[0].decode("utf-8"))
            query_start_time = datetime.datetime.strptime(query.start_time, TIME_FORMAT)
            cache_start_time = datetime.datetime.strptime(cache['start_time'], TIME_FORMAT)
            cache_end_time = datetime.datetime.strptime(cache['end_time'], TIME_FORMAT)
            if query_start_time >= cache_end_time:
                new_query_db.append({'start_time': query.start_time, 'end_time': query.end_time})
                miss_data_flag = True
                break
            if query_start_time > cache_start_time and (query_start_time - cache_start_time) < datetime.timedelta(
                    minutes=REDIS_TRUSTED_DATA_LIMIT_BY_MINUTE):
                if RESPONSE_STATUS[FAILURE] in cache['response']:
                    new_query_db.append({'start_time': query.start_time, 'end_time': query.end_time})
                    break
                new_query_cache.append(cache)
                new_query_db.append({'start_time': str(cache_end_time), 'end_time': query.end_time})
                miss_data_flag = True
                break
            if query_start_time < cache_start_time and (RESPONSE_STATUS[FAILURE] not in cache['response']):
                #     new_query_cache.append(cache)
                new_query_db.append({'start_time': str(query.start_time), 'end_time': query.end_time})
                break
            #     query.end_time = str(cache_start_time)
    except Exception as ex:
        logger.error(ex)
        return {}
    if not miss_data_flag:
        new_query_db.append({'start_time': str(query.start_time), 'end_time': query.end_time})
    return {
        'data': get_list_result(new_query_cache, 'response') if new_query_cache else None,
        'query_string': get_query_string(new_query_db) if new_query_db else None
    }


def get_list_result(list_value: List[dict], item_key):
    response = {}
    for value in list_value:
        item = value.get(item_key, {})
        if isinstance(item, str):
            item = {}
        for key, value in item.items():
            response[key] = value if not response.get(key) else value + response[key]
    return response


def get_query_string(list_value: List[dict]):
    query_string = "select logs.url, count(1) as count from logs where "
    for index in range(0, len(list_value)):
        query_string += "(time>='"
        query_string += list_value[index]['start_time']
        query_string += "' and "
        query_string += "time<='"
        query_string += list_value[index]['end_time']
        query_string += "')"
        if index < len(list_value) - 1:
            query_string += ' or '

    query_string += """ Group by logs.url Order BY count Desc"""
    return query_string


def responses(data, is_get_total=False):
    total = data.get('total')
    if is_get_total:
        return {
            'total': total
        }
    if total:
        del data['total']
    __data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    response = {}
    response['total'] = total
    response['data'] = [{key: val} for key, val in __data.items()]
    return response
