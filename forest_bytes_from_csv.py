"""
This script is used to convert the forest.csv file into a compact binary file for use in embedded systems.
"""

import csv
import numpy as np

FILE_NAME = 'forest.csv'
BINARY_NAME = 'forest.bin'
EMPTY_BYTES = b''

forest = csv.reader(open(FILE_NAME, 'r', encoding='utf-8-sig'), delimiter=',')



with open(BINARY_NAME, 'wb') as f:
    all_bytes = EMPTY_BYTES

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

        all_bytes = all_bytes + depth + threshold + feature + value
    print(all_bytes)
    print(len(all_bytes))
    f.write(all_bytes)