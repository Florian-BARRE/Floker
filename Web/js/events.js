// History viewer (view all states updated)
function history_viewer_call() {
    console.log("topics_viewer_call");
    GLOBAL["display_data"] = "history";
    handle_supervisor();
}


// Topics viewer (view all topics and history size)
function topics_viewer_call() {
    console.log("topics_viewer_call");
    GLOBAL["display_data"] = "topics";
    handle_supervisor();
}

// Display all data (const and dynamics value)
function display_mode_all_call(){
    console.log("display_mode_all_call");
    GLOBAL["display_mode"] = "all";
    handle_supervisor();
}

// Display only dynamic data (dynamics value)
function display_mode_dynamic_call() {
    console.log("display_mode_dynamic_call");
    GLOBAL["display_mode"] = "dynamic";
    handle_supervisor();
}