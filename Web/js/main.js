addEventListener('load', (event) => { 
    create_table(DATA_TABLE_ID, 1, HISTORY_TEMPLATE.length);
    create_table(GENERAL_INFO_TABLE_ID, 1, GENERAL_INFOS_TEMPLATE.length);

    handle_supervisor();
    setInterval(handle_supervisor, REFRESH_WAIT);
})


async function handle_supervisor(){
    switch (GLOBAL["display_data"] || DEFAULT_DISPLAY_DATA) {
        case 'history':
            handle_display_history_table();
            break;
        case 'topics':
            handle_display_topics_table();
            break;
        default:
            console.log('Unknown display data');
            break;
    }
  
}

async function handle_display_history_table(){
    switch (GLOBAL["display_mode"] || DEFAULT_DISPLAY_MODE) {
        case 'all':
            display_history_table();
            break;
        case 'dynamic':
            display_dynamic_history();
            break;
        default:
            console.log('Unknown display mode');
            break;
    }
}

async function handle_display_topics_table() {
    switch (GLOBAL["display_mode"] || DEFAULT_DISPLAY_MODE) {
        case 'all':
            display_topics_table();
            break;
        case 'dynamic':
            display_dynamic_topics();
            break;
        default:
            console.log('Unknown display mode');
            break;
    }
}