import os
import json
import numpy as np
from math import sqrt, floor

from io import BytesIO
from PIL import Image
from datetime import datetime
from multiprocessing import Queue

from src.algorithms import CGNRAlgorithm
class Worker:
    def __init__(self, id:int, input_queue:Queue, output_queue:Queue):
        self.__id = id
        self.__pid = os.getpid()
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.__models = [None, None]

    def run(self):
        self.print('Started...')
        while True:
            try:
                job = self.__input_queue.get()
                
                output = self.executeJob(job)

                self.__output_queue.put(output)
            except Exception as e:
                self.print(f'Error: {e}')
        self.print('Finished...')

    def executeJob(self, job):
        self.print(f'Starting job {job["job_id"]}')
        try:
            H = self.getModel(job["model"])
            job["started_at"] = datetime.now()

            algo = CGNRAlgorithm(H)
            
            signal = self.getSignal(job["signal"])
            
            output, it, error  = algo.processSignal(signal)

            image, image_bytes = self.outputToImage(output)

            job["image"] = image_bytes
            job["finished_at"] = datetime.now()
            
            # DEBUG
            image.save(f'./img/{job["job_id"]}.png', format="png")

            self.print(f'Job {job["job_id"]} finished')

            return dict({
                'job_id': job["job_id"],
                'iterations_at': it,
                'started_at': job["started_at"],
                'finished_at': job["finished_at"],
                'image': job["image"]
            })
        except Exception as e:
            self.print(f'Job {job["job_id"]} FAILED')
            raise e
        
    def getSignal(self, raw_signal: bytes):
        data = json.loads(raw_signal.decode('utf-8'))
        signal = np.array(data, dtype=np.float64)
        signal.shape = (signal.shape[0], 1)
        return signal
    
    def outputToImage(self, image_arr: np.array):
        img_size = floor(sqrt(image_arr.shape[1]))
        print(img_size, sqrt(image_arr.shape[1]), image_arr.shape[1], image_arr.shape)
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
        if self.__models[model] is None:
            self.__models[model] = np.loadtxt(f'./data/H-{int(model+1)}.csv', delimiter=',', dtype=np.float64)

        return self.__models[model]
        
    def print(self, msg):
        print(f'[{self.__pid}] Worker {self.__id}:', msg)     


