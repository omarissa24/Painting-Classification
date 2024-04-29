import time
import itertools

def process_paintings(file_path):
    with open(file_path, 'r') as file:
        n = int(file.readline().strip())
        
        landscapes = []
        portraits = []
        
        for i in range(n):
            line = file.readline().strip().split()
            painting_type = line[0]
            tag_count = int(line[1])
            tags = line[2:2+tag_count]
            
            if painting_type == 'L':
                landscapes.append((i, set(tags)))
            elif painting_type == 'P':
                portraits.append((i, set(tags)))
    
    frameglasses = []
    
    for landscape in landscapes:
        frameglasses.append({'type': 'L', 'paintings': [landscape[0]], 'tags': list(landscape[1])})
    
    for i in range(0, len(portraits), 2):
        if i+1 < len(portraits):
            combined_tags = portraits[i][1].union(portraits[i+1][1])
            frameglasses.append({'type': 'P', 'paintings': [portraits[i][0], portraits[i+1][0]], 'tags': list(combined_tags)})
        else:
            frameglasses.append({'type': 'P', 'paintings': [portraits[i][0]], 'tags': list(portraits[i][1])})
    
    return frameglasses

# this function returns all possible combinations of frameglasses in the form of a list of lists of frameglasses
def get_frameglasses_combinations(frameglasses):
    frameglass_combos = list(itertools.permutations(frameglasses))
    
    return frameglass_combos
    

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

def get_global_robotic_satisfaction(frameglass_combos):
    global_satisfaction = 0
    
    for i in range(len(frameglass_combos)):
        for j in range(i+1, len(frameglass_combos)):
            global_satisfaction += get_local_robotic_satisfaction(frameglass_combos[i], frameglass_combos[j])
    
    return global_satisfaction

def get_max_satisfaction(frameglass_combos):
    max_satisfaction = 0
    max_satisfaction_combo = None
    
    for frameglass_combo in frameglass_combos:
        satisfaction = get_global_robotic_satisfaction(frameglass_combo)
        max_satisfaction = max(max_satisfaction, satisfaction)

        if satisfaction == max_satisfaction:
            max_satisfaction_combo = frameglass_combo
    
    return max_satisfaction, max_satisfaction_combo

def write_output_file(output_file_path, best_combo):
    with open(output_file_path, 'w') as file:
        file.write(str(len(best_combo)) + '\n')
        for frameglass in best_combo:
            if frameglass['type'] == 'L':
                file.write(str(frameglass['paintings'][0]) + '\n')
            elif frameglass['type'] == 'P':
                file.write(str(frameglass['paintings'][0]) + ' ' + str(frameglass['paintings'][1]) + '\n')

def main(input_file_path):
    input_file_path = 'Data/' + input_file_path
    res = process_paintings(input_file_path)

    combos = get_frameglasses_combinations(res)

    max_satisfaction, max_satisfaction_combo = get_max_satisfaction(combos)

    output_file_path = input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    write_output_file(output_file_path, max_satisfaction_combo)

    return max_satisfaction

# --------------------------------------------

start = time.time()

res = main('0_example.txt')
print(res)

print('Time taken:', time.time()-start)