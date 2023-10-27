from configuration import APP_CONFIG

from tools.sql.table import History
from tools.topics_cash_supervisor import check_topic_existence


def update_history_size_cash(session, topic, rows_to_add=None, add_to_cash_if_not_exist=True):
    if APP_CONFIG.ENABLE_HISTORY_SIZE_CASH and APP_CONFIG.GLOBAL["history_size_cash"].get(topic,
                                                                                          None) is None and add_to_cash_if_not_exist and \
            check_topic_existence(session, topic, add_if_not_exist=False)["exist"]:
        add_history_size_in_cash(session, topic)
        if rows_to_add is not None:
            increment_history_size(topic, rows_to_add)


def add_history_size_in_cash(session, topic):
    # Use this function ONLY after ENABLE_HISTORY_SIZE_CASH verification
    current_history_size = session.query(History).filter(getattr(History, "topic") == topic).count()
    APP_CONFIG.GLOBAL["history_size_cash"][topic] = current_history_size


def increment_history_size(topic, increment):
    APP_CONFIG.GLOBAL["history_size_cash"][topic] += increment


def get_history_size(session, topic, add_if_not_exist=True):
    if not check_topic_existence(session, topic, add_if_not_exist=add_if_not_exist)["exist"]:
        return None
    update_history_size_cash(session, topic, add_to_cash_if_not_exist=add_if_not_exist)

    if APP_CONFIG.ENABLE_HISTORY_SIZE_CASH:
        cash_history_size = APP_CONFIG.GLOBAL["history_size_cash"].get(topic, None)

        return session.query(History).filter(
            getattr(History, "topic") == topic).count() if cash_history_size is None else cash_history_size


def delete_history_size_in_cash(topic):
    if APP_CONFIG.ENABLE_HISTORY_SIZE_CASH:
        APP_CONFIG.GLOBAL["history_size_cash"].pop(topic, None)
