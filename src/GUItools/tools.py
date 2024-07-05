from customtkinter import *
from tkinter import messagebox
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t


def textbox_caller(func, text_box: CTkEntry):
    def call_func():
        text = text_box.get()
        folder = os.path.join(os.getcwd(), "Data", text, "raw")
        print(folder)        
        if not os.path.exists(os.path.join(folder, "data.log")) or not os.path.exists(os.path.join(folder, "events.log")):
            gui_error("File Path not Found")
            return
        append_to_log(f'Begining data parsing in {folder}', "INFO")
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
                func(end=float(end))
            elif end == "":
                func(start=float(start))
            else:
                start = float(start)
                end = float(end)
                if start > end:
                    gui_error("End time cannot be less then Start time")
                    append_to_log(f"Failed to create graphs as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                    return
                func(start, end)
        except Exception:
            gui_error("Invalid Start or End Time")
    return call_func2

def custom_plot_caller(func, start_box: CTkEntry, end_box: CTkEntry, option1: CTkOptionMenu, option2: CTkOptionMenu): 
    def call_func2():
        try:
            start = start_box.get()
            end = end_box.get()
            if start == "" and end == "":
                func(option1.get(), option2.get())
            elif start == "":
                func(option1.get(), option2.get(), end=float(end))
            elif end == "":
                func(option1.get(), option2.get(), start=float(start))
            else:
                start = float(start)
                end = float(end)
                if start > end:
                    gui_error("End cannot be less then Start")
                    append_to_log(f"Failed to create graphs as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                    return
                func(option1.get(), option2.get(), start, end)
        except Exception:
            gui_error("Invalid Start or End value")
    return call_func2

def gui_error(msg: str) -> None:
    messagebox.showerror(title="Program Error", message=msg)
    append_to_log(msg, "ERROR")

def clear_gui(window: CTk) -> None:
    for child in window.children.copy():
        window.children[child].destroy() 
    append_to_log("Clearing GUI Screen", "INFO") 

def single_plot(folder_name: str, xaxis: tuple, yaxis: tuple, start = 0, end = None) -> None:
    if not os.path.exists("Data\\" + folder_name + "Plots"):
        os.mkdir("Data\\" + folder_name + "Plots")

    start_ind = get_xaxis_index(xaxis[1], start)
    end_ind = get_xaxis_index(xaxis[1], end)
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
    start = get_xaxis_index(time, start_time)
    end = get_xaxis_index(time, end_time)
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

def get_xaxis_index(xaxis: list, given_time) -> int:
    if given_time == 0:
        return given_time
    elif given_time is None:
        return len(xaxis)
    else:
        for i, t in enumerate(xaxis):
            if t > given_time:
                return i - 1
            
def append_to_log(msg: str, mode: str = 'info') -> None:
    try:
        with open("program.log", "a") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {mode}: {msg}\n')
            file.close()
    except Exception:
        gui_error("Error adding to program log")

