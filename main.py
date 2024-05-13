import csv
import os

SELECT_RANGE = True # Set to False if running for first time on new data
LOWER, UPPER = 6260, 6290 # Set the range
TEST_DIR = "CO-O1\\" # Specify the folder
DATA_NAME = "data.log" # Specify the data file
EVENT_NAME = "events.log" # Specify the event file
DATA_DIR_NAME = "0. Raw\\" # Specify the data directory
PARSED_DIR_NAME = "1. Parsed\\" # Specify the parsed data directory
SELECT_DIR_NAME = "3. Further Selected\\" # Specify the selected data directory

SENSOR_NAME = "Sensors\\"
ACTUATOR_NAME = "Actuators\\"


from utils import parse_tools


def create_dirs():
    if not os.path.exists(TEST_DIR + PARSED_DIR_NAME):
        os.mkdir(TEST_DIR + PARSED_DIR_NAME)
        os.mkdir(TEST_DIR + PARSED_DIR_NAME + SENSOR_NAME)
        os.mkdir(TEST_DIR + PARSED_DIR_NAME + ACTUATOR_NAME)
    if not os.path.exists(TEST_DIR + SELECT_DIR_NAME):
        os.mkdir(TEST_DIR + SELECT_DIR_NAME)
        os.mkdir(TEST_DIR + SELECT_DIR_NAME + SENSOR_NAME)
        os.mkdir(TEST_DIR + SELECT_DIR_NAME + ACTUATOR_NAME)



def main():
    os.chdir("Data")
    create_dirs()

    sensor_lines = []
    with open(TEST_DIR + DATA_DIR_NAME + DATA_NAME, "r") as data:
        sensor_lines = data.readlines()

    actuator_lines = []
    with open(TEST_DIR + DATA_DIR_NAME + EVENT_NAME, "r") as event:
        actuator_lines = event.readlines()

    time_offset = parse_tools.get_seconds_hhmmss(parse_tools.split_space_comma(actuator_lines[0])[1])
    sensors = parse_sensor_lines(sensor_lines, time_offset)
    actuators = parse_actuator_lines(actuator_lines, time_offset)

    for sensor in sensors:
        sensor_filename = sensor + ".csv"
        with open(TEST_DIR + PARSED_DIR_NAME + SENSOR_NAME + sensor_filename, 'w', newline='') as sensor_file:
            sensor_writer = csv.writer(sensor_file, delimiter=',')
            sensor_writer.writerows(sensors[sensor])

        if not SELECT_RANGE:
            continue

        with open(TEST_DIR + SELECT_DIR_NAME + SENSOR_NAME + sensor_filename, 'w', newline='') as sensor_file:
            sensor_writer = csv.writer(sensor_file, delimiter=',')
            for row in sensors[sensor]:
                if LOWER < row[0] < UPPER:
                    sensor_writer.writerow(row)


    for actuator in actuators:
        actuator_filename = actuator + ".csv"
        with open(TEST_DIR + PARSED_DIR_NAME + ACTUATOR_NAME + actuator_filename, 'w', newline='') as actuator_file:
            actuator_writer = csv.writer(actuator_file, delimiter=',')
            actuator_writer.writerows(actuators[actuator])

        if not SELECT_RANGE:
            continue

        with open(TEST_DIR + SELECT_DIR_NAME + ACTUATOR_NAME + actuator_filename, 'w', newline='') as actuator_file:
            actuator_writer = csv.writer(actuator_file, delimiter=',')
            for row in actuators[actuator]:
                if LOWER < row[0] < UPPER:
                    actuator_writer.writerow(row)


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
    print(actuators.keys())
    return actuators


if __name__ == "__main__":
    main()