import os
import json
import gc
import numpy as np
from math import sqrt, floor

from io import BytesIO
from PIL import Image
from datetime import datetime
from multiprocessing import Queue, Event

from src.algorithms import CGNRAlgorithm

class Worker:
    def __init__(self, id:int, input_queue:Queue, output_queue:Queue, event, models_timeout_s: int = 0.25, max_error=1e-6):
        self.__id = id
        self.__pid = os.getpid()
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.__event = event
        self.__models_timeout_s = models_timeout_s
        self.__max_error = max_error
        self.__models = [None, None]
        self.__gain_models = [None, None]

    def run(self):
        self.print('Running...')
        while self.__event.is_set():
            try:
                job = self.__input_queue.get(timeout=self.__models_timeout_s)
                
                output = self.executeJob(job)

                self.__output_queue.put(output)
                gc.collect()
            except Exception as e:
                if self.__input_queue.empty():
                    pass
                #     if self.isModelLoaded():
                #         self.print('Queue empty, clearing models')
                #         self.__models = [None, None]
                #         self.__gain_models = [None, None]
                #         gc.collect()
                else:
                    self.print(f'Error: {e}')
        
        self.__models = [None, None]
        self.__gain_models = [None, None]
        gc.collect()
        
        self.__event.set()
        self.print('Terminated...')
        exit(0)

    def executeJob(self, job):
        self.print(f'Starting job {job["job_id"]}')
        try:
            H = self.getModel(job["model"])
            job["started_at"] = datetime.now()

            algo = CGNRAlgorithm(H, max_error=self.__max_error)
            
            signal = self.getSignal(job["signal"])

            if job["use_gain"]:
                signal = self.applyGainToSignal(signal, job["model"])
            
            output, it, error  = algo.processSignal(signal)

            image, image_bytes = self.outputToImage(output)

            job["image"] = image_bytes
            job["finished_at"] = datetime.now()
            job["total_time_ms"] = round((job["finished_at"] - job["started_at"]).total_seconds()*1000)

            # DEBUG
            image.save(f'./img/{job["job_id"]}.png', format="png")

            self.print(f'Job {job["job_id"]} finished in {job["total_time_ms"]}ms with {it} iterations')

            return dict({
                'job_id': job["job_id"],
                'iterations_at': it,
                'started_at': job["started_at"],
                'finished_at': job["finished_at"],
                'image': job["image"],
                'total_time_ms': job["total_time_ms"]
            })
        except Exception as e:
            self.print(f'Job {job["job_id"]} FAILED')
            print(e)
            raise e
        
    def getSignal(self, raw_signal: bytes):
        data = json.loads(raw_signal.decode('utf-8'))
        signal = np.array(data, dtype=np.float64)
        signal.shape = (signal.shape[0], 1)
        return signal
    
    def applyGainToSignal(self, signal, model:int):
        gain = self.getGainModel(model)
        return np.multiply(signal, gain)
    
    def outputToImage(self, image_arr: np.array):
        img_size = floor(sqrt(image_arr.shape[1]))

        image_arr *= 255
        image_arr = np.reshape(image_arr, (img_size, img_size), order="F")
        
        img = Image.fromarray(image_arr)
        img = img.convert('L')

        bytesio = BytesIO()
        img.save(bytesio, format="png")

        return img, bytesio.getvalue()

    def getModel(self, model: int):
        if model != 1 and model != 2:
            raise ValueError(f'Model {model} is not implemented')
        model -= 1
        try:
            if self.__models[model] is None:
                self.__models = [None, None]
                self.__models[model] = np.load(f'./data/H-{int(model+1)}.npy')
        except:
            self.print(f'WARNING: Binary file for gain model {model+1} not found. Using slow CSV version.')
            if self.__models[model] is None:
                self.__models[model] = np.loadtxt(f'./data/H-{int(model+1)}.csv', delimiter=',', dtype=np.float64)

        return self.__models[model]
    
    def getGainModel(self, model: int):
        if model != 1 and model != 2:
            raise ValueError(f'Model {model} is not implemented')
        model -= 1
        try:
            if self.__gain_models[model] is None:
                self.__gain_models = [None, None]
                self.__gain_models[model] = np.load(f'./data/gain-model-{int(model+1)}.npy')
        except:
            self.print(f'WARNING: Cached file for gain model {model+1} not found. Generating gain...')
            self.__gain_models[model] = self.__genGainSignal(model+1)

        return self.__gain_models[model]
    
    def __genGainSignal(self, model:int):
        N = 64
        S = 436 if model == 2 else 794

        signal = np.ones(shape=(S*N, 1), dtype=np.float64)
        
        for l in range(S):
            for c in range(N):
                gain = 100 + (1 / 20) * (c + 1) * np.sqrt(c + 1)
                signal[l*N + c] *=  gain
        
        return signal
    
    def isModelLoaded(self):
        return self.__models[0] is not None or self.__models[1] is not None
        
    def print(self, msg):
        print(f'[{self.__pid}] W{self.__id}:', msg)     


