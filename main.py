from threading import Thread
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher


from tools.app_components.history_size_supervizor import start_history_size_supervisor
from tools.sql import app, db
from configuration import APP_CONFIG

if __name__ == '__main__':
    Thread(target=start_history_size_supervisor, args=(app, db)).start()

    with app.app_context():
        if APP_CONFIG.SERVER_MODE == "debug_server":
            app.run(host='0.0.0.0', port=APP_CONFIG.GLOBAL["listen_port"], debug=True)

        elif APP_CONFIG.SERVER_MODE == "cherrypy_server":
            server = WSGIServer(('0.0.0.0', APP_CONFIG.GLOBAL["listen_port"]), PathInfoDispatcher({'/': app}))
            server.maxthreads = -1 # No max thread
            try:
                server.start()
            except KeyboardInterrupt:
                server.stop()
        else:
            print("ERROR - Select a correct server mode")
