"""
This script is used to convert the forest.csv file into a compact binary file for use in embedded systems.
"""

import csv
import numpy as np

def byte_count(
        all_bytes_list, 
        start_idx, 
        end_idx
        ):
    byte_count = 0
    for idx in range(start_idx, end_idx):
        byte_count += sum([len(x) for x in all_bytes_list[idx]])
    return byte_count


def links_to_pointers(
    branches,
    all_bytes_list,
    idx
    ):
    if len(branches) != 2:
        return b''
    else:
        branch_idx = byte_count(all_bytes_list, idx, branches[1])
        return np.int16(branch_idx).tobytes()
    
def live_traversal(
        all_bytes_list,
        all_branches
        ):
    live_bytes = all_bytes_list[::-1]
    live_branches = all_branches[::-1]
    for idx, branch in enumerate(live_branches):
        live_bytes[idx] = live_bytes[idx] + [links_to_pointers(branch, live_bytes[::-1], len(live_bytes) - idx)]
    return live_bytes[::-1]

FILE_NAME = 'linked_forest.csv'
BINARY_NAME = 'linked_forest.bin'
EMPTY_BYTES = b''

forest = csv.reader(open(FILE_NAME, 'r', encoding='utf-8-sig'), delimiter=',')



with open(BINARY_NAME, 'wb') as f:
    all_bytes = EMPTY_BYTES
    all_bytes_list = []
    branch_list = []

    for idx, row in enumerate(forest):
        if idx == 0:
            continue

        if row[1] != '':
            threshold = np.float32(row[1]).tobytes()
        else:
            threshold = EMPTY_BYTES

        if row[2] != '':
            feature = int(row[2]).to_bytes(1, 'big')
        else:
            feature = EMPTY_BYTES

        if row[3] != '':
            depth = (-1 * int(row[0])).to_bytes(1, 'big', signed=True)
            
            value = np.array([np.int16(x) for x in row[3].strip('.][').split('. ')]).tobytes()
        else:
            depth = int(row[0]).to_bytes(1, 'big', signed=True)

            value = EMPTY_BYTES

        if row[4] != '':
            branch_list += [[int(x) for x in row[4].strip('][').split(', ')]]
        else:
            branch_list += [[]]
        
        all_bytes_list += [[depth, threshold, feature, value]]

    all_bytes_list = live_traversal(all_bytes_list, branch_list)
    # print(all_bytes_list)
    all_bytes = b''.join([b''.join(x) for x in all_bytes_list])
    print(all_bytes)
    f.write(all_bytes)