
import random
import networkx as nx
import networkx.algorithms.approximation as nx_app
import time


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

        # frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)

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

def main(input_file_path):
    frameglasses, landscape_tags, portrait_tags, tag_frameglasses = get_frameglasses(input_file_path)
    G = create_tags_graph(frameglasses, tag_frameglasses)
    cycle = nx_app.christofides(G, weight='weight')
    edge_list = list(nx.utils.pairwise(cycle))
    max_satisfaction = sum([G[u][v]['weight'] for u, v in edge_list])
    print(max_satisfaction)
    # max_satisfaction, best_combo = get_max_satisfaction_greedy(frameglasses, tag_frameglasses)
    # output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    # # write_output_file(output_file_path, best_combo)
    # return max_satisfaction


start = time.time()
print(main('1_binary_landscapes.txt'))
print(time.time() - start)