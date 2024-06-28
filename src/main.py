import csv
import os
import pandas as pd

# import libraries required for checking the program completion time
import time

from carina_parser import parser as carina_parser
from csv_rw import csv_rw


SELECT_RANGE = True # Set to False if running for first time on new data
LOWER, UPPER = 28000, 29500 # Set the range
LOWER_F, UPPER_F = 4040, 4140 # Set the range
TEST_DIR = "CF-O4\\"


def main():
    start_time = time.time()

    create_dirs()
    csv_rw.init(TEST_DIR)

    if not carina_parser.has_been_parsed(TEST_DIR):
        print("Parsing data...")
        carina_parser.init(TEST_DIR)
        sensors, actuators = carina_parser.parse_from_raw()
        csv_rw.write_to_cache(sensors, actuators)

    sensor_df, actuator_df = csv_rw.read_into_df()
    csv_rw.write_to_csv(sensor_df, actuator_df)
    if SELECT_RANGE:
        csv_rw.write_to_csv(sensor_df, actuator_df, (LOWER, UPPER), "compiled")
        csv_rw.write_to_csv(sensor_df, actuator_df, (LOWER_F, UPPER_F), "selected")

    end_time = time.time()
    print("Time taken to run the program: ", end_time - start_time, " seconds")


def create_dirs():
    if not os.path.exists(".cache\\"):
        os.mkdir(".cache\\")
    if not os.path.exists(".cache\\" + TEST_DIR):
        os.mkdir(".cache\\" + TEST_DIR)
    if not os.path.exists("Data\\" + TEST_DIR + "compiled\\"):
        os.mkdir("Data\\" + TEST_DIR + "compiled\\")


if __name__ == "__main__":
    main()