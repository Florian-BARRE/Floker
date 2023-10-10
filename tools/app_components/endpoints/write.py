from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History
from tools.sql_actions import add_topic

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
        # Check is the topic exist in the general topics table
        general_topic_result = db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

        # If it exists
        if len(general_topic_result) == 1:
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

        # If doesn t exist
        elif len(general_topic_result) == 0:
            # Add the new topic
            add_topic(db.session, topic, default_value=state)

        # If there is to many topics create an error
        else:
            print(f"To many {topic}, what is the matter ?")

        msg = "topic's writer works successfully"

    except KeyError as err:
        print(f"ERROR - write_topic: {err}")
        return jsonify(status=msg), APP_CONFIG.CODE_ERROR["crash"]

    if topic is not None:
        return jsonify(status=msg), APP_CONFIG.CODE_ERROR["successfully_request"]

    else:
        return jsonify(status="Error missing parameter"), APP_CONFIG.CODE_ERROR["missing_parameter"]
