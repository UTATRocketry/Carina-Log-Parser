import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import *
from scipy.interpolate import *

MY_DIR = "Data\\CF-O4\\"

SENSOR_FILE = "compiled\\sensors_selected.csv"
ACTUATOR_FILE = "compiled\\actuators_selected.csv"

def main():
    setup()
    #fill_study()
    flow_study()


def setup():
    os.chdir(MY_DIR)

    global sensors_df, actuators_df

    sensors_df = pd.read_csv(SENSOR_FILE)
    actuators_df = pd.read_csv(ACTUATOR_FILE)

    # Determine when the actuator "SVMOV" assumes the value 1
    sv_mov = actuators_df[actuators_df["SVMOV"] == 1]
    print(sv_mov)

    # Normalize all times to be referenced to the time of sv_mov
    time_offset = sv_mov["Time"].values[0]
    sensors_df["Time"] -= time_offset
    actuators_df["Time"] -= time_offset

    # Rename the sensor "PGOT" to "PGSO"
    sensors_df.rename(columns={"PGOT": "PGSO"}, inplace=True)


def fill_study():
    global sensors_df
    # Consider only time values from -725 to -300
    sensors_df = sensors_df[(sensors_df["Time"] >= -725) & (sensors_df["Time"] <= -25)]

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
    ax2[0].set_ylim(-2, 16)
    # Lower linewidth
    ax2[0].lines[0].set_linewidth(0.5)
    
    ax1.plot(sensors_df["Time"], sensors_df["MOT_filtered"], color="green")
    ax1.set_ylabel("Tank Mass (kg)")

    #ax2[1].plot(sensors_df["Time"], sensors_df["dMOT"], color="orange")
    # Horizontal line at 0
    #ax2[1].axhline(0, color="black", linestyle="-", linewidth=0.5)
    #ax2[1].set_ylabel("Mass Flow (kg/s)")

    ax1.set_xlabel("Time (s)")
    ax1.set_title("CF-O4 Fill Study")

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


    ax1.set_xlim(0, 14)
    ax1.set_xlabel("Time (s)")
    ax1.set_title("CF-O4 Flow Study")

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