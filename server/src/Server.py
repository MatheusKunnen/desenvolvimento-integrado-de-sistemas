from .api.ApiServer import ApiServer
from .db import Database
from .models.Job import JobBase
from .manager.JobManager import JobManager
class Server: 
    def __init__(self):
        self.__db = Database('sqlite:///teste.sqlite')
        self.__job_manager = JobManager(self.__db)
        self.__http_server = ApiServer(self.__db, self.__job_manager)
        JobBase.metadata.create_all(self.__db.getEngine())

    def run(self):
        self.__http_server.run()
        print("Running server")