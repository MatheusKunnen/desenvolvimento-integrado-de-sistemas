from .api.ApiServer import ApiServer
from .db import Database
from .models.Job import JobBase
from .models.AppInfo import AnalyticsBase

from .manager.JobManager import JobManager
class Server: 
    def __init__(self):
        self.__jobs_db = Database('sqlite:///teste.sqlite')
        self.__analytics_db = Database('sqlite:///analytics.sqlite')

        JobBase.metadata.create_all(self.__jobs_db.getEngine())
        AnalyticsBase.metadata.create_all(self.__analytics_db.getEngine())

        self.__job_manager = JobManager(self.__jobs_db, self.__analytics_db)
        self.__http_server = ApiServer(self.__jobs_db, self.__analytics_db, self.__job_manager)

    def run(self):
        self.__http_server.run()
        print("Running server")