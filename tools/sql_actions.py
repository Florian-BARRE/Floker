from configuration import APP_CONFIG
from tools.sql.table import Topics, History
from tools.utilities import get_current_date


def add_topic(session, topic, default_value=None,
              default_history_size=APP_CONFIG.GLOBAL["default_history_size"]) -> bool:
    success = False
    try:
        date = get_current_date()
        # Add the new topic in general topics table
        session.add(
            Topics(
                topic=topic,
                history_size=default_history_size
            )
        )
        # Add a row concern the topic in the history
        session.add(
            History(
                topic=topic,
                state=default_value,
                date=date["date"],
                timestamp=date["date_timespamp"],
            )
        )
        session.commit()

        success = True
    except KeyError as err:
        print(f"ERROR - add_topic: {err}")

    return success
