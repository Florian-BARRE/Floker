from configuration import APP_CONFIG

from tools.sql.table import Topics
from tools.sql_actions import add_topic


def check_topic_existence(session, topic, add_if_not_exist=True, default_state=None):
    if APP_CONFIG.ENABLE_TOPICS_CASH:
        # Check in cash if topic is available
        if APP_CONFIG.GLOBAL["topics_cash"].get(topic, None) is None:
            topics_table_result = session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

            # If it exists
            if len(topics_table_result) == 1:
                output = (1, add_topic_in_cash(rows=topics_table_result))

            # If it doesn't exist
            elif len(topics_table_result) == 0 and add_if_not_exist:
                if default_state is not None:
                    add_topic(session, topic, default_value=default_state)
                else:
                    add_topic(session, topic)
                output = (1, add_topic_in_cash(topic=topic, size=APP_CONFIG.GLOBAL["default_history_size"]))

            # If there is more than 1 topic -> Error
            else:
                print(f"To many {topic}, what is the matter ?")
                output = 0
        else:
            output = (1, APP_CONFIG.GLOBAL["topics_cash"].get(topic))

    else:
        topics_table_result = session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

        # If it exists
        if len(topics_table_result) == 1:
            output = (1, topics_table_result[0].history_size)

        # If it doesn't exist
        elif len(topics_table_result) == 0 and add_if_not_exist:
            add_topic(session, topic)
            output = (1, topics_table_result[0].history_size)

        # If there is more than 1 topic -> Error
        else:
            print(f"To many {topic}, what is the matter ?")
            output = 0

    return output


def add_topic_in_cash(rows=None, topic=None, size=None):
    if rows is None:
        APP_CONFIG.GLOBAL["topics_cash"][topic] = size
        return size
    else:
        APP_CONFIG.GLOBAL["topics_cash"][rows[0].topic] = rows[0].history_size
        return rows[0].history_size

def delete_topic_in_cash(topic):
    if APP_CONFIG.ENABLE_TOPICS_CASH:
        APP_CONFIG.GLOBAL["topics_cash"].pop(topic, None)
