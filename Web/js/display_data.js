//##### Display raw table #####
async function display_topics_table(){
    let data = await get_topics();
    let extract = data["extraction"];

    update_nb_rows(DATA_TABLE_ID, data["length"], TOPICS_TEMPLATE.length);

    for (let l = 0; l < data["length"]; l++){
        row_values = [];
        for (let key in TOPICS_TEMPLATE) 
            row_values.push(extract[l][TOPICS_TEMPLATE[key]]);

        set_row(DATA_TABLE_ID, l, row_values);
    }    

    general_info_update([data["length"]]);
}

async function display_history_table() {
    let data = await get_history();
    let extract = data["extraction"];
    
    update_nb_rows(DATA_TABLE_ID, data["length"], HISTORY_TEMPLATE.length);

    for (let l = 0; l < data["length"]; l++) {
        row_values = [];
        for (let key in HISTORY_TEMPLATE)
            row_values.push(extract[l][HISTORY_TEMPLATE[key]]);

        set_row(DATA_TABLE_ID, l, row_values);
    }    
}

//##### Display dynamics table #####
async function display_dynamic_topics() {
    let data_history = await get_last_value_of_each_topic();
    hide_const_state(data_history);

    let data_topics = await get_topics();
    let data_topics_extract = data_topics["extraction"];

    update_nb_rows(DATA_TABLE_ID, get_nb_dynamics_states(), TOPICS_TEMPLATE.length);
   
    let row_index = 0;
    for (let l = 0; l < data_topics_extract.length; l++) {
        let row = data_topics_extract[l];
        if (GLOBAL["store_display_value_of_topic"][row.topic]["display"]) {
            let row_values = [];
            for (let k = 0; k < TOPICS_TEMPLATE.length; k++){
               
                row_values.push(row[TOPICS_TEMPLATE[k]]);
            }
            set_row(DATA_TABLE_ID, row_index, row_values)
            row_index++;
        }
    }
 
}

async function display_dynamic_history(){
    let data_history = await get_last_value_of_each_topic();
    hide_const_state(data_history);

    update_nb_rows(DATA_TABLE_ID, get_nb_dynamics_states(), HISTORY_TEMPLATE.length);

    let row_index = 0;
    for (let topic in data_history) {
        if (GLOBAL["store_display_value_of_topic"][topic]["display"]) {
            let row_values = [topic];
            for (let k=1; k<HISTORY_TEMPLATE.length; k++)
                row_values.push(data_history[topic][HISTORY_TEMPLATE[k]]);
            
            set_row(DATA_TABLE_ID, row_index, row_values)
            row_index++;
        }
    }

    document.getElementById("size").innerHTML = size;
}