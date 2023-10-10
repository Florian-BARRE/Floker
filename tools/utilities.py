from functools import wraps

from configuration import APP_CONFIG


def get_current_date():
    from datetime import datetime
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
