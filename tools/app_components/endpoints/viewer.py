from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History
from tools.sql_actions import add_topic
from tools.utilities import get_current_date


@app.route('/api/viewer', methods=['GET'])
def table_viewer():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    start_millis = get_current_date()["date_timespamp"]

    table = request.args.get('table')
    topic = request.args.get('topic')
    history_size = request.args.get('history_size')
    parse_arg = request.args.get('parse')

    if table is None:
        return jsonify(status="Error table parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    try:
        # 2 possibilities: extract history table | topics table
        json_extraction = []

        # extract history table
        if table.lower() == "history":
            if topic is not None:
                topic = topic.replace("$", "/")
                extraction = extract_history_table_from_topic(topic, history_size)
            else:
                extraction = extract_history_table()

            json_extraction = sql_to_json(extraction, History)

        # extract topics table
        elif table.lower() == "topics":
            extraction = extract_topics_table()
            json_extraction = sql_to_json(extraction, Topics)

        # Prepare the final json
        final_json = jsonify(
            status="topic's viewer works successfully",
            length=len(json_extraction),
            extraction_duration=get_current_date()["date_timespamp"] - start_millis,
            extraction=json_extraction
        )

        if parse_arg is not None:
            return str(final_json.json[parse_arg]), APP_CONFIG.CODE_ERROR["successfully_request"]
        else:
            return final_json, APP_CONFIG.CODE_ERROR["successfully_request"]

    except KeyError as err:
        print(f"ERROR - read_topic: {err}")
        return jsonify(status="topic's reader doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]


def extract_history_table_from_topic(topic, history_size):
    # Check is the topic exist in the general topics table
    general_topic_result = db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()

    # If it exists
    if len(general_topic_result) == 1:
        history_topic_results = db.session.query(History).filter(
            getattr(History, "topic") == topic).order_by(getattr(History, "timestamp").desc()).all()

        if history_size is not None and history_size >= 0:
            return history_topic_results[:history_size]

        return history_topic_results

    elif len(general_topic_result) == 0:
        # Add the new topic
        add_topic(db.session, topic)
        return extract_history_table_from_topic(topic, history_size)

    else:
        print(f"To many {topic}, what is the matter ?")
        return []


def extract_history_table():
    return db.session.query(History).order_by(getattr(History, "timestamp").desc()).all()


def extract_topics_table():
    return db.session.query(Topics).all()


def sql_to_json(extraction: object, table: object) -> object:
    # sourcery skip: dict-comprehension, dict-literal
    # Get table column
    columns = [col.name for col in table.__table__.columns]

    json_extraction = []
    for row in extraction:
        json_row = dict()
        for column in columns:
            json_row[column] = getattr(row, column)

        json_extraction.append(json_row)
    return json_extraction