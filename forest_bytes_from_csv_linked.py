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

            value = np.array([np.int16(x) for x in row[3].strip('.][').replace('\n', '').split(', ')]).tobytes()
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
            

def create_array_for_c(all_bytes, forest_structure, metadata, c_file_names='forest_data', byte_format='hex'):

    c_file = "".join((c_file_names, '.c'))
    h_file = "".join((c_file_names, '.h'))

    ptr = 0
    if byte_format == 'hex':
        byte_list = bytes_to_hex(all_bytes)
    elif byte_format == 'decimal':
        byte_list = bytes_to_decimal(all_bytes)
    else:
        raise ValueError
    
    with open(metadata, 'r', encoding='utf-8-sig') as f:
        for line in f:
            # if line.startswith('largest_sample_size'):
            #     largest_sample_size = int(line.split(':')[1].strip())
            if line.startswith('feature_count'):
                feature_count = int(line.split(':')[1].strip())
            elif line.startswith('tree_count'):
                tree_count = int(line.split(':')[1].strip())
            elif line.startswith('class_count'):
                class_count = int(line.split(':')[1].strip())
            elif line.startswith('classes'):
                classes = [x for x in line.split(':')[1].strip().split(', ')]
            # elif line.startswith('max_depth'):
            #     max_depth = int(line.split(':')[1].strip())
    
    with open(c_file, 'w', encoding='utf-8-sig') as f:
        f.write('#include <stdint.h>\n')

        f.write(f'char *classes[{class_count}] = ')
        f.write('{')
        for c in classes:
            f.write(f'\"{c}\",\n')
        f.write('};\n')

        f.write('uint8_t forest_structure[] = {\n')
        for row in forest_structure:
            if row:
                vals = byte_list[ptr:ptr+8]
                ptr += 8
                f.write(f'{", ".join([str(v) for v in vals])},\n')
            else:
                vals = byte_list[ptr:(ptr+1+(2*class_count))]
                ptr += 1+(2*class_count)
                f.write(f'{", ".join([str(v) for v in vals])},\n')
        f.write('};\n')
    

    with open(h_file, 'w', encoding='utf-8-sig') as f:
        f.write('#include <stdint.h>\n')
        f.write(f'#define FEATURE_COUNT {feature_count}\n')
        f.write(f'#define FOREST_SIZE {tree_count}\n')
        f.write(f'#define NUM_CLASSES {class_count}\n\n')

        # f.write('typedef structure {\n')
        # if max_depth < 128:
        #     f.write('    int8_t depth;\n')
        # else:
        #     f.write('    int16_t depth;\n')
        # f.write('    float threshold;\n')
        # if feature_count < 256:
        #     f.write('    uint8_t feature;\n')
        # else:
        #     f.write('    uint16_t feature;\n')
        # if len(byte_list) < 32768:
        #     f.write('    int16_t next_node;\n')
        # else:
        #     f.write('    int32_t next_node;\n')
        # f.write('} branch_t;\n\n')

        # f.write('typedef structure {\n')
        # if max_depth < 128:
        #     f.write('    int8_t depth;\n')
        # else:
        #     f.write('    int16_t depth;\n')
        # if largest_sample_size < 32768:
        #     f.write(f'    int16_t value[{class_count}];\n')
        # else:
        #     f.write(f'    int32_t value[{class_count}];\n')


    return 0





# FILE_NAME = 'temp_forest.csv'
# BINARY_NAME = 'temp.bin'

# final_bytes = forest_to_binary(FILE_NAME, BINARY_NAME, write_to_file=False)

# create_array_for_c(final_bytes, get_forest_structure(FILE_NAME))