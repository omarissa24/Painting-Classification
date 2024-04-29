paintings_file_path = '0_example.txt'
import time

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

def get_frameglasses_combinations(frameglasses):
    frameglasses_combinations = []
    
    for i in range(len(frameglasses)):
        for j in range(i+1, len(frameglasses)):
            frameglasses_combinations.append({'frameglasses': [frameglasses[i], frameglasses[j]], 'tags': set(frameglasses[i]['tags']).union(set(frameglasses[j]['tags']))})

    return frameglasses_combinations


def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

def get_combo_with_max_satisfaction(frameglasses_combinations):
    max_satisfaction = 0
    best_combo = None
    
    for combo in frameglasses_combinations:
        satisfaction_score = get_local_robotic_satisfaction(combo['frameglasses'][0], combo['frameglasses'][1])
        max_satisfaction = max(max_satisfaction, satisfaction_score)
        if max_satisfaction == satisfaction_score:
            best_combo = combo['frameglasses']
    
    return best_combo

time1 = time.time()

res = process_paintings(paintings_file_path)

combos = get_frameglasses_combinations(res)

best_combo = get_combo_with_max_satisfaction(combos)

output_file_path = paintings_file_path.replace('.txt', '_output.txt')

with open(output_file_path, 'w') as file:
    file.write(str(len(best_combo)) + '\n')
    
    for combo in best_combo:
        if combo['type'] == 'L':
            file.write(str(combo['paintings'][0]) + '\n')
        elif combo['type'] == 'P':
            file.write(str(combo['paintings'][0]) + ' ' + str(combo['paintings'][1]) + '\n')
time2 = time.time()

print(time2 - time1)