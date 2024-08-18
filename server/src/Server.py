from .api.ApiServer import ApiServer
from .db import Database
from .models.Job import JobBase

class Server: 
    def __init__(self):
        self.__db = Database('sqlite:///teste.sqlite')
        self.__http_server = ApiServer(self.__db)
        JobBase.metadata.create_all(self.__db.getEngine())

    def run(self):
        self.__http_server.run()
        print("Running server")