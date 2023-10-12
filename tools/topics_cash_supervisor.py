from configuration import APP_CONFIG

from tools.sql.table import Topics
from tools.sql_actions import add_topic


def check_topic_existence(session, topic, add_if_not_exist=True, default_state=None, default_history_size=None):
    # Get topic
    topic_result = None

    if APP_CONFIG.ENABLE_TOPICS_CASH and APP_CONFIG.GLOBAL["topics_cash"].get(topic, None) is not None:
        topic_result = {"exist": True, "history_size": APP_CONFIG.GLOBAL["topics_cash"].get(topic)}
    else:
        topics_table_result = session.query(Topics).filter(getattr(Topics, "topic") == topic).all()
        if len(topics_table_result) == 1:
            topic_result = {"exist": True, "history_size": topics_table_result[0].history_size}

            if APP_CONFIG.ENABLE_TOPICS_CASH:
                add_topic_in_cash(rows=topics_table_result)

        elif len(topics_table_result) > 1:
            print(f"To many {topic}, what is the matter ?")
            topic_result = {"exist": False, "history_size": -1}

    # If no topic found
    if topic_result is None:
        if add_if_not_exist:
            # Add missing topic in the topics table
            call_add_topic(session, topic, default_value=default_state, default_history_size=default_history_size)
            topics_table_result = session.query(Topics).filter(getattr(Topics, "topic") == topic).all()
            # Add missing topic in cash
            if APP_CONFIG.ENABLE_TOPICS_CASH:
                add_topic_in_cash(topics_table_result)

            topic_result = {"exist": True, "history_size": topics_table_result[0].history_size}
        else:
            topic_result = {"exist": False, "history_size": -1}

    return topic_result

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


def call_add_topic(session, topic, default_value=None, default_history_size=None):
    if default_value is None and default_history_size is None:
        add_topic(session, topic)
    elif default_value is not None and default_history_size is None:
        add_topic(session, topic, default_value=default_value)
    elif default_value is None and default_history_size is not None:
        add_topic(session, topic, default_history_size=default_history_size)
    else:
        add_topic(session, topic, default_value=default_value, default_history_size=default_history_size)
