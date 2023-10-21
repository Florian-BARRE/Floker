from datetime import datetime
from functools import wraps
from flask import g

from tools.sql import app

from configuration import APP_CONFIG


def get_current_date():
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    return {
        "date": now,
        "date_timespamp": timestamp
    }


def increment_threads_count(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        start_time = get_current_date()["date_timespamp"]
        result = function(*args, **kwargs)
        APP_CONFIG.GLOBAL["current_total_execution_duration_of_threads"] += get_current_date()[
                                                                                "date_timespamp"] - start_time
        APP_CONFIG.GLOBAL["current_period_threads_opened"] += 1
        return result

    return decorated_function


@app.before_request
def increment_request_counter():
    APP_CONFIG.GLOBAL["requests_counter"] += 1
    APP_CONFIG.GLOBAL["dynamic_requests_counter"] += 1
    g.request_counted = True


@app.teardown_request
def decrement_request_counter(exception=None):
    if getattr(g, 'request_counted', False):
        APP_CONFIG.GLOBAL["dynamic_requests_counter"] -= 1
