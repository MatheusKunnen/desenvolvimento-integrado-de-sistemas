import json

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
    
    def getSignalsFolderPath(self):
        return self.get('signals_folder_path', './signals')
    
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
