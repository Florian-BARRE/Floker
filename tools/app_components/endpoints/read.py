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
        history_size = topic_check_result["history_size"]

        # If it exists
        if topic_check_result["exist"]:
            # Take the state, last state or state index which was asked
            if previous_state_index is None:
                index = 0
            else:
                try:
                    previous_state_index = int(previous_state_index)
                except KeyError as err:
                    print(f"ERROR - parse previous_state_index: {err}")
                    return jsonify(status="topic's reader doesn't work, an error occured"), APP_CONFIG.CODE_ERROR[
                        "crash"]

                nb_rows = db.session.query(History).filter(getattr(History, "topic") == topic).count()
                index = min(previous_state_index, history_size, nb_rows - 1)

            # Get the state
            row = db.session.query(History).filter(getattr(History, "topic") == topic).order_by(
                getattr(History, "timestamp").desc()).offset(index).limit(index + 1)[0]
            state = row.state
            timestamp = row.timestamp
            date = row.date

            if state is None:
                state = "null"

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
