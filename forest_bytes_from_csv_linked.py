"""
This script is used to convert the forest.csv file into a compact binary file for use in embedded systems.
"""

import csv
import numpy as np

def forest_to_binary(file_name, binary_name, write_to_file=True):
    forest = csv.reader(open(file_name, 'r', encoding='utf-8-sig'), delimiter=',')

    if write_to_file:
        with open(binary_name, 'wb') as f:
            f.write(byte_struct(forest))
        return 0
    else:
        return byte_struct(forest)

def byte_struct(forest):
    empty_bytes = b''
    all_bytes = empty_bytes
    all_bytes_list = []
    branch_list = []

    for idx, row in enumerate(forest):
        if idx == 0:
            continue

        if row[1] != '':
            # threshold
            threshold = np.float32(row[1]).tobytes()
        else:
            threshold = empty_bytes

        if row[2] != '':
            # feature
            feature = int(row[2]).to_bytes(1, 'big')
        else:
            feature = empty_bytes

        if row[3] != '':
            # depth and value
            depth = (-1 * int(row[0])).to_bytes(1, 'big', signed=True)

            value = np.array([np.int16(x) for x in row[3].strip('.][').split('. ')]).tobytes()
        else:
            depth = int(row[0]).to_bytes(1, 'big', signed=True)

            value = empty_bytes

        if row[4] != '':
            branch_list += [[int(x) for x in row[4].strip('][').split(', ')]]
        else:
            branch_list += [[]]

        all_bytes_list += [[depth, threshold, feature, value]]

    # create linked branch positions
    all_bytes_list = live_traversal(all_bytes_list, branch_list)
    # final byte string
    all_bytes = b''.join([b''.join(x) for x in all_bytes_list])
    return all_bytes

def byte_count(
        all_bytes_list, 
        start_idx, 
        end_idx
        ):
    counter = 0
    for idx in range(start_idx, end_idx):
        counter += sum([len(x) for x in all_bytes_list[idx]])
    return counter


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

def bytes_to_decimal(all_bytes):
    return [b for b in all_bytes]

def bytes_to_hex(all_bytes):
    return [hex(b) for b in all_bytes]

def get_forest_structure(file_name):
    forest = csv.reader(open(file_name, 'r', encoding='utf-8-sig'), delimiter=',')
    return [True if row[4] != '' else False for row in forest][1:]
            

def create_array_for_c(all_bytes, forest_structure, c_file='forest_data.c', byte_format='hex'):
    ptr = 0
    if byte_format == 'hex':
        byte_list = bytes_to_hex(all_bytes)
    elif byte_format == 'decimal':
        byte_list = bytes_to_decimal(all_bytes)
    else:
        raise ValueError
    
    with open(c_file, 'w', encoding='utf-8-sig') as f:
        f.write('#include <stdint.h>\n')
        f.write('uint8_t forest_structure[] = {\n')
        for row in forest_structure:
            if row:
                vals = byte_list[ptr:ptr+8]
                ptr += 8
                f.write(f'{", ".join([str(v) for v in vals])},\n')
            else:
                vals = byte_list[ptr:ptr+21]
                ptr += 21
                f.write(f'{", ".join([str(v) for v in vals])},\n')
        f.write('};\n')




FILE_NAME = 'linked_forest_small.csv'
BINARY_NAME = 'temp.bin'

final_bytes = forest_to_binary(FILE_NAME, BINARY_NAME, write_to_file=False)

create_array_for_c(final_bytes, get_forest_structure(FILE_NAME))