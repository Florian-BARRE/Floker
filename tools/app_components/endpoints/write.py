from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import History

from tools.topics_cash_supervisor import check_topic_existence
from tools.utilities import get_current_date, increment_threads_count


@app.route(APP_CONFIG.GLOBAL["API_root"] + 'write', methods=['GET'])
@increment_threads_count
def write_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')
    state = request.args.get('state')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")

    return write_task(topic, state)


def write_task(topic, state):
    msg = "topic's writer doesn't work, an error occured"

    try:
        topic_check_result = check_topic_existence(db.session, topic, add_if_not_exist=True, default_state=state)

        # If it exists
        if topic_check_result[0] == 1:
            # Check in history the state
            date = get_current_date()
            db.session.add(
                History(
                    topic=topic,
                    state=state,
                    date=date["date"],
                    timestamp=date["date_timespamp"]
                )
            )
            db.session.commit()

        # If there is to many topics create an error
        elif topic_check_result[0] > 1:
            print(f"To many {topic}, what is the matter ?")

        msg = "topic's writer works successfully"

    except KeyError as err:
        print(f"ERROR - write_topic: {err}")
        return jsonify(status=msg), APP_CONFIG.CODE_ERROR["crash"]

    if topic is not None:
        return jsonify(status=msg), APP_CONFIG.CODE_ERROR["successfully_request"]

    else:
        return jsonify(status="Error missing parameter"), APP_CONFIG.CODE_ERROR["missing_parameter"]
