import loguru
from flask import Flask, request
from utils.redis import get_celery_redis_data, push_redis_data, get_cache_query_data, get_list_result, \
    responses
from utils.config import RESPONSE_STATUS, MISS_DATA, FAILURE, SUCCESS, REDIS_QUERY_KEY, get_new_domains_query_string
from utils.log_model import LogModel, UpdateLogModel, ListLogModel, QueryModel
from tasks import delete_log as delete_log_worker, get_top_domain
from tasks import create_log as create_log_worker
from tasks import update_log as update_log_worker
from tasks import create_logs as create_logs_worker
from flask_swagger_ui import get_swaggerui_blueprint
from tasks import update_logs as update_logs_worker
from tasks import delete_logs as delete_logs_worker

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "List API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route('/log', methods=['POST'])
def create_log():
    log = LogModel(request)
    if not log.url:
        return RESPONSE_STATUS[MISS_DATA]

    task = create_log_worker.delay(log.to_json())

    if RESPONSE_STATUS[FAILURE] in task.get():
        return RESPONSE_STATUS[FAILURE]

    return RESPONSE_STATUS[SUCCESS]


# create
# {
#     "url":"ditimsohoc.com"
# }

# update
# {
#     "id":"378417",
#     "new_log":{
#         "id":"378419",
#         "url":"hohohohooh.com",
#         "time":"2022-12-17 14:56:28.99999"
#     }
# }

# delete {
#     "id":"378419"
# }

@app.route('/log', methods=['PUT'])
def update_log():
    log = UpdateLogModel(request)
    if not (log.id or log.new_log):
        return RESPONSE_STATUS[MISS_DATA]

    task = update_log_worker.delay(log.to_json())

    if RESPONSE_STATUS[FAILURE] in task.get():
        return RESPONSE_STATUS[FAILURE]

    return RESPONSE_STATUS[SUCCESS]


@app.route('/log', methods=['DELETE'])
def delete_log():
    log = LogModel(request)
    if not log.id:
        return RESPONSE_STATUS[MISS_DATA]

    task = delete_log_worker.delay(log.to_json())

    if RESPONSE_STATUS[FAILURE] in task.get():
        return RESPONSE_STATUS[FAILURE]

    return RESPONSE_STATUS[SUCCESS]


# list

# create
# {
#     "logs": [
#         {
#             "url": "33333.xxxx"
#         },
#         {
#             "url": "44444.xxxx"
#         }
#     ]
# }

@app.route('/logs', methods=['POST'])
def create_logs():
    logs = ListLogModel(request).logs
    if not logs:
        return RESPONSE_STATUS[MISS_DATA]
    task = create_logs_worker.delay(logs)
    response = get_celery_redis_data(task.id)
    if not response:
        loguru.logger.error(f"Error :{RESPONSE_STATUS[MISS_DATA]}")
        return RESPONSE_STATUS[FAILURE]
    response_status = response.get("result")

    return response_status


# update
# {
#     "logs": [
#         {
#             "id": "378422",
#             "new_log": {
#                 "id": "378429",
#                 "url": "s1.com",
#                 "time": "2022-11-17 14:26:28.99999"
#             }
#         },
#         {
#             "id": "378423",
#             "new_log": {
#                 "id": "378441",
#                 "url": "s2.com",
#                 "time": "2021-12-17 00:56:28.000"
#             }
#         }
#     ]
# }

@app.route('/logs', methods=['PUT'])
def update_logs():
    logs = ListLogModel(request).logs
    if not logs:
        return RESPONSE_STATUS[MISS_DATA]
    task = update_logs_worker.delay(logs)
    response = get_celery_redis_data(task.id)
    if not response:
        loguru.logger.error(f"Error :{RESPONSE_STATUS[MISS_DATA]}")
        return RESPONSE_STATUS[FAILURE]

    response_status = response.get("result")
    return response_status


# delete
# {
#     "logs": [
#         {
#             "id": "378427",
#             "url": "23213213213213.xxxx"
#         },
#         {
#
#             "url": "44444444444444444.xxxx"
#         }
#     ]
# }
@app.route('/logs', methods=['DELETE'])
def delete_logs():
    logs = ListLogModel(request).logs
    if not logs:
        return RESPONSE_STATUS[MISS_DATA]
    task = delete_logs_worker.delay(logs)
    response = get_celery_redis_data(task.id)
    if not response:
        loguru.logger.error(f"Error :{RESPONSE_STATUS[MISS_DATA]}")
        return RESPONSE_STATUS[FAILURE]

    response_status = response.get("result")
    return response_status


# {
#     "time_by_the_hour": 222
#
# }

@app.route('/get-top-domains', methods=['GET'])
def top_domain_logs():
    query = QueryModel(request)
    time_by_the_hour = query.time_by_the_hour
    if not (time_by_the_hour or time_by_the_hour.isnumeric()):
        return RESPONSE_STATUS[MISS_DATA]
    cache_data = get_cache_query_data(REDIS_QUERY_KEY, query)

    response = []
    if cache_data.get('data'):
        response.append({'response': cache_data['data']})

    if cache_data.get('query_string'):
        task = get_top_domain.delay(cache_data['query_string'], None, None)
        celery_result_data = get_celery_redis_data(task.id).get("result", RESPONSE_STATUS[MISS_DATA])
        response.append({'response': celery_result_data})
        response = get_list_result(response, 'response')
        response['total'] = len(response) if not response.get('total') else len(response) - 1

        push_redis_data(REDIS_QUERY_KEY, {
            'time_by_the_hour': time_by_the_hour,
            'response': response,
            'start_time': query.start_time,
            'end_time': query.end_time
        })
    return responses(response)


# {
#     "time_by_the_hour": 222
#
# }

@app.route('/get-new-domains', methods=['GET'])
def get_new_domains():
    query = QueryModel(request)
    time_by_the_hour = query.time_by_the_hour
    if not (time_by_the_hour or str(time_by_the_hour).isnumeric()):
        return RESPONSE_STATUS[MISS_DATA]

    response = []
    task = get_top_domain.delay(get_new_domains_query_string(query.start_time), None, None)
    celery_result_data = get_celery_redis_data(task.id).get("result", RESPONSE_STATUS[MISS_DATA])
    response.append({'response': celery_result_data})
    response = get_list_result(response, 'response')
    response['total'] = len(response) if not response.get('total') else len(response) - 1

    return responses(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
