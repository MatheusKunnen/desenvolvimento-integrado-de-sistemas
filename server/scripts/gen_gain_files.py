import numpy as np
import pickle

def getGainVec(model:int):
        N = 64
        S = 436 if model == 2 else 794

        signal = np.ones(shape=(S*N, 1), dtype=np.float64)
        
        for l in range(S):
            for c in range(N):
                gain = 100 + (1 / 20) * (c + 1) * np.sqrt(c + 1)
                # print(l, c)
                signal[l*N + c] *=  gain
        
        return signal

BASE_PATH = '../data/'
if __name__ == '__main__':
    model_1_gain = getGainVec(1)
    model_2_gain = getGainVec(2)

    models = [model_1_gain, model_2_gain]
    for i,model in enumerate(models):
         file_path = BASE_PATH + f'gain-model-{i+1}'
         print(f'Saving gain model {model.shape} in {file_path}')
         np.save(file=file_path, arr=model)