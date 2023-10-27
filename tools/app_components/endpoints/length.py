from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import History

from tools.topics_cash_supervisor import check_topic_existence
from tools.utilities import increment_threads_count
from tools.history_size_cash_supervisor import get_history_size

@app.route(APP_CONFIG.GLOBAL["API_root"] + 'history_length', methods=['GET'])
@increment_threads_count
def get_topic_history_length():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    topic = request.args.get('topic')

    if topic is None:
        return jsonify(status="Error topic parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    topic = topic.replace("$", "/")

    try:
        topic_check_result = check_topic_existence(db.session, topic, add_if_not_exist=False)

        # If it exists
        if topic_check_result["exist"]:
            # Get the length of topic's history
            length = get_history_size(db.session, topic, add_if_not_exist=False)
            return jsonify(status="Topic length getter works successfully", length=length), APP_CONFIG.CODE_ERROR[
                "successfully_request"]

        else:
            return jsonify(status="Topic doesn't exist"), APP_CONFIG.CODE_ERROR[
                "successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="Topic length getter doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]
