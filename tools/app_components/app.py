from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History
from tools.sql_actions import add_topic
from tools.utilities import get_current_date


@app.route('/api/write', methods=['GET'])
def write_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]
    msg = "topic's writer doesn't work, an error occured"

    topic = request.args.get('topic')
    topic = topic.replace("$", "/")
    state = request.args.get('state')
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

    if topic is not None and state is not None:
        return jsonify(status=msg), APP_CONFIG.CODE_ERROR["successfully_request"]

    else:
        return jsonify(status="Error missing parameter"), APP_CONFIG.CODE_ERROR["missing_parameter"]


@app.route('/api/read', methods=['GET'])
def read_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]
    topic = request.args.get('topic')
    topic = topic.replace("$", "/")
    parse_arg = request.args.get('parse')
    previous_state_index = request.args.get('previous_state_index')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

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


@app.route('/api/delete', methods=['GET'])
def delete_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')
    topic = topic.replace("$", "/")

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    try:
        # Check is the topic exist in the general topics table
        general_topic_result = db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

        # If it exists
        if len(general_topic_result) == 1:
            # Check in history the topic's state
            history_topic_result = db.session.query(History).filter(
                getattr(History, "topic") == topic).order_by(getattr(History, "timestamp").desc()).all()

            # Delete all rows
            for row in history_topic_result:
                db.session.delete(row)

            # Delete topic row
            db.session.delete(general_topic_result[0])

            db.session.commit()

        # If doesn t exist
        elif len(general_topic_result) == 0:
            return jsonify(status="topic doesn't exist"), APP_CONFIG.CODE_ERROR["successfully_request"]

        # If there is to many topics create an error
        else:
            print(f"To many {topic}, what is the matter ?")

        return jsonify(status="topic's delete work successfully"), APP_CONFIG.CODE_ERROR["successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="topic's delete doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]


@app.route('/api/history_size', methods=['GET'])
def change_history_size():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')
    topic = topic.replace("$", "/")
    size = request.args.get('size')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    elif size is None or size == "" or int(size) < 0:
        return jsonify(status="Error new history size is incorrect"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    try:
        # Check is the topic exist in the general topics table
        general_topic_result = db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

        # If it exists
        if len(general_topic_result) == 1:
            # Change history size
            general_topic_result[0].history_size = size
            db.session.commit()

        # If doesn t exist
        elif len(general_topic_result) == 0:
            # Add the new topic
            add_topic(db.session, topic, default_history_size=size)

        # If there is to many topics create an error
        else:
            print(f"To many {topic}, what is the matter ?")

        return jsonify(status="history size changer work successfully"), APP_CONFIG.CODE_ERROR["successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="History size changer doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]
