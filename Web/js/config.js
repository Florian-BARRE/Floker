const API_TOKEN = "rbFHGxhhv7LEVQ264XALk763eBVtqy68k6i3Lt8Pj4HtG9neQu"
const BASE_URL = "https://floker.flo-machines.dynv6.net/api/viewer?token=" + API_TOKEN + "&table="
const TOPICS_TABLE = "topics"
const HISTORY_TABLE = "history"

const TOPICS_VIEWER_URL = BASE_URL + TOPICS_TABLE
const HISTORY_VIEWER_URL = BASE_URL + HISTORY_TABLE

const REFRESH_WAIT = 500;
const DATA_TABLE_ID = "main_table";
const GENERAL_INFO_TABLE_ID = "general_info_table";

const DEFAULT_DISPLAY_DATA = "history";
const DEFAULT_DISPLAY_MODE = "all";

var GLOBAL = {}; 

var DISPLAY_STATE_CPT = 4;

const TOPICS_TEMPLATE = ["topic", "history_size"];
const HISTORY_TEMPLATE = ["topic", "state", "timestamp", "date"];
const GENERAL_INFOS_TEMPLATE = ["Size", "Speed"];
const PERFORMANCE_INFOS_TEMPLATE = ["Speed", "Status"];