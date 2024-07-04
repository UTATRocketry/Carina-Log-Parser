from customtkinter import *
from tkinter import messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t

def textbox_caller(func, text_box: CTkEntry):
    def call_func():
        text = text_box.get() + "\\"
        if not os.path.exists("Data\\" + text + "raw\\data.log") or not os.path.exists("Data\\" + text + "raw\\events.log"):
            gui_error("File Path not Found")
            return
        func(text)
    return call_func

def replot_caller(func, start_box: CTkEntry, end_box: CTkEntry):
    def call_func2():
        try:
            start = start_box.get()
            end = end_box.get()
            if start == "" and end == "":
                func()
            elif start == "":
                func(end=int(end))
            elif end == "":
                func(start=int(start))
            else:
                start = int(start)
                end = int(end_box)
                if start > end:
                    gui_error("End time cannot be less then Start time")
                    return
                func(start, end)
        except Exception:
            gui_error("Invalid Start or End Time")
    return call_func2

def custom_plot_caller(func, start_box: CTkEntry, end_box: CTkEntry, option1: CTkOptionMenu, option2: CTkOptionMenu): # debug 
    def call_func2():
        try:
            start = start_box.get()
            end = end_box.get()
            if start == "" and end == "":
                func(option1.get(), option2.get())
            elif start == "":
                func(option1.get(), option2.get(), end=int(end))
            elif end == "":
                func(option1.get(), option2.get(), start=int(start))
            else:
                start = int(start)
                end = int(end_box)
                if start > end:
                    gui_error("End time cannot be less then Start time")
                    return
                func(option1.get(), option2.get(), start, end)
        except Exception:
            gui_error("Invalid Start or End Time")
    return call_func2

def gui_error(msg: str) -> None:
    messagebox.showerror(title="Program Error", message=msg)

def clear_gui(window: CTk) -> None:
    for child in window.children.copy():
        window.children[child].destroy()  

def single_plot(folder_name: str, xaxis: tuple, yaxis: tuple, start = 0, end = None) -> None:
    if not os.path.exists("Data\\" + folder_name + "Plots"):
        os.mkdir("Data\\" + folder_name + "Plots")

    start_ind = get_time_index(xaxis[1], start)
    end_ind = get_time_index(xaxis[1], end)
    plt.plot(xaxis[1][start_ind:end_ind], yaxis[1][start_ind:end_ind])
    plt.title(f"{yaxis[0]} vs {xaxis[0]} Plot")
    plt.xlabel(xaxis[0])
    plt.ylabel(yaxis[0])
    plt.savefig(f"Data\\{folder_name}Plots\\{yaxis[0]}vs{xaxis[0]}.jpg")
    plt.close()

def generate_plots(folder_name: str, dataframe: pd.DataFrame, type: str = "sensor", start_time = 0, end_time = None) -> None:
    if not os.path.exists("Data\\" + folder_name + "Plots"):
        os.mkdir("Data\\" + folder_name + "Plots")

    time = dataframe["Time"].to_list()
    start = get_time_index(time, start_time)
    end = get_time_index(time, end_time)
    time = time[start:end]
    if type.lower() == "actuator":
        time.append(time[-1] + 0.01)

    for column in dataframe.columns:
        if column != "Time": 
            data = dataframe[column].to_list()[start:end]
            if type.lower() == "sensor":
                plt.plot(time, data)
            elif type.lower() == "actuator":
                plt.stairs(data, time)
            plt.title(column + " vs Time Plot")
            plt.xlabel("Time (s)")
            plt.ylabel(column)
            plt.savefig(f"Data\\{folder_name}Plots\\{column}_[T{t.strftime('%Hh%Mm%Ss', t.gmtime(start_time))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end_time))}].jpg")
            plt.close()

def get_time_index(time: list, given_time) -> int:
    if given_time == 0:
        return given_time
    elif given_time is None:
        return len(time)
    else:
        for i, t in enumerate(time):
            if t > given_time:
                return i - 1

