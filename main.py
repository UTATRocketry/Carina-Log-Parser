import csv
import os

SELECT_RANGE = True # Set to False if running for first time on new data
LOWER, UPPER = 6190, 6220 # Set the range
FOLDER = "CO-O1\\" # Specify the folder
SELECT_NAME = "3. Further_Selected\\" # Change to '3. Further_Selected_Data' for different scales

def get_seconds_hhmmss(time_formatted):
    time_formatted = time_formatted.split(":")
    time_formatted = [int(t) for t in time_formatted]
    return time_formatted[0]*3600 + time_formatted[1]*60 + time_formatted[2]
  

def split_space_comma(line):
    delim_1 = line.split(",")
    delim_2 = []
    for d in delim_1:
        delim_2.extend(d.split(" "))
    return delim_2


def main():
    os.chdir("Data")
    folder = FOLDER
    data_folder = "0. Raw\\"
    data = "data.log"
    parsed_data_folder = "1. Parsed\\"
    selected_data_folder = SELECT_NAME
    

    lines = []
    with open(folder + data_folder + data, "r") as data:
        lines = data.readlines()

    sensors = {}

    time_offset = get_seconds_hhmmss(split_space_comma(lines[0])[1])

    for line in lines:
        line = split_space_comma(line)

        time = get_seconds_hhmmss(line[1]) - time_offset + float(line[2])/1000
        if (time < 0):
            time += 86400
        value = float(line[6][:-1])

        if line[5] in sensors:
            sensors[line[5]].append((time, value))
        else:
            sensors[line[5]] = [(time, value)]
        
    if not os.path.exists(folder + parsed_data_folder):
        os.mkdir(folder + parsed_data_folder)
    if not os.path.exists(folder + selected_data_folder):
        os.mkdir(folder + selected_data_folder)

    for sensor in sensors:
        sensor_filename = sensor + ".csv"
        with open(folder + parsed_data_folder + sensor_filename, 'w', newline='') as sensor_file:
            sensor_writer = csv.writer(sensor_file, delimiter=',')
            sensor_writer.writerows(sensors[sensor])

        if not SELECT_RANGE:
            continue

        with open(folder + selected_data_folder + sensor_filename, 'w', newline='') as sensor_file:
            sensor_writer = csv.writer(sensor_file, delimiter=',')
            for row in sensors[sensor]:
                if LOWER < row[0] < UPPER:
                    sensor_writer.writerow(row)

if __name__ == "__main__":
    main()