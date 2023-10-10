import re
from os import cpu_count
from sqlalchemy import select

from configuration import APP_CONFIG
from tools.sql.table import Topics, History
from tools.utilities import get_current_date


def history_size_regulator_routine(db):
    try:
        all_topics = db.session.query(Topics).filter(getattr(Topics, "id") >= 0).all()
        cpt_deleted_rows = 0

        for topic in all_topics:
            items_to_delete = db.session.query(History.id).filter(
                getattr(History, "topic") == topic.topic).order_by(getattr(History, "timestamp").desc()).offset(
                topic.history_size).subquery()
            db.session.query(History).filter(History.id.in_(select(items_to_delete))).delete(
                synchronize_session='fetch')
            cpt_deleted_rows = db.session.query(items_to_delete).count()

            db.session.commit()

        return (
            f"#-> {get_current_date()['date']} - History size regulator routine was successfully executed.",
            f"#--> OUTPUT: \033[92m{cpt_deleted_rows}\033[0m rows deleted.",
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
            f"#--> OUTPUT: \033[92m{count}\033[0m"
            f" were completed in \033[92m{last_call_delta}\033[0m.",
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
            f"#--> OUTPUT: total work duration \033[92m{duration}\033[0m,"
            f" the average thread duration is \033[92m{average}\033[0m).",
            ""
        )

    except KeyError as err:
        return f"ERROR - threads_timer_routine: {err}"


def threads_available_routine():
    try:
        return (
            f"#-> {get_current_date()['date']} - Threads available routine was successfully executed.",
            f"#--> OUTPUT: \033[92m{cpu_count()} threads\033[0m"
            f" are available on this machine."
        )

    except KeyError as err:
        return f"ERROR - threads_available_routine: {err}"


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
                    threads_available_routine()
                )

                last_routine = get_current_date()["date_timespamp"]
