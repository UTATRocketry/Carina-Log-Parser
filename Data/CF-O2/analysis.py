import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import *
from scipy.interpolate import *

test_id = "CF-O2"
MY_DIR = "Data\\" + test_id + "\\"

FILL = False
SENSOR_FILE = "compiled\\sensors_selected.csv"
ACTUATOR_FILE = "compiled\\actuators_selected.csv"
#SENSOR_FILE = "compiled\\sensors_compiled.csv"
#ACTUATOR_FILE = "compiled\\actuators_compiled.csv"

def main():
    setup()
    if FILL: fill_study()
    else: flow_study()


def setup():
    os.chdir(MY_DIR)

    global sensors_df, actuators_df

    sensors_df = pd.read_csv(SENSOR_FILE)
    actuators_df = pd.read_csv(ACTUATOR_FILE)

    # Rename the sensors ("OXGS-PT-002", "OXGS-PT-001", "OXFL-PT-001", "OXFL-LC-001", "OXCC-PT-001") to ("PGS", "PGSO", "POTB", "MOT", "PCC")
    sensors_df.rename(columns={"OXGS-PT-002": "PGS", "OXGS-PT-001": "PGSO", "OXFL-PT-001": "POTB", "OXFL-LC-001": "MOT", "OXCC-PT-001": "PCC"}, inplace=True)

    # Rename the actuators ("OXGS-O-FILL", "OXGS-P-FILL", "ENABLE OXFL-A-FILL", "OXFL-A-FILL", "OXFL-A-VENT", "OXFL-A-DUMP", "OXGS-A-FILL", "OXGS-MOV", "OXGS-A-DUMP")
    # to ("BVGSO", "BVGSP", "ENABLE_BVOTP", "BVOTP", "SVOTV", "SVOTD", "BVGS", "SVMOV", "SVGSD")
    actuators_df.rename(columns={"OXGS-O-FILL": "BVGSO", "OXGS-P-FILL": "BVGSP", "ENABLE OXFL-A-FILL": "ENABLE_BVOTP", "OXFL-A-FILL": "BVOTP", "OXFL-A-VENT": "SVOTV", "OXFL-A-DUMP": "SVOTD", "OXGS-A-FILL": "BVGS", "OXGS-MOV": "SVMOV", "OXGS-A-DUMP": "SVGSD"}, inplace=True)

    # Determine when the actuator "SVMOV" assumes the value 1
    sv_mov = actuators_df[actuators_df["SVMOV"] == 1]
    print(sv_mov)

    # Normalize all times to be referenced to the time of sv_mov
    time_offset = sv_mov["Time"].values[0]
    sensors_df["Time"] -= time_offset
    actuators_df["Time"] -= time_offset




def fill_study():
    global sensors_df
    # Consider only time values from -1100 to -100
    sensors_df = sensors_df[(sensors_df["Time"] >= -1700) & (sensors_df["Time"] <= -100)]

    # Apply a butterworth filter to the "MOT" sensor. Assume a sampling frequency of 20Hz. Use a cutoff frequency of 1Hz.
    b, a = butter(4, 10, "low", fs=40)
    sensors_df["MOT_filtered"] = filtfilt(b, a, sensors_df["MOT"])

    # Take the smoothed derivative of the "MOT_filtered" sensor to get the mass flow rate "dMOT"
    sensors_df["dMOT"] = savgol_filter(sensors_df["MOT_filtered"], 11, 3, deriv=1, delta=1/20)


    # Plot "PGS" - "POTB" as "Pressure difference (psi)" on one axis. Plot "MOT" on another axis as "Tank mass (kg)". Title fill study.

    fig, ax1 = plt.subplots(1, 1, sharex=True)
    ax2 = [0, 0]
    ax2[0] = ax1.twinx()
    #ax2[1] = ax1[1].twinx()

    ax1.plot(sensors_df["Time"], sensors_df["MOT"], color="red")
    ax1.plot(sensors_df["Time"], sensors_df["MOT_filtered"], color="green")
    # Line at 0
    ax2[0].axhline(0, color="black", linestyle="-", linewidth=0.5)
    ax1.set_ylabel("Tank Mass (kg)")

    ax2[0].plot(sensors_df["Time"], sensors_df["PGS"] - sensors_df["POTB"], color="blue")
    ax2[0].set_ylabel("Pressure Difference (psi)")
    ax2[0].set_ylim(35, 65)
    # Lower linewidth
    ax2[0].lines[0].set_linewidth(0.5)
    
    ax1.plot(sensors_df["Time"], sensors_df["MOT_filtered"], color="green")
    ax1.set_ylabel("Tank Mass (kg)")

    #ax2[1].plot(sensors_df["Time"], sensors_df["dMOT"], color="orange")
    # Horizontal line at 0
    #ax2[1].axhline(0, color="black", linestyle="-", linewidth=0.5)
    #ax2[1].set_ylabel("Mass Flow (kg/s)")

    ax1.set_xlabel("Time (s)")
    ax1.set_title(test_id + " Fill Study")

    # Minor gridlines
    ax2[0].minorticks_on()
    #ax1.minorticks_on()
    #ax1.grid(which="major", linestyle="--", linewidth=0.5)
    ax2[0].grid(which="both", linestyle="--", linewidth=0.5)

    # Make it look nice
    plt.xlabel("Time (s)")
    plt.gcf().set_size_inches(12, 5)
    plt.tight_layout()

    # Save the plot in fullscreen resolution
    
    plt.savefig("fill_study.png", dpi=500)

    plt.show()


def flow_study():
    global sensors_df
    # Consider only time values from 0 to 14
    #sensors_df = sensors_df[(sensors_df["Time"] >= -5) & (sensors_df["Time"] <= 20)]

    fig, ax1 = plt.subplots(1, 1, sharex=True)
    ax2 = ax1.twinx()
    #ax2[1] = ax1[1].twinx()


    lns1 = ax1.plot(sensors_df["Time"], sensors_df["POTB"], color="blue")
    lns2 = ax1.plot(sensors_df["Time"], sensors_df["PCC"], color="purple")
    ax1.set_ylabel("Pressure (psi)")
    ax1.set_ylim(0, 800)

    lns3 = ax2.plot(sensors_df["Time"], sensors_df["MOT"], color="red")
    ax2.set_ylabel("Tank Mass (kg)")
    ax2.set_ylim(0, 5.2)

    ax1.legend(lns1+lns2+lns3, ["POTB", "PCC", "MOT"], loc="upper right")

    # yline when BVOTP changes
    #bv_otp = actuators_df[actuators_df["BVOTP"].diff() != 0]
    #print(bv_otp)    

    bv_otp = actuators_df[actuators_df["BVOTP"] != '']
    # Plot a vertical line at each time step when BVOTP changes
    for time in bv_otp["Time"]:
        # Print the entry
        print(actuators_df[actuators_df["Time"] == time])
        ax1.axvline(time, color="black", linestyle="--", linewidth=0.5)


    ax1.set_xlim(0, 14)
    ax1.set_xlabel("Time (s)")
    ax1.set_title(test_id + " Flow Study")

    # Minor gridlines
    ax1.minorticks_on()
    ax1.grid(which="both", linestyle="--", linewidth=0.5)

    plt.gcf().set_size_inches(12, 5)
    plt.tight_layout()

    # Save the plot in fullscreen resolution
    plt.savefig("flow_study.png", dpi=500)
    plt.show()


if __name__ == "__main__":
    main()