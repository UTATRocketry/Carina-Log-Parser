
import os
import multiprocessing
import pandas as pd
from scipy.signal import savgol_filter
from queue import Queue
from . import parse_tools
import matplotlib.pyplot as plt

#Add mass flow rate column
# also fix actouator data so it mathes same time scale

def init(input_test_dir):
    global test_dir
    test_dir = input_test_dir


def has_been_parsed(test_dir):
    return os.path.exists(os.path.join(os.getcwd(), ".cache", test_dir, "sensors.csv")) and os.path.exists(os.path.join(os.getcwd(), ".cache", test_dir, "actuators.csv"))

def parse_from_raw(queue: Queue = None):
    sensor_lines = []
    with open(os.path.join(os.getcwd(), "Data", test_dir, "raw", "data.log"), "r") as data:
        sensor_lines = data.readlines()
    if queue: queue.put(2)

    actuator_lines = []
    with open(os.path.join(os.getcwd(), "Data", test_dir, "raw", "events.log"), "r") as event:
        actuator_lines = event.readlines()
    if queue: queue.put(3)

    time_offset = parse_tools.get_seconds_hhmmss(parse_tools.split_space_comma(actuator_lines[0])[1])
   
    num_cores = max(1, multiprocessing.cpu_count() - 4)
    segment_size = len(sensor_lines) // num_cores
    with multiprocessing.Pool(num_cores) as pool:
        segments = [(sensor_lines[i * segment_size:(i + 1) * segment_size], time_offset) for i in range(num_cores)]
        if len(sensor_lines) % num_cores != 0:
            segments.append((sensor_lines[num_cores * segment_size:], time_offset))

        results = pool.starmap(parse_sensor_lines, segments)
    
    sensors = results[0]
    i = 1
    while i < len(results):
        for sensor_name, data in results[i].items():
            if sensor_name in sensors:
                sensors[sensor_name].extend(data)
            else:
                sensors[sensor_name] = data
        i += 1
    if queue: queue.put(4)

    mass_flow_rate(sensors)
    if queue: queue.put(5)

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

        time = parse_tools.get_seconds_hhmmss(time_hhmmss) + float(time_ms) / 1000 - time_offset
        if time < 0:
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

def mass_flow_rate(sensors: dict) -> None: # remove noise first before caluclating derivative

    mass_flow = []
    time = [val[0] for val in sensors[list(sensors.keys())[0]]]
    h = time[1] - time[0]
    if "MFT" in sensors.keys():
        mass = [val[1] for val in sensors["MFT"]]
    else:
        mass = [val[1] for val in sensors["MOT"]]
    mass = savgol_filter(mass, len(mass)//300, 3)
    plt.plot(time, mass)
    plt.show()

    for i in range(len(mass) - 1): 
        res = (mass[i+1] - mass[i]) / h
        mass_flow.append((time[i], res))
    mass_flow.append((time[i+1], 0))
    sensors["MFR"] = mass_flow

def actuators_reformat(actuators: dict) -> None: 
    for actuator in actuators:
        state = 0
        for i in range(len(actuators[actuator])):
            if actuators[actuator][i][1] == 1: 
                state = 1
            elif actuators[actuator][i][1] == 0:
                state = 0
            else:
                actuators[actuator][i] = (actuators[actuator][i][0], state)


def dataframe_format(sensors: dict, actuators: dict):
    # Create a Pandas DataFrame with column names as the sensor and actuator names
    sensor_df = pd.DataFrame(columns=["Time"] + list(sensors.keys()))
    sensor_df["Time"] = [val[0] for val in sensors[list(sensors.keys())[0]]]
    for sensor in sensors:
        sensor_df[sensor] = [val[1] for val in sensors[sensor]]

    actuator_df = pd.DataFrame(columns=["Time"] + list(actuators.keys()))
    actuator_df["Time"] = [val[0] for val in actuators[list(actuators.keys())[0]]]
    actuators_reformat(actuators)
    for actuator in actuators:
        actuator_df[actuator] = [val[1] for val in actuators[actuator]]
    
    return sensor_df, actuator_df