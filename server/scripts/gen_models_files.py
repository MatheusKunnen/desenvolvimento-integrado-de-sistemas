import numpy as np
from datetime import datetime

BASE_PATH = '../data/'
MODELS = ['H-1', 'H-2']

def getModel(model:str):
    return np.loadtxt(f'{BASE_PATH}{model}.csv', delimiter=',', dtype=np.float64)
    # return np.load(f'{BASE_PATH}{model}.npy')

if __name__ == '__main__':
    for model in MODELS:
         file_path = BASE_PATH + model
         start = datetime.now()
         print(f'Converting model {model}')
         model_mat = getModel(model)
         print(f'Model {model_mat.shape}')
         stop = datetime.now()
         delta = stop - start
         np.save(file=file_path, arr=model_mat)
         print(f'Processing time {model} {round(delta.total_seconds()*1000)}ms')
