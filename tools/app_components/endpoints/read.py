from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History
from tools.sql_actions import add_topic


@app.route('/api/read', methods=['GET'])
def read_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]
    topic = request.args.get('topic')
    parse_arg = request.args.get('parse')
    previous_state_index = request.args.get('previous_state_index')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")

    try:
        # Check is the topic exist in the general topics table
        general_topic_result = db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

        # If it exists
        if len(general_topic_result) == 1:
            # Check in history the topic's state
            history_topic_result = db.session.query(History).filter(
                getattr(History, "topic") == topic).order_by(getattr(History, "timestamp").desc()).all()

            # Get topic's history size in general topics
            history_size = general_topic_result[0].history_size

            # Take the state, last state or state index which was asked
            if previous_state_index is None:
                state = history_topic_result[0].state

            elif int(previous_state_index) > len(history_topic_result):
                state = history_topic_result[-1].state
            else:
                state = history_topic_result[int(previous_state_index)].state
            if state is None:
                state = "null"


        elif len(general_topic_result) == 0:
            # Add the new topic
            add_topic(db.session, topic)
            state = "null"
            history_size = APP_CONFIG.GLOBAL["default_history_size"]

        else:
            print(f"To many {topic}, what is the matter ?")

        if parse_arg is not None:
            return \
                jsonify(status="topic's reader works successfully", state=state, history_size=str(history_size)).json[
                    parse_arg], APP_CONFIG.CODE_ERROR["successfully_request"]
        else:
            return jsonify(status="topic's reader works successfully", state=state, history_size=history_size), \
                   APP_CONFIG.CODE_ERROR[
                       "successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="topic's reader doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]