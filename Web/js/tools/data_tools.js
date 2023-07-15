function hide_const_state(dict) {
    if (GLOBAL["store_display_value_of_topic"] === undefined) { GLOBAL["store_display_value_of_topic"] = {}; }

    if (GLOBAL["store_last_value_of_each_topic"] !== undefined) {

        for (let topic in dict) {
            // If new topic -> init display state 
            if (GLOBAL["store_display_value_of_topic"][topic] === undefined) {
                GLOBAL["store_display_value_of_topic"][topic] = {
                    "cpt": 0,
                    "display": true
                }
            }
            // If no update (last timestamp == new timestamp)
            else if (GLOBAL["store_last_value_of_each_topic"][topic]["timestamp"] === dict[topic]["timestamp"]) {
                GLOBAL["store_display_value_of_topic"][topic]["cpt"]++;

                if (GLOBAL["store_display_value_of_topic"][topic]["cpt"] > DISPLAY_STATE_CPT) {
                    GLOBAL["store_display_value_of_topic"][topic]["display"] = false;
                }
            }
            // If update (last timestamp != new timestamp)
            else {
                GLOBAL["store_display_value_of_topic"][topic]["cpt"] = 0;
                GLOBAL["store_display_value_of_topic"][topic]["display"] = true;
            }
        }
    }
    // Update last states
    GLOBAL["store_last_value_of_each_topic"] = dict;
}

function get_nb_dynamics_states() {
    let cpt = 0;

    for (let topic in GLOBAL["store_display_value_of_topic"])
        cpt += GLOBAL["store_display_value_of_topic"][topic]["display"];

    return cpt;
}


async function get_last_value_of_each_topic() {
    let history = await get_history();

    let last_value_dict = {};

    for (let k = 0; k < history["length"]; k++) {
        let current_item = history["extraction"][k];
        let current_topic = current_item["topic"];

        if (last_value_dict[current_topic] === undefined) {
            state = current_item["state"];
            if (state == null) state = "null";

            last_value_dict[current_topic] = {
                "id": current_item["id"],
                "timestamp": current_item["timestamp"],
                "date": current_item["date"],
                "state": state
            };
        }
        else if (current_item["timestamp"] > last_value_dict[current_topic]["timestamp"]) {
            state = current_item["state"];
            if (state == null) state = "null";

            last_value_dict[current_topic] = {
                "id": current_item["id"],
                "timestamp": current_item["timestamp"],
                "date": current_item["date"],
                "state": state
            };
        }
    }

    return last_value_dict;
}


