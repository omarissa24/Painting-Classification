"""
KCW Team 18

Omar Issa
Akram Yamak
Samih Mackieh
Chris Karam
Brial Alalam

"""

import time
from KCW_Team_18 import main

def KCW_final_score(input_file_path):

    res = 0

    is_example = False
    is_binary = False
    is_computable = False
    is_random = False
    is_oily = False

    if input_file_path == '0_example.txt':
        is_example = True
    elif input_file_path == '1_binary_landscapes.txt':
        is_binary = True
    elif input_file_path == '10_computable_moments.txt':
        is_computable = True
    elif input_file_path == '11_randomizing_paintings.txt':
        is_random = True
    elif input_file_path == '110_oily_portraits.txt':
        is_oily = True
    else:
        raise Exception('Error:', 'Invalid input file')
    res = main(input_file_path, is_binary, is_oily, is_random, is_computable, is_example)
    print(input_file_path, res)
    return res

import os 

start = time.time()

total = 0
for file in os.listdir('Data'):
    if file.endswith('.txt'):
        total += KCW_final_score(file)

print('Total time:', (time.time()-start) / 60, ' minutes')
print('Total score:', total)
