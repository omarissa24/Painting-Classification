import time
import random
from deap import base, creator, tools, algorithms
import numpy
from multiprocessing import Pool
from itertools import combinations, product
from scipy.optimize import linear_sum_assignment
import numpy as np

def process_paintings(file_path, is_binary=False):
    # a dictionary that stores the set of tags for each index of landscpe paintings
    landscape_tags = {}
    # a dictionary that stores the set of tags for each index of portrait paintings
    portrait_tags = {}
    # a dictionary that stores the set of frameglasses that contain a particular tag
    tag_frameglasses = {}
    with open(file_path, 'r') as file:
        n = int(next(file).strip())
        
        frameglasses = []
        portrait_buffer = None
        
        for i in range(n):
            line = next(file).strip().split()
            painting_type = line[0]
            tags = set(line[2:int(line[1])+2])
            
            if painting_type == 'L':
                landscape_tags[i] = tags
                frameglasses.append({'type': 'L', 'paintings': [i], 'tags': list(tags)})
            elif painting_type == 'P':
                portrait_tags[i] = tags
                if portrait_buffer:
                    combined_tags = portrait_buffer['tags'].union(tags)
                    frameglasses.append({'type': 'P', 'paintings': [portrait_buffer['index'], i], 'tags': list(combined_tags)})
                    portrait_buffer = None
                else:
                    portrait_buffer = {'tags': tags, 'index': i}
            
            for tag in tags:
                if tag not in tag_frameglasses:
                    tag_frameglasses[tag] = []
                tag_frameglasses[tag].append(i)
        
        if portrait_buffer:
            frameglasses.append({'type': 'P', 'paintings': [portrait_buffer['index']], 'tags': list(portrait_buffer['tags'])})

    if not is_binary:
        frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
    return frameglasses, landscape_tags, portrait_tags, tag_frameglasses

# def process_paintings(file_path):
#     # a dictionary that stores the set of tags for each index of landscpe paintings
#     landscape_tags = {}
#     # a dictionary that stores the set of tags for each index of portrait paintings
#     portrait_tags = {}
#     # a dictionary that stores the set of frameglasses that contain a particular tag
#     tag_frameglasses = {}
#     with open(file_path, 'r') as file:
#         n = int(next(file).strip())
        
#         frameglasses = []
        
#         for i in range(n):
#             line = next(file).strip().split()
#             painting_type = line[0]
#             tags = set(line[2:int(line[1])+2])
            
#             if painting_type == 'L':
#                 landscape_tags[i] = tags
#                 frameglasses.append({'type': 'L', 'paintings': [i], 'tags': list(tags)})
#             elif painting_type == 'P':
#                 portrait_tags[i] = tags
#                 # frameglasses.append({'type': 'P', 'paintings': [i], 'tags': list(tags)})
            
#             for tag in tags:
#                 if tag not in tag_frameglasses:
#                     tag_frameglasses[tag] = []
#                 tag_frameglasses[tag].append(i)
        
#         pairs = pair_all_portraits(portrait_tags, 5000)
#         merged_portraits = merge_paired_portraits(pairs, portrait_tags)
#         frameglasses.extend(merged_portraits)

#     # frameglasses = merge_portraits(frameglasses)
#     frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
#     return frameglasses, landscape_tags, portrait_tags, tag_frameglasses

def merge_portraits(frameglasses):
    start = 0
    end = len(frameglasses) - 1
    while start < end:
        if frameglasses[start]['type'] == 'P' and frameglasses[end]['type'] == 'P':
            combined_tags = set(frameglasses[start]['tags']) | set(frameglasses[end]['tags'])
            frameglasses[start] = {
                'type': 'P',
                'paintings': [frameglasses[start]['paintings'][0], frameglasses[end]['paintings'][0]],
                'tags': list(combined_tags)
            }
            frameglasses.pop(end)
            start += 1
            end -= 1
        elif frameglasses[start]['type'] == 'P':
            end -= 1
        elif frameglasses[end]['type'] == 'P':
            start += 1
        else:
            start += 1
            end -= 1

    return frameglasses

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

def get_max_satisfaction(frameglass_combos):

    if not frameglass_combos:
        return 0, []
    
    curr_fg = frameglass_combos[0]
    res = [curr_fg]
    rem_fg = frameglass_combos[1:]
    total_satisfaction = 0

    while rem_fg:
        max_satisfaction = 0
        max_fg = None

        for fg in rem_fg:
            satisfaction = get_local_robotic_satisfaction(curr_fg, fg)
            if satisfaction >= max_satisfaction:
                max_satisfaction = satisfaction
                max_fg = fg

        if max_fg:
            res.append(max_fg)
            rem_fg.remove(max_fg)
            total_satisfaction += max_satisfaction
            curr_fg = max_fg
        else:
            break

    return total_satisfaction, res

def get_max_satisfaction_batch(frameglass_combos, chunk_size=100):
    if not frameglass_combos:
        return 0, []
    
    curr_fg = frameglass_combos[0]
    res = [curr_fg]
    rem_fg = frameglass_combos[1:]
    total_satisfaction = 0

    while rem_fg:
        max_satisfaction = -1
        max_fg = None

        for i in range(min(chunk_size, len(rem_fg))):
            satisfaction = get_local_robotic_satisfaction(curr_fg, rem_fg[i])
            if satisfaction > max_satisfaction:
                max_satisfaction = satisfaction
                max_fg = rem_fg[i]

        if max_fg:
            res.append(max_fg)
            rem_fg.remove(max_fg)
            total_satisfaction += max_satisfaction
            curr_fg = max_fg
        else:
            break
    
    for i in range(0, len(rem_fg), 2):
        total_satisfaction += get_local_robotic_satisfaction(rem_fg[i], rem_fg[i+1])
        res.append(rem_fg[i])
        res.append(rem_fg[i+1])

    return total_satisfaction, res

def get_best_combo_binary(frameglasses, tag_frameglasses):
    best_combo = []
    max_satisfaction = 0
    visited = set()
    for fg in frameglasses:
        neighbors = []
        if fg['paintings'][0] not in visited:
            visited.add(fg['paintings'][0])
            for tag in fg['tags']:
                neighbors.extend([index for index in tag_frameglasses[tag] if index not in visited])
                
            for neighbor in neighbors:
                if neighbor not in visited:
                    nb_common_tags = len(set(fg['tags']).intersection(set(frameglasses[neighbor]['tags'])))
                    nb_tags = len(frameglasses[neighbor]['tags'])
                    if nb_tags > 2 * nb_common_tags:
                        max_satisfaction += get_local_robotic_satisfaction(fg, frameglasses[neighbor])
                        best_combo.append(fg)
                        best_combo.append(frameglasses[neighbor])
                        visited.add(neighbor)
                        break

    for fg in frameglasses:
        if fg['paintings'][0] not in visited:
            best_combo.append(fg)
            visited.add(fg['paintings'][0])

    return max_satisfaction, best_combo

def write_output_file(output_file_path, best_combo):
    with open(output_file_path, 'w') as file:
        file.write(str(len(best_combo)) + '\n')
        for frameglass in best_combo:
            if frameglass['type'] == 'L':
                file.write(str(frameglass['paintings'][0]) + '\n')
            elif frameglass['type'] == 'P':
                file.write(str(frameglass['paintings'][0]) + ' ' + str(frameglass['paintings'][1]) + '\n')


def evaluate_batch_size(individual, frameglass_combos):
    batch_size = int(individual[0])
    max_satisfaction, _ = get_max_satisfaction_batch(frameglass_combos, batch_size)
    return (max_satisfaction,)

def setup_toolbox():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_batch_size", random.randint, 10, 1000)
    toolbox.register("individual", tools.initRepeat, creator.Individual, 
                     toolbox.attr_batch_size, n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate_batch_size)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutUniformInt, low=10, up=1000, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    return toolbox


def run_genetic_algorithm(toolbox, threshold=0.01, ngen=20, patience=5):
    pool = Pool()
    toolbox.register("map", pool.map)

    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    last_best = None
    no_improve_count = 0

    for gen in range(ngen):
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=1,
                                       stats=stats, halloffame=hof, verbose=True)

        current_best = hof.items[0].fitness.values[0]
        if last_best is not None and (current_best - last_best) < threshold:
            no_improve_count += 1
        else:
            no_improve_count = 0

        last_best = current_best

        if no_improve_count >= patience:
            print("Convergence reached after", gen + 1, "generations.")
            break

    pool.close()
    return hof[0][0]  # Best batch size found

#     toolbox = setup_toolbox()
#     optimal_batch_size = run_genetic_algorithm(toolbox, threshold=0.01, patience=10)
#     print("Optimal Batch Size Found:", optimal_batch_size)

def compute_intersection_size(i, j, portrait_tags):
    common_tags = len(portrait_tags[i].intersection(portrait_tags[j]))
    tags_in_i = len(portrait_tags[i]) - common_tags
    tags_in_j = len(portrait_tags[j]) - common_tags
    return min(common_tags, tags_in_i, tags_in_j)
    
def hungarian_algorithm(portait_tags):
    keys = list(portait_tags.keys())
    n = len(keys)
    matrix = np.full((n, n), 0)
    for i, j in product(range(n), repeat=2):
        if i != j:
            matrix[i, j] = compute_intersection_size(keys[i], keys[j], portait_tags)
            matrix[j, i] = matrix[i, j]

    row_ind, col_ind = linear_sum_assignment(-matrix)
    
    return [(keys[i], keys[j]) for i, j in zip(row_ind, col_ind)]

def remove_duplicates(pairs):
    paired_portraits = set()
    unique_pairs = []
    for pair in pairs:
        if pair[0] not in paired_portraits and pair[1] not in paired_portraits:
            unique_pairs.append(pair)
            paired_portraits.add(pair[0])
            paired_portraits.add(pair[1])

    return unique_pairs

def pair_portraits_by_batch_size(start, end, portrait_tags):
    sorted_portrait_tags = dict(sorted(portrait_tags.items(), key=lambda x: len(x[1]), reverse=True)[start:end])
    pairs = hungarian_algorithm(sorted_portrait_tags)
    pairs = remove_duplicates(pairs)
    return pairs

def merge_paired_portraits(pairs, portrait_tags):
    merged_portraits = []
    for pair in pairs:
        tags = portrait_tags[pair[0]].union(portrait_tags[pair[1]])
        merged_portraits.append({
            'type': 'P',
            'paintings': [pair[0], pair[1]],
            'tags': list(tags)
        })

    return merged_portraits

def pair_all_portraits(portrait_tags, batch_size=100):
    n = len(portrait_tags)
    pairs = []
    for i in range(0, n, batch_size):
        pair = pair_portraits_by_batch_size(i, min(i+batch_size, n), portrait_tags)
        pairs.extend(pair)

    return pairs

    
def main(input_file_path):

    paintings = process_paintings(input_file_path)
    max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 275)
    max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 600)
    max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 1000)
    print(max_satisfaction)
    output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    write_output_file(output_file_path, max_satisfaction_combo)

    return max_satisfaction

# --------------------------------------------

if __name__ == '__main__':
    start = time.time()
    input_file_path = '1_binary_landscapes.txt'
    paintings, landscape_tags, portrait_tags, tag_frameglasses = process_paintings(input_file_path, True)
    max_satisfaction, best_combo = get_best_combo_binary(paintings, tag_frameglasses)
    # max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 275)
    # max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 600)
    # max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 1000)
    print(max_satisfaction)
    # output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    # write_output_file(output_file_path, max_satisfaction_combo)
    print((time.time() - start) / 60)