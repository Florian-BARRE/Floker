from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History

from tools.topics_cash_supervisor import check_topic_existence, delete_topic_in_cash
from tools.utilities import increment_threads_count


@app.route(APP_CONFIG.GLOBAL["API_root"] + 'delete', methods=['GET'])
@increment_threads_count
def delete_topic():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")

    try:

        topic_check_result = check_topic_existence(db.session, topic)

        # If it exists
        if topic_check_result[0] == 1:
            # Delete history topic rows
            to_delete = db.session.query(History).filter(getattr(History, "topic") == topic)
            to_delete.delete(synchronize_session='fetch')

            # Delete topic row
            to_delete = db.session.query(Topics).filter(getattr(Topics, "topic") == topic)
            to_delete.delete(synchronize_session='fetch')

            db.session.commit()

            # Delete the topic from the cash
            delete_topic_in_cash(topic)

        # If doesn t exist
        elif topic_check_result[0] == 0:
            return jsonify(status="topic doesn't exist"), APP_CONFIG.CODE_ERROR["successfully_request"]

        # If there is to many topics create an error
        else:
            print(f"To many {topic}, what is the matter ?")

        return jsonify(status="topic's delete work successfully"), APP_CONFIG.CODE_ERROR["successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="topic's delete doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]
