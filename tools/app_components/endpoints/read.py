from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import History

from tools.topics_cash_supervisor import check_topic_existence
from tools.utilities import get_current_date, increment_threads_count


@app.route(APP_CONFIG.GLOBAL["API_root"] + 'read', methods=['GET'])
@increment_threads_count
def read_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]
    topic = request.args.get('topic')
    parse_arg = request.args.get('parse')
    previous_state_index = request.args.get('previous_state_index')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")
    return read_task(topic, parse_arg=parse_arg, previous_state_index=previous_state_index)


def read_task(topic, parse_arg=None, previous_state_index=None):
    try:
        topic_check_result = check_topic_existence(db.session, topic)

        # If it exists
        if topic_check_result[0] == 1:
            # Check in history the topic's state
            history_topic_result = db.session.query(History).filter(
                getattr(History, "topic") == topic).order_by(getattr(History, "timestamp").desc()).all()

            # Get topic's history size in general topics
            history_size = topic_check_result[1]

            # Take the state, last state or state index which was asked
            if previous_state_index is None:
                state = history_topic_result[0].state
                timestamp = history_topic_result[0].timestamp
                date = history_topic_result[0].date

            elif int(previous_state_index) >= len(history_topic_result):
                state = history_topic_result[-1].state
                timestamp = history_topic_result[-1].timestamp
                date = history_topic_result[-1].date

            else:
                state = history_topic_result[int(previous_state_index)].state
                timestamp = history_topic_result[int(previous_state_index)].timestamp
                date = history_topic_result[int(previous_state_index)].date
            if state is None:
                state = "null"

        elif topic_check_result[0] == 0:
            state = "null"
            timestamp = get_current_date()["date_timespamp"]
            date = get_current_date()["date"]
            history_size = APP_CONFIG.GLOBAL["default_history_size"]

        else:
            print(f"To many {topic}, what is the matter ?")

        if parse_arg is not None:
            return \
                jsonify(status="topic's reader works successfully", state=state, timestamp=str(timestamp), date=date,
                        history_size=str(history_size)).json[
                    parse_arg], APP_CONFIG.CODE_ERROR["successfully_request"]
        else:
            return jsonify(status="topic's reader works successfully", state=state, timestamp=timestamp, date=date,
                           history_size=history_size), \
                   APP_CONFIG.CODE_ERROR[
                       "successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="topic's reader doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]
