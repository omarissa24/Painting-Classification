import multiprocessing
import time

def process_paintings(file_path):
  with open(file_path, 'r') as file:
    n = int(next(file).strip())
    
    frameglasses = []
    
    for i in range(n):
      line = next(file).strip().split()
      painting_type = line[0]
      tags = set(line[2:int(line[1])+2])
      
      if painting_type == 'L':
        frameglasses.append({'type': 'L', 'paintings': [i], 'tags': list(tags)})
      elif painting_type == 'P':
        frameglasses.append({'type': 'P', 'paintings': [i], 'tags': list(tags)})

    # sort the frameglasses by alphabetical order of tags
    frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)

    # combine the first P that you find with the last P at the end of the list and remove the last P
    i = 0
    while i < len(frameglasses):
      if frameglasses[i]['type'] == 'P':
        j = len(frameglasses) - 1
        while j > i:
          if frameglasses[j]['type'] == 'P':
            combined_tags = set(frameglasses[i]['tags']).union(set(frameglasses[j]['tags']))
            frameglasses[i] = {'type': 'P', 'paintings': [i, j], 'tags': list(combined_tags)}
            frameglasses.pop(j)
            break
          j -= 1
      i += 1
  return frameglasses

def find_furthest_distance_between_two_fg(frameglasses):
    max_distance = 0
    for i in range(0, len(frameglasses), 2):
        distance = frameglasses[i+1]['paintings'][0] - frameglasses[i]['paintings'][0]
        if distance > max_distance:
            max_distance = distance
    return max_distance

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

def get_freq_of_tags_with_index_of_frameglass(frameglass_combos):
    tags_fg = {}
    for i, fg in enumerate(frameglass_combos):
        for tag in fg['tags']:
            if tag not in tags_fg:
                tags_fg[tag] = []
            tags_fg[tag].append(i)

    for tag in tags_fg:
        tags_fg[tag] = len(tags_fg[tag])

    return len([tag for tag in tags_fg if tags_fg[tag] > 1])

def get_max_fg_with_same_len_tags(frameglass_combos):
    tags_fg = {}
    for fg in frameglass_combos:
        if (len(fg['tags']) not in tags_fg):
            tags_fg[len(fg['tags'])] = 0
        tags_fg[len(fg['tags'])] += 1

    return max(tags_fg, key=tags_fg.get)

def get_max_satisfaction(frameglass_combos, chunk_size=100):
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

    return total_satisfaction, res

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
    combos = process_paintings(input_file_path)

    thresholds = [200, 500, 1000, 2000]
    res = []

    for threshold in thresholds:
        max_satisfaction, max_satisfaction_combo = get_max_satisfaction(combos, threshold)
        res.append((max_satisfaction))
        combos = max_satisfaction_combo

    output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    write_output_file(output_file_path, max_satisfaction_combo)

    return max_satisfaction

if __name__ == '__main__':
    start = time.time()
    print(main('110_oily_portraits.txt'))
    print((time.time() - start) / 60)

    start = time.time()
    print(main('11_randomizing_paintings.txt'))
    print((time.time() - start) / 60)