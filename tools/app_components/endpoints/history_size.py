from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics
from tools.sql_actions import add_topic

from tools.utilities import increment_threads_count

@app.route(APP_CONFIG.GLOBAL["API_root"] + 'history_size', methods=['GET'])
@increment_threads_count
def change_history_size():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')
    size = request.args.get('size')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    elif size is None or size == "" or int(size) < 0:
        return jsonify(status="Error new history size is incorrect"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")

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
