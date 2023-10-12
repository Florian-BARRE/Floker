from flask import jsonify, request

from configuration import APP_CONFIG
from tools.sql import app
from tools.utilities import get_current_date

from tools.app_components.endpoints.read import read_task
from tools.app_components.endpoints.write import write_task

from tools.utilities import increment_threads_count


@app.route(APP_CONFIG.GLOBAL["API_root"] + 'multi', methods=['POST'])
@increment_threads_count
def multi_task():
    if APP_CONFIG.TOKEN != request.args.get('token'):
        return jsonify(status="Error auth", state=None), APP_CONFIG.CODE_ERROR["unauthorize"]

    start_millis = get_current_date()["date_timespamp"]

    parse_arg = request.args.get('parse')
    json_requests = request.get_json()

    if json_requests is None or len(json_requests) == 0:
        return jsonify(status="Error json request parameter is missing"), APP_CONFIG.CODE_ERROR["missing_parameter"]

    try:
        requests_response = []

        for index, json_request in enumerate(json_requests):
            response = "error"
            type = json_request.get("type", None)

            if type is None:
                return jsonify(status="Type of under request not valid !"), APP_CONFIG.CODE_ERROR["crash"]
            # Read
            elif type.lower() == "read":
                topic = json_request.get("topic", None)

                if topic is None:
                    return jsonify(status=f"Under request number '{index}' of type 'READ': no topic presence."), \
                           APP_CONFIG.CODE_ERROR["crash"]

                parse = json_request.get("parse", None)
                previous_state_index = json_request.get("previous_state_index", None)

                response = read_task(topic, parse_arg=parse, previous_state_index=previous_state_index)
            # Write
            elif type.lower() == "write":
                topic = json_request.get("topic", None)
                state = json_request.get("state", "null")

                if topic is None:
                    return jsonify(status=f"Under request number '{index}' of type 'WRITE': no topic presence."), \
                           APP_CONFIG.CODE_ERROR["crash"]

                response = write_task(topic, state)

            elif type.lower() == "delete":
                # TODO: muti request for delete
                pass
            elif type.lower() == "history_size":
                # TODO: muti request for history_size
                pass
            elif type.lower() == "viewer":
                # TODO: muti request for viewer
                pass
            elif type.lower() == "history_length":
                # TODO: history_length request for viewer
                pass

            # Add response to array
            http_code = APP_CONFIG.CODE_ERROR["crash"]
            data = "null"

            try:
                http_code = response[0].status_code
                data = response[0].json
            except:
                http_code = response[1]
                data = response[0]


            requests_response.append(
                {
                    "http_code": http_code,
                    "data": data
                }
            )

        final_json = jsonify(
            status="topic's viewer works successfully",
            length=len(requests_response),
            extraction_duration=get_current_date()["date_timespamp"] - start_millis,
            response=requests_response
        )

        if parse_arg is not None:
            return str(final_json.json[parse_arg]), APP_CONFIG.CODE_ERROR["successfully_request"]
        else:
            return final_json, APP_CONFIG.CODE_ERROR["successfully_request"]

    except KeyError as err:
        print(f"ERROR - multi: {err}")
        return jsonify(status="Multi request doesn't work, an error occured"), APP_CONFIG.CODE_ERROR["crash"]
