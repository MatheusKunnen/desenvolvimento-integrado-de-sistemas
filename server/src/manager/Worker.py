import os
from multiprocessing import Queue

class Worker:
    def __init__(self, id:int, input_queue:Queue, output_queue:Queue):
        self.__id = id
        self.__pid = os.getpid()
        self.__input_queue = input_queue
        self.__output_queue = output_queue

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
        self.print(f'Starting job {job.job_id}')
        try:
            pass
        except Exception as e:
            self.print(f'Job {job.job_id} FAILED')
            raise e
        
    def print(self, msg:str):
        print(f'[{self.__pid}] Worker {self.__id}: {msg}')     


