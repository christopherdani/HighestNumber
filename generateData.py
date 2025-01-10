import numpy as np
import uuid
import time
import os 

directory = 'Data' 
if not os.path.exists(directory): 
    os.makedirs(directory) 
    
file_path = os.path.join(directory, 'data.csv') 
outfile = os.path.join(directory, 'data.csv')

numRows = 10_000_000

data = [[uuid.uuid4().int for i in range(numRows)],
        np.random.randint(0, 999999999 ,size=(numRows,))]
rows = ['%i_%i\n' % row for row in zip(*data)]

t0 = time.time()

with open(outfile, 'a') as csvfile:
    csvfile.writelines(rows)

tdelta = time.time() - t0
print(tdelta)        