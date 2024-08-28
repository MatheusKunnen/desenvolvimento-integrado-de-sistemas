import os
import json
import math

class LocalConfig:
    __DefaultInstance = None

    def __init__(self, config_file:str = 'config.json'):
        self.__config_file = config_file
        self.__config_data = dict({})
        self.load_config()

    def load_config(self):
        f = None
        try:
            f = open(self.__config_file)
            data = json.load(f)
            self.__config_data = data
        except Exception as e:
            print(e)
        finally:
            if f is not None:
                f.close()

    def getJobsDbPath(self):
        return self.get('jobs_db', 'sqlite:///data/jobs.sqlite')
    
    def getAnalyticsDbPath(self):
        return self.get('jobs_db', 'sqlite:///data/analytics.sqlite')
    
    def getAnalyticsRowsLimit(self):
        return self.get('analytics_rows_limit', 600)

    def getApiPort(self):
        return self.get('api_port', 5005)

    def getMaxError(self):
        return self.get('max_error', 1e-6)
    
    def getModelClearTimeout(self):
        return self.get('model_clear_timeout', 0.5)
    
    def getModelMaxError(self):
        return self.get('model_max_error', 1e-6)
    
    def getMaxModelWorkers(self):
        return self.get('max_model_workers', math.floor(os.cpu_count()*0.8))
    
    def getAnalyticsPollingTime(self):
        return self.get('analytics_polling_time', 1)
    
    def getAnalyticsVerbose(self):
        return self.get('analytics_verbose', False)
    
    def getClientFolderPath(self):
        return self.get('client_folder_path', './client')
    
    def get(self, key:str, default):
        if self.__config_data.get(key) is None:
            return default
        return self.__config_data.get(key)    

    @staticmethod
    def SetDefault(Instance):
        LocalConfig.__DefaultInstance = Instance

    @staticmethod
    def GetDefault():
        if LocalConfig.__DefaultInstance is None:
            raise RuntimeError('No default instance of LocalConfig')
        return LocalConfig.__DefaultInstance
