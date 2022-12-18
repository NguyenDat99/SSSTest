import datetime

from loguru import logger
from sqlalchemy import select, delete

from utils.config import RESPONSE_STATUS, FAILURE, SUCCESS, TIME_FORMAT, MISS_DATA
from utils.celery import celery_worker, celery_logger
from utils.database import SessionLocal, Log
from sqlalchemy.orm import Session

database: Session = SessionLocal()


@celery_worker.task
def create_log(logs):
    try:
        celery_logger.info('Starting create_log')
        if not logs.get('url'):
            return RESPONSE_STATUS[FAILURE]
        if logs.get('id') and database.execute(select(Log).filter(Log.id == logs.get('id'))).first():
            return RESPONSE_STATUS[FAILURE]
        log = Log(
            id=logs.get('id'),
            url=logs['url'],
            time=str(datetime.datetime.now().strftime(TIME_FORMAT))
        )
        database.add(log)
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return RESPONSE_STATUS[SUCCESS]


@celery_worker.task
def update_log(logs):
    celery_logger.info('Starting create_log')
    new_log = logs.get('new_log')
    try:
        old_log = database.query(Log).filter(Log.id == logs['id']).first()
        if new_log.get('id'):
            old_log.id = new_log['id']
        if new_log.get('time'):
            old_log.time = new_log['time']
        if new_log.get('url'):
            old_log.url = new_log['url']
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()

    celery_logger.info('Done !')
    return RESPONSE_STATUS[SUCCESS]


@celery_worker.task
def delete_log(logs):
    try:
        celery_logger.info('Starting create_log')
        if not database.execute(select(Log).filter(Log.id == logs['id'])).first():
            return RESPONSE_STATUS[FAILURE]
        database.execute(delete(Log).where(Log.id == logs['id']))
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return RESPONSE_STATUS[SUCCESS]


# list

@celery_worker.task
def create_logs(logs):
    try:
        celery_logger.info('Starting create_logs')
        exist_ids = [log.id for log in database.execute(
            select(Log).filter(Log.id.in_([log['id'] for log in logs if log.get('id')]))).scalars().all()]
        new_logs = []
        error = []
        for index in range(0, len(logs)):
            if not logs[index].get('url'):
                error.append(RESPONSE_STATUS[MISS_DATA])
            if logs[index].get('id') and logs[index]['id'] in exist_ids:
                error.append(RESPONSE_STATUS[FAILURE])
            else:
                new_logs.append(Log(
                    id=logs[index].get('id'),
                    url=logs[index]['url'],
                    time=str(datetime.datetime.now().strftime(TIME_FORMAT))
                ))
                error.append(RESPONSE_STATUS[SUCCESS])
        database.bulk_save_objects(new_logs)
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return error


@celery_worker.task
def update_logs(logs):
    try:
        celery_logger.info('Starting update_logs')
        old_logs = {str(log.id): log for log in database.execute(
            select(Log).filter(Log.id.in_([log['id'] for log in logs if log.get('id')]))).scalars().all()}

        error = []
        for index in range(0, len(logs)):
            if not logs[index].get('id'):
                error.append(RESPONSE_STATUS[MISS_DATA])
            if logs[index].get('id') and not old_logs.get(logs[index].get('id')):
                error.append(RESPONSE_STATUS[FAILURE])
            if logs[index].get('id') and old_logs.get(logs[index].get('id')):
                new_logs = logs[index].get('new_log')
                if not new_logs:
                    error.append(RESPONSE_STATUS[MISS_DATA])
                else:
                    if new_logs.get('id'):
                        old_logs[logs[index].get('id')].id = new_logs.get('id')
                    if new_logs.get('url'):
                        old_logs[logs[index].get('id')].url = new_logs.get('url')
                    if new_logs.get('time'):
                        old_logs[logs[index].get('id')].time = new_logs.get('time')
                    error.append(RESPONSE_STATUS[SUCCESS])

        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return error


@celery_worker.task
def delete_logs(logs):
    celery_logger.info('Starting create_log')
    error = []
    ids = []
    try:
        for log in logs:
            if not str(log.get('id')).isnumeric():
                error.append(RESPONSE_STATUS[MISS_DATA])
            else:
                ids.append(log['id'])
        if not ids:
            return error
        database.execute(delete(Log).where(Log.id.in_(ids)))
        error.append(RESPONSE_STATUS[SUCCESS])
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return error


@celery_worker.task
def push_tracking_data(logs):
    try:
        celery_logger.info('Starting push_tracking_data')
        log = Log(
            time=logs['datetime'],
            url=logs['url']
        )
        database.add(log)
        database.commit()
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return RESPONSE_STATUS[SUCCESS]


@celery_worker.task
def get_top_domain(query_string=None, start_time=None, end_time=None):
    try:
        celery_logger.info('Starting push_tracking_data')
        if not query_string:
            query_string = f""" select logs.url, count(1) as count from logs where time>='{start_time}' and time <='{end_time}'
                            Group by logs.url
                            Order BY count Desc"""

        logs = database.execute(query_string)
        response = {}
        for log in logs:
            response[log.url] = log.count
        response['total'] = len(response)
    except Exception as e:
        logger.error(f"error: {e}")
        return RESPONSE_STATUS[FAILURE]
    finally:
        database.close()
    celery_logger.info('Done !')
    return response

