
import random
import networkx as nx
import networkx.algorithms.approximation as nx_app
import time
from collections import defaultdict
import numpy as np


def get_frameglasses(file_path):
  # a dictionary that stores the set of tags for each index of landscpe paintings
  landscape_tags = {}
  # a dictionary that stores the set of tags for each index of portrait paintings
  portrait_tags = {}
  # a dictionary that stores the set of frameglasses that contain a particular tag
  tag_frameglasses = {}
  # A list of index that represent the list of index of frameglasses ordered by the number of tags
  frameglasses = []
  with open(file_path, 'r') as file:
        n = int(next(file).strip())

        for i in range(n):
            line = next(file).strip().split()
            painting_type = line[0]
            tags = set(line[2:int(line[1])+2])

            if painting_type == 'L':
                landscape_tags[i] = tags
            elif painting_type == 'P':
                portrait_tags[i] = tags
            for tag in tags:
                if tag not in tag_frameglasses:
                    tag_frameglasses[tag] = []
                tag_frameglasses[tag].append(i)
            
            frameglasses.append({'index': i, 'tags': tags})

        # frameglasses.sort(key=lambda x: len(x['tags']))
        frameglasses = connectivity_based_sorting(frameglasses, tag_frameglasses)

  return frameglasses, landscape_tags, portrait_tags, tag_frameglasses

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)


# find the average distance between two frameglasses that have the same tag
def find_average_distance_between_two_fg(frameglasses, tag_frameglasses):
    total_distance = 0
    total_pairs = 0
    n = len(frameglasses)
    for tag in tag_frameglasses:
        fg_indexes = tag_frameglasses[tag]
        fg_indexes = [index for index in fg_indexes if index < n]
        if len(fg_indexes) < 2:
            continue
        for i in range(0, len(fg_indexes) - 1, 2):
            distance = abs(frameglasses[fg_indexes[i+1]]['index'] - frameglasses[fg_indexes[i]]['index'])
            total_distance += distance
            total_pairs += 1

    return -(-total_distance // total_pairs)

# create a dictionary where the key is the number of tags for each frameglass and the value is the number of frameglasses with that number of tags
def get_freq_of_tags_with_index_of_frameglass(frameglass_combos):
    tags_fg = {}
    for i, fg in enumerate(frameglass_combos):
        if len(fg['tags']) not in tags_fg:
            tags_fg[len(fg['tags'])] = 0
        tags_fg[len(fg['tags'])] += 1

    # sort the values of the dictionary in descending order
    tags_fg = dict(sorted(tags_fg.items(), key=lambda x: x[1], reverse=True))
    return tags_fg

def connectivity_based_sorting(frameglasses, tag_frameglasses):
    # Calculate the number of potential connections for each frameglass
    frameglass_connections = {}
    for fg in frameglasses:
        connections = set()
        for tag in fg['tags']:
            connections.update(tag_frameglasses[tag])
        # Remove self-connection
        connections.discard(fg['index'])
        frameglass_connections[fg['index']] = len(connections)

    # Sort frameglasses based on the number of connections
    frameglasses.sort(key=lambda x: frameglass_connections[x['index']], reverse=True)

    return frameglasses

def get_best_combo(frameglasses, tag_frameglasses):
    best_combo = []
    max_satisfaction = 0
    visited = set()
    for fg in frameglasses:
        neighbors = []
        if fg['index'] not in visited:
            visited.add(fg['index'])
            for tag in fg['tags']:
                neighbors.extend([index for index in tag_frameglasses[tag] if index not in visited])
                
            for neighbor in neighbors:
                if neighbor not in visited:
                    nb_common_tags = len(set(fg['tags']).intersection(set(frameglasses[neighbor]['tags'])))
                    nb_tags = len(frameglasses[neighbor]['tags'])
                    if nb_tags > 2 * nb_common_tags:
                        max_satisfaction += get_local_robotic_satisfaction(fg, frameglasses[neighbor])
                        best_combo.append(fg['index'])
                        best_combo.append(frameglasses[neighbor]['index'])
                        visited.add(neighbor)
                        break

    for fg in frameglasses:
        if fg['index'] not in visited:
            best_combo.append(fg['index'])
            visited.add(fg['index'])

    return max_satisfaction, best_combo

def sort_based_on_occurance_of_same_number_of_tags(frameglasses):
    freq = get_freq_of_tags_with_index_of_frameglass(frameglasses)
    sorted_frameglasses = []
    for key in freq:
        for fg in frameglasses:
            if len(fg['tags']) == key:
                sorted_frameglasses.append(fg)

    # sorted_frameglasses = interleave_sorted_frameglasses(sorted_frameglasses)

    return sorted_frameglasses

def create_tags_graph(frameglasses, tag_frameglasses):
    G = nx.Graph()
    
    for tag, fgs in tag_frameglasses.items():
        if len(fgs) == 2:
            fg1, fg2 = fgs
            score = get_local_robotic_satisfaction(frameglasses[fg1], frameglasses[fg2])
            G.add_edge(fg1, fg2, weight=score)
    return G

def get_max_satisfaction_greedy(frameglasses, tag_frameglasses):
    G = create_tags_graph(frameglasses, tag_frameglasses)
    total_satisfaction = 0
    res = []
    visited = set()
    for u, v, w in sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True):
        if u not in visited and v not in visited:
            total_satisfaction += w['weight']
            res.append(u)
            res.append(v)
            visited.add(u)
            visited.add(v)
    return total_satisfaction, res

def write_output_file(output_file_path, best_combo):
    with open(output_file_path, 'w') as file:
        file.write(str(len(best_combo)) + '\n')
        for frameglass in best_combo:
            file.write(str(frameglass) + '\n')

def sort_based_on_freq_of_number_of_tags(frameglasses):
    freq = get_freq_of_tags_with_index_of_frameglass(frameglasses)
    sorted_frameglasses = []
    for key in freq:
        for fg in frameglasses:
            if len(fg['tags']) == key:
                sorted_frameglasses.append(fg)

    return sorted_frameglasses

def main(input_file_path):
    frameglasses, landscape_tags, portrait_tags, tag_frameglasses = get_frameglasses(input_file_path)
    print(get_freq_of_tags_with_index_of_frameglass(frameglasses))
 
    max_satisfaction, best_combo = get_best_combo(frameglasses, tag_frameglasses)
    # output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    # write_output_file(output_file_path, best_combo)
    return max_satisfaction


start = time.time()
print(main('1_binary_landscapes.txt'))
print(time.time() - start)