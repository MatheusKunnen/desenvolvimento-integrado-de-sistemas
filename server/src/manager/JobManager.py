from multiprocessing import Process, Queue
from .Worker import Worker

def worker_entry(id, input_q, output_q):
    w = Worker(id, input_q, output_q)
    w.run()

class JobManager:
    
    def __init__(self, jobs_db):
        self.__jobs_db = jobs_db

        self.__n_workers = 4
        self.__processes = []

        self.__jobs_queue = Queue()
        self.__results_queue = Queue()
        
        self.__initWorkers()

    def __initWorkers(self):
        for i in range(self.__n_workers):
            p = Process(target=worker_entry, args=(i, self.__jobs_queue, self.__results_queue), daemon=True)
            self.__processes.append(p)
        
        for p in self.__processes:
            p.start()