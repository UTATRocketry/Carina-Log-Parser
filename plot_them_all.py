import pandas as pd
import matplotlib.pyplot as plt

test_ids = ["CF-O1", "CF-O2", "CF-O3", "CF-O4", "CF-O5"]

SENSOR_FILE = "compiled\\sensors_selected.csv"
ACTUATOR_FILE = "compiled\\actuators_selected.csv"

def main():
    global sensors_dfs, actuators_dfs
    sensors_dfs = []
    actuators_dfs = []
    for test_id in test_ids:
        setup(test_id)
    flow_study()


def setup(test_id):
    global sensors_dfs, actuators_dfs

    sensors_df = pd.read_csv("Data\\" + test_id + "\\" + SENSOR_FILE)
    actuators_df = pd.read_csv("Data\\" + test_id + "\\" + ACTUATOR_FILE)


    if (test_id == "CF-O1"):
         # Rename the sensors ("OXGS-PT-002", "OXGS-PT-001", "OXFL-PT-001", "OXFL-LC-001", "OXCC-PT-001") to ("PGS", "PGSO", "POTT", "MOT", "POTB")
        sensors_df.rename(columns={"OXGS-PT-002": "PGS", "OXGS-PT-001": "PGSO", "OXFL-PT-001": "POTT", "OXFL-LC-001": "MOT", "OXCC-PT-001": "POTB"}, inplace=True)
        # Rename the actuators ("OXGS-O-FILL", "OXGS-P-FILL", "ENABLE OXFL-A-FILL", "OXFL-A-FILL", "OXFL-A-VENT", "OXFL-A-DUMP", "OXGS-A-FILL", "OXGS-MOV", "OXGS-A-DUMP")
        # to ("BVGSO", "BVGSP", "ENABLE_BVOTP", "BVOTP", "SVOTV", "SVOTD", "BVGS", "SVMOV", "SVGSD")
        actuators_df.rename(columns={"OXGS-O-FILL": "BVGSO", "OXGS-P-FILL": "BVGSP", "ENABLE OXFL-A-FILL": "ENABLE_BVOTP", "OXFL-A-FILL": "BVOTP", "OXFL-A-VENT": "SVOTV", "OXFL-A-DUMP": "SVOTD", "OXGS-A-FILL": "BVGS", "OXGS-MOV": "SVMOV", "OXGS-A-DUMP": "SVGSD"}, inplace=True)
    if (test_id == "CF-O2"):
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

    sensors_dfs.append(sensors_df)


def flow_study():
    global sensors_dfs
    
    fig, ax1 = plt.subplots(5, 1)
    ax2 = []
    for ax in ax1:
        ax2.append(ax.twinx())
    
    for i in range(5):
        sensors_df = sensors_dfs[i]
        lns1 = ax1[i].plot(sensors_df["Time"], sensors_df["POTB"], color="blue")
        if (test_ids[i] == "CF-O1"):
            lns2 = ax1[i].plot(sensors_df["Time"], sensors_df["POTT"], color="navy")
        else:
            lns2 = ax1[i].plot(sensors_df["Time"], sensors_df["PCC"], color="purple")
        
        ax1[i].set_ylabel("Pressure (psi)")
        ax1[i].set_ylim(0, 1000)

        lns3 = ax2[i].plot(sensors_df["Time"], sensors_df["MOT"], color="red")
        ax2[i].set_ylabel("Tank Mass (kg)")
        ax2[i].set_ylim(0, 6.6)

        if (test_ids[i] == "CF-O1"):
            ax1[i].legend(lns1+lns2+lns3, ["POTB", "POTT", "MOT"], loc="upper right")
        else:
            ax1[i].legend(lns1+lns2+lns3, ["POTB", "PCC", "MOT"], loc="upper right")


        ax1[i].set_xlim(0, 14)
        ax1[i].set_xlabel("Time (s)")
        ax1[i].set_title(test_ids[i] + " Flow Study")

        # Minor gridlines
        ax1[i].minorticks_on()
        ax1[i].grid(which="both", linestyle="--", linewidth=0.5)

    plt.gcf().set_size_inches(12, 25)
    plt.tight_layout()
    plt.savefig("flow_study.png", dpi=500)
    #plt.show()


if __name__ == "__main__":
    main()