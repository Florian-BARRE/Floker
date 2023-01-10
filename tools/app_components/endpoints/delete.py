from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History


@app.route('/api/delete', methods=['GET'])
def delete_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')

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
