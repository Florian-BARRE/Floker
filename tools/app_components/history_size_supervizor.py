from time import sleep

from configuration import APP_CONFIG
from tools.sql.table import Topics, History
from tools.utilities import get_current_date


def routine(db):
    try:
        all_topics = db.session.query(Topics).filter(getattr(Topics, "id") >= 0).all()

        for topic in all_topics:
            history_size = topic.history_size

            topic_values = db.session.query(History).filter(
                getattr(History, "topic") == topic.topic).order_by(getattr(History, "timestamp").desc()).all()

            # Check if the history size is over that the limit
            if len(topic_values) > history_size:
                # remove excess rows
                for excess_row in topic_values[history_size:]:
                    db.session.delete(excess_row)

                db.session.commit()

    except KeyError as err:
        print(f"ERROR - start_history_size_supervisor: {err}")


def start_history_size_supervisor(app, db):
    last_routine = get_current_date()["date_timespamp"]
    with app.app_context():
        while True:
            if (get_current_date()["date_timespamp"] - last_routine) > APP_CONFIG.GLOBAL["supervisor_routine_wait"]:
                last_routine = get_current_date()["date_timespamp"]
                routine(db)
            else:
                sleep(5)
