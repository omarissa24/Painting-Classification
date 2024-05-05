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
        
        for i in range(n):
            line = next(file).strip().split()
            painting_type = line[0]
            tags = set(line[2:int(line[1])+2])
            
            if painting_type == 'L':
                landscape_tags[i] = tags
                frameglasses.append({'type': 'L', 'paintings': [i], 'tags': list(tags)})
            elif painting_type == 'P':
                portrait_tags[i] = tags
            
            for tag in tags:
                if tag not in tag_frameglasses:
                    tag_frameglasses[tag] = []
                tag_frameglasses[tag].append(i)
        
        merged_portraits = merge_portraits(portrait_tags, 2000)
        frameglasses.extend(merged_portraits)

        frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
    return frameglasses, landscape_tags, portrait_tags, tag_frameglasses

def merge_portraits(portrait_tags, batch_size=800):
    portrait_tags = dict(sorted(portrait_tags.items(), key=lambda x: len(x[1]), reverse=True))
    portrait_indexes = list(portrait_tags.keys())
    merged_portraits = []
    
    for i in range(0, len(portrait_indexes), batch_size):
        batch = portrait_indexes[i:i+batch_size]
        used = set()

        for i, first in enumerate(batch):
            if first in used:
                continue
            best_pair = None
            best_common_tags = float('inf')
            used.add(first)
            
            for j, second in enumerate(batch):
                if second in used:
                    continue
                common_tags = len(portrait_tags[first].intersection(portrait_tags[second]))
                if common_tags < best_common_tags:
                    best_pair = second
                    best_common_tags = common_tags

            if best_pair:
                merged_tags = list(portrait_tags[first].union(portrait_tags[best_pair]))
                merged_portraits.append({
                    'type': 'P',
                    'paintings': [first, best_pair],
                    'tags': merged_tags
                })
                used.add(best_pair)



    return merged_portraits

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

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

def best_combo_binary(frameglasses, tag_frameglasses):
    best_combo = []
    fg_copy = frameglasses.copy()
    frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
    max_satisfaction = 0
    visited = set()
    best_combo.append(frameglasses[0])
    visited.add(frameglasses[0]['paintings'][0])
    frameglasses.pop(0)

    while frameglasses:
        curr = best_combo[-1]
        neighbors = []
        for tag in curr['tags']:
            neighbors.extend([index for index in tag_frameglasses[tag] if index not in visited])

        for neighbor in neighbors:
            if neighbor not in visited:
                nb_common_tags = len(set(curr['tags']).intersection(set(fg_copy[neighbor]['tags'])))
                nb_tags = len(fg_copy[neighbor]['tags'])
                if nb_tags > 2 * nb_common_tags:
                    best_combo.append(fg_copy[neighbor])
                    visited.add(neighbor)
                    frameglasses.remove(fg_copy[neighbor])
                    break

        if not neighbors:
            best_combo.append(frameglasses[-1])
            visited.add(frameglasses[-1]['paintings'][0])
            frameglasses.pop(-1)
            curr = best_combo[-1]

    
    for i in range(len(best_combo) - 1):
        max_satisfaction += get_local_robotic_satisfaction(best_combo[i], best_combo[i+1])

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
    
def main(input_file_path, is_binary=False, is_oily=False, is_random=False, is_computable=False, is_example=False):

    input_file_path = 'Data/' + input_file_path
    paintings, landscape_tags, portrait_tags, tag_frameglasses = process_paintings(input_file_path)

    max_satisfaction = 0
    max_satisfaction_combo = []

    if is_example:
        # example combo
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 10)

    if is_computable:
        # computable combo
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 1000)

    if is_binary:
        # binary combo
        max_satisfaction, max_satisfaction_combo = best_combo_binary(paintings, tag_frameglasses)

        return max_satisfaction
    
    if is_oily:
        # oily combo
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 1000)
        print("First batch done:", max_satisfaction)
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 1200)

    if is_random:
        # randomizing combo
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(paintings, 1000)
        print("First batch done:", max_satisfaction)
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(max_satisfaction_combo, 1500)

    # output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')
    # write_output_file(output_file_path, max_satisfaction_combo)

    return max_satisfaction

print(main('110_oily_portraits.txt', is_oily=True))