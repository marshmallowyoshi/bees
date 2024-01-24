from train_forest import train_forest, forest_struct_to_csv
from forest_bytes_from_csv_linked import forest_to_binary, create_array_for_c, get_forest_structure
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

DATA_SOURCE = "observations-386953.csv"
OUTPUT_NAME = "temp_forest"
C_DATA_OUTPUT = "forest_data"
BINARY_OUTPUT = "temp.bin"

def main():
    inaturalist_bombus_observations = pd.read_csv(DATA_SOURCE)
    rf, _, _ = train_forest(inaturalist_bombus_observations)
    forest_struct_to_csv(rf, OUTPUT_NAME)

    forest_bytes = forest_to_binary(''.join((OUTPUT_NAME, '.csv')), BINARY_OUTPUT, write_to_file=False)
    csv_name = ''.join((OUTPUT_NAME, '.csv'))
    meta_name = ''.join((OUTPUT_NAME, '.meta'))
    create_array_for_c(forest_bytes, get_forest_structure(csv_name), meta_name, C_DATA_OUTPUT)
    return

if __name__ == "__main__":
    main()
