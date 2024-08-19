import numpy as np
from PIL import Image

class CGNRAlgorithm:
    def __init__(self, H: np.array):
        self.__H = H

    def processSignal(self, signal: np.array):
        H = self.__H
        r = signal

        # p0=HTr0
        p = np.matmul(H.T, r)

        # f0=0
        image = np.zeros_like(len(p))

        erro = 1

        cont = 0

        while erro > 1e-6:
            cont += 1
            # 𝐰𝐢=𝐇𝐩𝐢
            w = np.matmul(H, p)
            # 𝛼𝑖=||𝐳𝐢||22/||𝐰𝐢||22
            alpha = np.linalg.norm(p)**2 / np.linalg.norm(w)**2

            # fi+1=fi+αipi
            image = image + alpha*p.T
            # ri+1=ri−αiHpi
            r_aux = r - alpha * np.dot(H, p) 

            # ϵ=ri+12−ri2
            erro = abs(np.linalg.norm(r_aux) - np.linalg.norm(r))
            # print('error', erro, erro > 1e-6 )
            if erro < 1e-6:
                break
            
            # βi=rTi+1ri+1rTiri
            beta = np.dot(r_aux.T, r_aux) / np.dot(r.T, r)
            # pi+1=HTri+1+βipi
            p = np.dot(H.T, r_aux) + beta*p
            
            r = r_aux

        print('Iterações:', cont)

        image = image - image.min()
        image = image / image.max()
        image = image * 255
        
        image = np.reshape(image, (30, 30), order='F')
        # print(image)
        
        img = Image.fromarray(image)
        img = img.convert("L")
        
        return img, cont