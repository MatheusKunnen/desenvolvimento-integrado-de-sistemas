from flask import Flask
from gevent.pywsgi import WSGIServer

from src.config import LocalConfig
from src.db import Database
from src.manager import JobManager

from .JobView import JobView
from .AnalyticsView import AnalyticsView

class ApiServer:
    __FlaskApp = None
    
    def __init__(self, jobs_db: Database, analytics_db: Database, job_m: JobManager):
        self.__jobs_db = jobs_db
        self.__analytics_db = analytics_db
        self.__job_m = job_m

        if ApiServer.__FlaskApp is None:
            ApiServer.__FlaskApp = Flask('ApiServer')

        self.__app = ApiServer.__FlaskApp

        JobView.register(self.__app, route_base='/job', init_argument=(self.__jobs_db, self.__job_m, ...) )
        AnalyticsView.register(self.__app, route_base='/analytics', init_argument=(self.__analytics_db, ...) )

    def run(self):
        port = LocalConfig.GetDefault().getApiPort()
        http_server = WSGIServer(('0.0.0.0', port), self.__app, log=None)
        print(f'Server started at http://localhost:{port}')
        http_server.serve_forever()
    
