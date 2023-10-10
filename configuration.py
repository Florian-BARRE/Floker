import json
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SECRET_FILE_PATH = 'secrets.json'
SECRET_CONFIG_STORE = {}

try:
    with open(SECRET_FILE_PATH) as config:
        SECRET_CONFIG_STORE = json.load(config)
except FileNotFoundError:
    try:
        with open(os.path.join(BASE_DIR, 'secrets.json')) as config:
            SECRET_CONFIG_STORE = json.load(config)
    except Exception:
        raise


class Config:
    # General
    APPLICATION_NAME = 'Floker'
    BASE_DIR = BASE_DIR
    GLOBAL = {
        "listen_port": 5000,
        "API_root": "/api/",
        "default_history_size": 50,
        "supervisor_routine_wait": 5,
        "current_period_threads_opened": 0,
        "current_total_execution_duration_of_threads": 0
    }
    CODE_ERROR = {
        "successfully_request": 200,
        "unauthorize": 401,
        "missing_parameter": 400,
        "crash": 500
    }

    # Run Mode
    SERVER_MODE = "cherrypy_server"  # debug_server | cherrypy_server
    DATABASE_MODE = SECRET_CONFIG_STORE["database_mode"]
    TOKEN = SECRET_CONFIG_STORE["token"]

    if DATABASE_MODE == "local":
        FLOKER_CONN_STR = f'sqlite:///{os.path.join(BASE_DIR, "databases", "floker.db")}'
    else:
        FLOKER_CONN_STR = SECRET_CONFIG_STORE["floker_conn_str"]


class Configuration(dict):

    def from_object(self, obj):
        for attr in dir(obj):

            if not attr.isupper():
                continue

            self[attr] = getattr(obj, attr)

        self.__dict__ = self


APP_CONFIG = Configuration()
APP_CONFIG.from_object(Config)
