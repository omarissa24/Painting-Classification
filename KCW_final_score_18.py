from KCW_Team_18 import main

def KCW_final_score(input_file_path):
    res = main(input_file_path)
    print(input_file_path, res)
    return res

import os
total = 0
for file in os.listdir('Data'):
    # total += KCW_final_score(file)
    print(file)
    total += 1

print('Total score:', total)
