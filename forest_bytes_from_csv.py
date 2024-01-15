import csv
import numpy as np

forest = csv.reader(open('forest.csv', 'r', encoding='utf-8-sig'), delimiter=',')

with open('forest.bin', 'wb') as f:
    for idx, row in enumerate(forest):
        if idx == 0:
            continue

        depth = int(row[0]).to_bytes(1, 'big')

        if row[1] != '':
            threshold = np.array(float(row[1])).tobytes()
        else:
            threshold = b''

        if row[2] != '':
            feature = int(row[2]).to_bytes(1, 'big')
        else:
            feature = b''

        if row[3] != '':
            
            value = np.array([int(x) for x in row[3].strip('.][').split('. ')]).tobytes()
        else:
            value = b''
        
        f.write(depth + threshold + feature + value)
