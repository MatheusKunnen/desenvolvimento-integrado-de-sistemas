import numpy as np

class CGNRAlgorithm:

    def __init__(self, H: np.array, max_error: float = 1e-6):
        self.__H = H
        self.__max_error = max_error

    @property
    def max_error(self):
        return self.__max_error
    
    def processSignal(self, signal: np.array):
        H = self.__H
        r = signal

        # p0=HTr0
        p = np.matmul(H.T, r)

        # f0=0
        image = np.zeros_like(len(p))

        error = self.max_error+1
        iterations = 0
        while error > self.max_error and iterations < 100:
            iterations += 1
            # 𝐰𝐢=𝐇𝐩𝐢
            w = np.matmul(H, p)
            # 𝛼𝑖=||𝐳𝐢||22/||𝐰𝐢||22
            alpha = np.linalg.norm(p)**2 / np.linalg.norm(w)**2

            # fi+1=fi+αipi
            image = image + alpha*p.T
            # ri+1=ri−αiHpi
            r_aux = r - alpha * np.dot(H, p) 

            # ϵ=ri+12−ri2
            error = abs(np.linalg.norm(r_aux) - np.linalg.norm(r))

            if error < self.max_error:
                break
            
            # βi=rTi+1ri+1rTiri
            beta = np.dot(r_aux.T, r_aux) / np.dot(r.T, r)
            # pi+1=HTri+1+βipi
            p = np.dot(H.T, r_aux) + beta*p
            
            r = r_aux

        return image, iterations, error