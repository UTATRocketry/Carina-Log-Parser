import csv
import os
import pandas as pd

# import libraries required for checking the program completion time
import time


from utils import parse_tools

SELECT_RANGE = True # Set to False if running for first time on new data
LOWER, UPPER = 2600, 4100 # Set the range
LOWER_F, UPPER_F = 4040, 4080 # Set the range
TEST_DIR = "CF-O2\\"
DATA_NAME = "data.log"
EVENT_NAME = "events.log"
DATA_DIR_NAME = "raw\\"
COMPILED_DIR_NAME = "1. Compiled\\"

SENSOR_NAME = "Sensors\\"
ACTUATOR_NAME = "Actuators\\"


def main():

    # start the timer
    start_time = time.time()
    os.chdir("Data")
    create_dirs()
    # If the data has already been parsed, skip the parsing step
    if not (os.path.exists("..\\.cache\\" + TEST_DIR + "sensors.csv") and os.path.exists("..\\.cache\\" + TEST_DIR + "actuators.csv")):
        print("Parsing data...")
        sensors, actuators = parse_from_raw()
        write_to_cache(sensors, actuators)
    sensor_df, actuator_df = read_into_df()
    write_to_csv(sensor_df, actuator_df)
    if SELECT_RANGE:
        write_to_csv(sensor_df, actuator_df, (LOWER, UPPER), "selected")
        write_to_csv(sensor_df, actuator_df, (LOWER_F, UPPER_F), "further_selected")

    # stop the timer
    end_time = time.time()
    print("Time taken to run the program: ", end_time - start_time, " seconds")


def create_dirs():
    if not os.path.exists("..\\.cache\\"):
        os.mkdir("..\\.cache\\")
    if not os.path.exists("..\\.cache\\" + TEST_DIR):
        os.mkdir("..\\.cache\\" + TEST_DIR)


def write_to_cache(sensors, actuators):
    # Create a Pandas DataFrame with column names as the sensor and actuator names
    sensor_df = pd.DataFrame(columns=["Time"] + list(sensors.keys()))
    sensor_df["Time"] = [val[0] for val in sensors[list(sensors.keys())[0]]]
    for sensor in sensors:
        sensor_df[sensor] = [val[1] for val in sensors[sensor]]
    sensor_df.to_csv("..\\.cache\\" + TEST_DIR + "sensors.csv", index=False)

    actuator_df = pd.DataFrame(columns=["Time"] + list(actuators.keys()))
    actuator_df["Time"] = [val[0] for val in actuators[list(actuators.keys())[0]]]
    for actuator in actuators:
        actuator_df[actuator] = [val[1] for val in actuators[actuator]]
    actuator_df.to_csv("..\\.cache\\" + TEST_DIR + "actuators.csv", index=False)


def read_into_df():
    sensor_df = pd.read_csv("..\\.cache\\" + TEST_DIR + "sensors.csv")
    actuator_df = pd.read_csv("..\\.cache\\" + TEST_DIR + "actuators.csv")

    return sensor_df, actuator_df


def write_to_csv(sensor_df, actuator_df, time_range = (), name_suffix = ""):
    # Write the sensor and actuator data to a CSV file, if the time range is specified, only write the data within that range
    if time_range:
        sensor_df = sensor_df[(sensor_df["Time"] >= time_range[0]) & (sensor_df["Time"] <= time_range[1])]
        actuator_df = actuator_df[(actuator_df["Time"] >= time_range[0]) & (actuator_df["Time"] <= time_range[1])]
    if name_suffix:
        name_suffix = "_" + name_suffix
    sensor_df.to_csv(TEST_DIR + "sensors" + name_suffix + ".csv", index=False)
    actuator_df.to_csv(TEST_DIR + "actuators" + name_suffix + ".csv", index=False)


def parse_from_raw():
    sensor_lines = []
    with open(TEST_DIR + DATA_DIR_NAME + DATA_NAME, "r") as data:
        sensor_lines = data.readlines()

    actuator_lines = []
    with open(TEST_DIR + DATA_DIR_NAME + EVENT_NAME, "r") as event:
        actuator_lines = event.readlines()

    time_offset = parse_tools.get_seconds_hhmmss(parse_tools.split_space_comma(actuator_lines[0])[1])
    sensors = parse_sensor_lines(sensor_lines, time_offset)
    actuators = parse_actuator_lines(actuator_lines, time_offset)

    return sensors, actuators


def parse_sensor_lines(lines, time_offset):
    sensors = {}
    for line in lines:
        line_split = parse_tools.split_space_comma(line)
        time_hhmmss = line_split[1]
        time_ms = line_split[2]
        sensor_name = line_split[5]
        sensor_value = line_split[6]

        time = parse_tools.get_seconds_hhmmss(time_hhmmss) + float(time_ms)/1000 - time_offset
        if (time < 0):
            time += 86400   

        value = float(sensor_value[:-1])

        if sensor_name not in sensors:
            sensors[sensor_name] = [(time, value)]
        else:
            sensors[sensor_name].append((time, value))
    return sensors


def parse_actuator_lines(lines, time_offset):
    actuators = {}
    for line in lines:
        # Ignore extra lines
        if "ON" not in line and "OFF" not in line and "rotated" not in line:
            continue

        line_split = parse_tools.split_space_comma(line)
        time_hhmmss = line_split[1]
        time_ms = line_split[2]
        time = parse_tools.get_seconds_hhmmss(time_hhmmss) + float(time_ms)/1000 - time_offset
        if (time < 0):
            time += 86400

        actuator_name = ""
        actuator_value = 0
        
        if "rotated" in line:
            actuator_name = line_split[9].replace(":", "")
            actuator_value = line_split[-2]
        else:
            actuator_name = line_split[6].replace("'", "")
            actuator_value = 1 if ("ON" in line_split[-1]) else 0

        if actuator_name not in actuators:
            actuators[actuator_name] = [(time, actuator_value)]
        else:
            actuators[actuator_name].append((time, actuator_value))

    # Assign values of '' to all actuators at each time step they don't have a preexisting value
    for actuator in actuators:
        time_values = [val[0] for val in actuators[actuator]]
        for other_actuator in actuators:
            if other_actuator == actuator:
                continue
            other_time_values = [val[0] for val in actuators[other_actuator]]
            for time in time_values:
                if time not in other_time_values:
                    actuators[other_actuator].append((time, ""))
    for actuator in actuators:
        actuators[actuator].sort(key=lambda x: x[0])
            
    return actuators


if __name__ == "__main__":
    main()