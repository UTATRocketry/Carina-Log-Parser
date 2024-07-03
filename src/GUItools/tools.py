from customtkinter import *
from tkinter import messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t

def textbox_caller(func, text_box: CTkEntry, window: CTk = None):
    def call_func():
        text = text_box.get() + "\\"
        if not os.path.exists("Data\\" + text + "raw\\data.log") or not os.path.exists("Data\\" + text + "raw\\events.log"):
            gui_error("File Path not Found, Try Again")
            return
        if window: 
            clear_gui(window)
        func(text)
    return call_func

def gui_error(msg: str) -> None:
    messagebox.showerror(title="Program Error", message=msg)

def clear_gui(window: CTk) -> None:
    for child in window.children.copy():
        window.children[child].destroy()  

def generate_plots(dataframe: pd.DataFrame, folder_name: str, type: str = "sensor", start_time = 0, end_time = None) -> None:
    if not os.path.exists("Data\\" + folder_name + "Plots"):
        os.mkdir("Data\\" + folder_name + "Plots")

    time = dataframe["Time"].to_list()
    start_time = get_time_index(time, start_time)
    end_time = get_time_index(time, end_time)
    time = time[start_time:end_time]
    if type.lower() == "actuators":
        time.append(time[-1] + 0.01)

    for column in dataframe.columns:
        if column != "Time": 
            data = dataframe[column].to_list()[start_time:end_time]
            if type.lower() == "sensor":
                plt.plot(time, data)
            elif type.lower() == "actuators":
                plt.stairs(data, time)
            plt.title(column + " vs Time Plot")
            plt.xlabel("Time (s)")
            plt.ylabel(column)
            plt.savefig(f"Data\\{folder_name}Plots\\{column}_[T{t.strftime('%Hh%Mm%Ss', t.gmtime(time[start_time]))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(time[end_time - 1]))}].jpg")
            plt.close()

def get_time_index(time: list, given_time) -> int:
    if given_time == 0:
        return 0
    elif given_time is None:
        return len(time)
    else:
        for t, i in enumerate(time):
            if t > given_time:
                return i - 1

