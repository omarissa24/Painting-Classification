import time
from KCW_Team_18 import main

def KCW_final_score(input_file_path):
    res = main(input_file_path)
    print(input_file_path, res)
    return res

import os 

start = time.time()

total = 0
for file in os.listdir('Data'):
    if file.endswith('.txt'):
        total += KCW_final_score(file)

print('Total time:', time.time()-start)
print('Total score:', total)
