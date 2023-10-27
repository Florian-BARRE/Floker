import re
from os import cpu_count
from sqlalchemy import select

from configuration import APP_CONFIG
from tools.sql.table import Topics, History
from tools.utilities import get_current_date

from tools.history_size_cash_supervisor import get_history_size
from tools.topics_cash_supervisor import check_topic_existence


def history_size_regulator_routine(db):
    try:
        # Get all topics to supervise. Topics source: from topics cash / from MySQL
        # If we use Topic cash only topics in, have changed => just supervise them
        # For the first supervisor running all topics are regulated
        if not APP_CONFIG.ENABLE_TOPICS_CASH or not APP_CONFIG.GLOBAL["supervisor_running"]:
            all_topics_sql = db.session.query(Topics).all()
            all_topics = dict()
            for row in all_topics_sql:
                all_topics[row.topic] = {
                    "history_size": row.history_size,
                    "current_history_size": get_history_size(session=db.session, topic=row.topic,
                                                             add_if_not_exist=False)
                }

        else:
            all_topics = dict()
            a = APP_CONFIG.GLOBAL["history_size_cash"]
            for topic, current_history_size in APP_CONFIG.GLOBAL["history_size_cash"].items():
                all_topics[topic] = {
                    "history_size": check_topic_existence(db.session, topic, add_if_not_exist=True)["history_size"],
                    "current_history_size": current_history_size
                }

        cpt_deleted_rows = 0
        for topic in all_topics:
            history_size = all_topics[topic].get("history_size", -1)
            current_history_size = all_topics[topic].get("current_history_size", None)

            if history_size != -1 and current_history_size is not None and current_history_size > history_size:
                cpt_deleted_rows += current_history_size - history_size
                items_to_delete = db.session.query(History.id).filter(
                    getattr(History, "topic") == topic).order_by(getattr(History, "timestamp").desc()).offset(
                    history_size).subquery()
                db.session.query(History).filter(History.id.in_(select(items_to_delete))).delete(
                    synchronize_session='fetch')
                db.session.commit()
                APP_CONFIG.GLOBAL["history_size_cash"][topic] = history_size

        return (
            f"#-> {get_current_date()['date']} - History size regulator routine was successfully executed.",
            f"#--> OUTPUT: \033[92m{cpt_deleted_rows} rows deleted.\033[0m",
            ""
        )


    except KeyError as err:
        return f"ERROR - history_size_regulator_routine: {err}"


def threads_counter_routine(last_call, count):
    try:
        APP_CONFIG.GLOBAL["current_period_threads_opened"] = 0
        last_call_delta = get_current_date()["date_timespamp"] - last_call
        return (
            f"#-> {get_current_date()['date']} - Threads counter supervisor routine was successfully executed.",
            f"#--> OUTPUT: \033[92m{count}"
            f" were completed in {last_call_delta}s.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - threads_counter_routine: {err}"


def threads_timer_routine(duration, count):
    try:
        APP_CONFIG.GLOBAL["current_total_execution_duration_of_threads"] = 0
        average = duration / count if count != 0 and count is not None else 0
        return (
            f"#-> {get_current_date()['date']} - Threads timer supervisor routine was successfully executed.",
            f"#--> OUTPUT: \033[92mtotal work duration {duration}s,"
            f" the average thread duration is {average}.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - threads_timer_routine: {err}"


def requests_counter_routine(last_call):
    try:
        last_call_delta = get_current_date()["date_timespamp"] - last_call
        nb_requests = APP_CONFIG.GLOBAL['requests_counter']
        APP_CONFIG.GLOBAL['requests_counter'] = 0
        return (
            f"#-> {get_current_date()['date']} - Requests counter routine was successfully executed.",
            f"#--> OUTPUT: \033[92mthere were {nb_requests} requests running in the last {last_call_delta}s.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - requests_counter_routine: {err}"


def requests_exceeded_routine():
    try:
        return (
            f"#-> {get_current_date()['date']} - Requests exeeded routine was successfully executed.",
            f"#--> OUTPUT: \033[92mthere were actually {APP_CONFIG.GLOBAL['dynamic_requests_counter']}"
            f" requests which are in queue.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - requests_exceeded_routine: {err}"


def threads_available_routine():
    try:
        return (
            f"#-> {get_current_date()['date']} - Threads available routine was successfully executed.",
            f"#--> OUTPUT: \033[92m{cpu_count()} threads"
            f" are available on this machine.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - threads_available_routine: {err}"


def topics_cash_counter_routine():
    try:
        return (
            f"#-> {get_current_date()['date']} - Topics cash counter routine was successfully executed.",
            f"#--> OUTPUT: \033[92mthere are actually {len(APP_CONFIG.GLOBAL['topics_cash'].keys())} topics in the cash.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - topics_cash_counter_routine: {err}"


def history_size_cash_counter_routine():
    try:
        return (
            f"#-> {get_current_date()['date']} - History size cash counter routine was successfully executed.",
            f"#--> OUTPUT: \033[92mthere are actually {len(APP_CONFIG.GLOBAL['history_size_cash'].keys())} topics in the cash.\033[0m",
            ""
        )

    except KeyError as err:
        return f"ERROR - history_size_cash_counter_routine: {err}"


def summary_routine(*args):
    def _ansi_length(s):
        return len(re.sub(r'\033\[[0-9;]*[mK]', '', str(s)))

    args_length = []
    for arg in args:
        if type(arg) is type(tuple()):
            args_length.extend(_ansi_length(under_arg) for under_arg in arg)
        else:
            args_length.append(_ansi_length(arg))

    max_length = max(args_length)
    table_width = max_length + 4

    print('+' + '-' * table_width + '+')
    for arg in args:
        if type(arg) is type(tuple()):
            for under_arg in arg:
                print(f'|  {str(under_arg)} {" " * (max_length - _ansi_length(under_arg))} |')
        else:
            print(f'|  {str(arg)} {" " * (max_length - _ansi_length(arg))} |')

    print('+' + '-' * table_width + '+')


def supervisor(app, db):
    last_routine = get_current_date()["date_timespamp"]

    with app.app_context():
        while True:
            if (get_current_date()["date_timespamp"] - last_routine) > APP_CONFIG.GLOBAL["supervisor_routine_wait"]:
                threads_count = APP_CONFIG.GLOBAL["current_period_threads_opened"]
                work_duration = APP_CONFIG.GLOBAL["current_total_execution_duration_of_threads"]
                summary_routine(
                    history_size_regulator_routine(db),
                    threads_counter_routine(last_routine, threads_count),
                    threads_timer_routine(work_duration, threads_count),
                    requests_counter_routine(last_routine),
                    requests_exceeded_routine(),
                    topics_cash_counter_routine(),
                    history_size_cash_counter_routine(),
                    threads_available_routine(),
                )

                last_routine = get_current_date()["date_timespamp"]
                APP_CONFIG.GLOBAL["supervisor_running"] = True
