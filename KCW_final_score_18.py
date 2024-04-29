from KCW_Team_18 import main

def KCW_final_score(input_file_path):
    res = main(input_file_path)
    print(input_file_path, res)
    return res

total = 0
total += KCW_final_score('110_oily_portraits.txt')
total += KCW_final_score('11_randomizing_paintings.txt')
total += KCW_final_score('1_binary_landscapes.txt')

print('Total score:', total)
