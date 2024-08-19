import os
import json
import numpy as np
from io import BytesIO
from datetime import datetime
from multiprocessing import Queue

from src.algorithms import CGNRAlgorithm
class Worker:
    def __init__(self, id:int, input_queue:Queue, output_queue:Queue):
        self.__id = id
        self.__pid = os.getpid()
        self.__input_queue = input_queue
        self.__output_queue = output_queue
        self.__H = None

    def run(self):
        self.print('Running...')
        while True:
            try:
                job = self.__input_queue.get()
                
                output = self.executeJob(job)

                self.__output_queue.put(output)
            except Exception as e:
                self.print(f'Error: {e}')

    def executeJob(self, job):
        self.print(f'Starting job {job["job_id"]}')
        try:
            self.loadModel(job["model"])
            job["started_at"] = datetime.now()

            algo = CGNRAlgorithm(self.__H)
            
            data = json.loads(job["signal"].decode('utf-8'))
            signal = np.array(data, dtype=np.float64)
            signal.shape = (signal.shape[0], 1)
            
            img,it  = algo.processSignal(signal)

            bytesio = BytesIO()

            img.save(bytesio, format="png")

            job["image"] = bytesio.getvalue()
            job["finished_at"] = datetime.now()
            
            img.save(f'./img/{job["job_id"]}.png', format="png")

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
        
    def loadModel(self, model: int):
        # print("Model: ", model)
        if self.__H is None:
            self.__H = np.loadtxt('./data/H-2.csv', delimiter=',', dtype=np.float64)
            self.__H = np.asarray(self.__H, dtype=np.float64)

        
    def print(self, msg):
        print(f'[{self.__pid}] Worker {self.__id}:', msg)     


