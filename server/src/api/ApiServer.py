from flask import Flask
from gevent.pywsgi import WSGIServer

from src.db import Database
from src.manager import JobManager

from .JobView import JobView

class ApiServer:
    __FlaskApp = None
    
    def __init__(self, db: Database, job_m: JobManager):
        self.__db = db
        self.__job_m = job_m

        if ApiServer.__FlaskApp is None:
            ApiServer.__FlaskApp = Flask('ApiServer')

        self.__app = ApiServer.__FlaskApp

        JobView.register(self.__app, route_base='/job', init_argument=(self.__db, self.__job_m, ...) )

    def run(self):
        http_server = WSGIServer(('0.0.0.0', 5005), self.__app)
        http_server.serve_forever()
        # self.__app.run(port=5005, debug=True)
    
