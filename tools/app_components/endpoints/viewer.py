from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import db, app
from tools.sql.table import Topics, History

from tools.topics_cash_supervisor import check_topic_existence
from tools.utilities import get_current_date, increment_threads_count


@app.route(APP_CONFIG.GLOBAL["API_root"] + 'viewer', methods=['GET'])
@increment_threads_count
def table_viewer():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    start_millis = get_current_date()["date_timespamp"]

    table = request.args.get('table')
    topic = request.args.get('topic')
    start_history_capture = request.args.get('start_history_capture')
    end_history_capture = request.args.get('end_history_capture')
    parse_arg = request.args.get('parse')

    # Try parse history capture point
    if start_history_capture is not None:
        try:
            start_history_capture = int(start_history_capture)
        except KeyError as err:
            print(f"ERROR - parse start_history_capture: {err}")
            return jsonify(status="topic's viewer doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]

    if end_history_capture is not None:
        try:
            end_history_capture = int(end_history_capture)
        except KeyError as err:
            print(f"ERROR - parse end_history_capture: {err}")
            return jsonify(status="topic's viewer doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]

    if table is None:
        return jsonify(status="Error table parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    try:
        # 2 possibilities: extract history table | topics table
        json_extraction = []

        # extract history table
        if table.lower() == "history":
            if topic is not None:
                topic = topic.replace("$", "/")
                extraction = extract_history_table_from_topic(
                    topic,
                    start_history_capture, end_history_capture
                )
            else:
                extraction = extract_history_table()

            json_extraction = sql_to_json(extraction, History)

        # extract topics table
        elif table.lower() == "topics":
            if topic is not None:
                topic = topic.replace("$", "/")

            extraction = extract_topics_table(topic)
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
        print(f"ERROR - table_viewer: {err}")
        return jsonify(status="topic's viewer doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]


def extract_history_table_from_topic(topic, start, end):
    topic_check_result = check_topic_existence(db.session, topic)

    # If it exists
    if topic_check_result["exist"]:
        # 2 cases:
        # from 0 to end_history_capture
        # from start_history_capture to end_history_capture

        # from 0 to end_history_capture
        if start is None and end is not None:
            return db.session.query(History).filter(getattr(History, "topic") == topic).order_by(
                getattr(History, "timestamp").desc()).limit(end).all()
        # from start_history_capture to end_history_capture
        elif start is not None and end is not None:
            return db.session.query(History).filter(getattr(History, "topic") == topic).order_by(
                getattr(History, "timestamp").desc()).offset(start).limit(end).all()

        else:
            return db.session.query(History).filter(getattr(History, "topic") == topic).order_by(
                getattr(History, "timestamp").desc()).all()


def extract_history_table():
    return db.session.query(History).order_by(getattr(History, "timestamp").desc()).all()


def extract_topics_table(topic=None):
    if topic is None:
        return db.session.query(Topics).all()
    else:
        return db.session.query(Topics).filter(getattr(Topics, "topic") == topic).all()


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
