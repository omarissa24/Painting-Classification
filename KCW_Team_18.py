import time
import heapq
import multiprocessing

# def process_paintings(file_path):
#     with open(file_path, 'r') as file:
#         n = int(next(file).strip())
        
#         frameglasses = []
#         portrait_buffer = None
        
#         for i in range(n):
#             line = next(file).strip().split()
#             painting_type = line[0]
#             tags = set(line[2:int(line[1])+2])
            
#             if painting_type == 'L':
#                 frameglasses.append({'type': 'L', 'paintings': [i], 'tags': list(tags)})
#             elif painting_type == 'P':
#                 if portrait_buffer:
#                     combined_tags = portrait_buffer['tags'].union(tags)
#                     frameglasses.append({'type': 'P', 'paintings': [portrait_buffer['index'], i], 'tags': list(combined_tags)})
#                     portrait_buffer = None
#                 else:
#                     portrait_buffer = {'tags': tags, 'index': i}
        
#         if portrait_buffer:
#             frameglasses.append({'type': 'P', 'paintings': [portrait_buffer['index']], 'tags': list(portrait_buffer['tags'])})

#     frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
#     return frameglasses

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

    frameglasses.sort(key=lambda x: len(x['tags']), reverse=True)
    merge_portraits(frameglasses)
    return frameglasses

def merge_portraits(frameglasses):
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

def get_local_robotic_satisfaction(frameglass1, frameglass2):
    common_tags = len(set(frameglass1['tags']).intersection(set(frameglass2['tags'])))
    tags_in_frameglass1 = len(set(frameglass1['tags']).difference(set(frameglass2['tags'])))
    tags_in_frameglass2 = len(set(frameglass2['tags']).difference(set(frameglass1['tags'])))
    
    return min(common_tags, tags_in_frameglass1, tags_in_frameglass2)

# this function runs in O(n^2) time
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

    return total_satisfaction, res

def get_max_satisfaction_multi_process(frameglass_combos):
    frameglass_combos.sort(key=lambda x: len(x['tags']), reverse=True)

    if not frameglass_combos:
        return 0, []
    
    curr_fg = frameglass_combos[0]
    res = [curr_fg]
    rem_fg = frameglass_combos[1:]
    total_satisfaction = 0

    # Split the remaining frameglasses into 4 equal parts
    n = len(rem_fg)
    part_size = n // 2
    parts = [rem_fg[i:i+part_size] for i in range(0, n, part_size)]

    # Create a pool of 4 processes
    if __name__ == '__main__':
        pool = multiprocessing.Pool()
        # Run the get_max_satisfaction function for each part
        results = pool.map(get_max_satisfaction, parts)
        pool.close()
        pool.join()

        for satisfaction, fg_list in results:
            total_satisfaction += satisfaction
            res.extend(fg_list)

    return total_satisfaction, res

from heapq import heappush, heappop

def get_max_satisfaction_greedy(frameglass_combos):
    if not frameglass_combos:
        return 0, []

    # Sort frameglass_combos based on the length of 'tags'
    frameglass_combos.sort(key=lambda x: len(x['tags']), reverse=True)

    # Initialize variables
    curr_fg = frameglass_combos[0]
    res = [curr_fg]
    total_satisfaction = 0
    max_heap = []

    # Create a list of available items initially set to True for all
    available = [True] * len(frameglass_combos)
    available[0] = False  # Mark the first as used

    # Pre-fill the heap
    for i in range(1, len(frameglass_combos)):
        satisfaction = -get_local_robotic_satisfaction(curr_fg, frameglass_combos[i])  # Use negative for max heap
        heappush(max_heap, (satisfaction, i))

    while max_heap:
        max_satisfaction, idx = heappop(max_heap)
        max_satisfaction = -max_satisfaction  # Convert back to positive

        if available[idx]:
            max_fg = frameglass_combos[idx]
            res.append(max_fg)
            available[idx] = False  # Mark as used
            total_satisfaction += max_satisfaction
            curr_fg = max_fg

            # Update heap with the new curr_fg
            for i in range(len(frameglass_combos)):
                if available[i]:
                    satisfaction = -get_local_robotic_satisfaction(curr_fg, frameglass_combos[i])
                    heappush(max_heap, (satisfaction, i))

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
    max_satisfaction, max_satisfaction_combo = get_max_satisfaction_batch(combos, 1000)
    print(max_satisfaction)

    output_file_path = str(max_satisfaction) + '-' + input_file_path.split('/')[-1].replace('.txt', '_output.txt')

    write_output_file(output_file_path, max_satisfaction_combo)

    return max_satisfaction

# --------------------------------------------

if __name__ == '__main__':
    start = time.time()
    print(main('110_oily_portraits.txt'))
    print((time.time() - start) / 60)