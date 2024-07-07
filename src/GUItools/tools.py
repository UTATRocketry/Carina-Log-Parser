
import os
import pandas as pd
import matplotlib.pyplot as plt
import time as t
from customtkinter import *
from tkinter import messagebox
from datetime import datetime


def textbox_caller(func, text_box: CTkEntry, save: IntVar):
    def call_func():
        text = text_box.get()
        folder = os.path.join(os.getcwd(), "Data", text, "raw")
        if not os.path.exists(os.path.join(folder, "data.log")) or not os.path.exists(os.path.join(folder, "events.log")):
            gui_error("File Path not Found")
            return
        append_to_log(f'Begining data parsing in {folder}', "INFO")
        func(text, save.get())
    return call_func

def replot_caller(func, start_box: CTkEntry, end_box: CTkEntry, save: IntVar):
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
                func(start, end, save.get())
        except Exception:
            gui_error("Invalid Start or End Time")
    return call_func2

def custom_plot_caller(func, start_box: CTkEntry, end_box: CTkEntry, option1: CTkOptionMenu, option2: CTkOptionMenu, save: IntVar): 
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
                func(option1.get(), option2.get(), start, end, save.get())
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

# add units
def single_plot(folder_name: str, xaxis: tuple, yaxis: tuple, start = 0, end = None, save:int = 0) -> None:
    if not os.path.exists(os.path.join(os.getcwd(), "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(), "Data", folder_name, "Plots"))

    start_ind = get_xaxis_index(xaxis[1], start)
    end_ind = get_xaxis_index(xaxis[1], end)
    p = plt.figure(f"{yaxis[0]}vs{xaxis[0]}")
    plt.plot(xaxis[1][start_ind:end_ind], yaxis[1][start_ind:end_ind])
    plt.title(f"{yaxis[0]} vs {xaxis[0]} Plot")
    plt.xlabel(get_axis_title(xaxis[0]))
    plt.ylabel(get_axis_title(yaxis[0]))
    p.show()

    if save == 1:
        p.savefig(os.path.join(os.getcwd(), "Data", folder_name, "Plots", f"{yaxis[0]} vs {xaxis[0]} Plot {t.strftime('%Hh%Mm%Ss', t.gmtime(start))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end))}.jpg"))

def generate_plots(folder_name: str, dataframe: pd.DataFrame, type: str = "sensor", start_time = 0, end_time = None, save:int = 0) -> None:
    if not os.path.exists(os.path.join(os.getcwd(), "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(),"Data", folder_name, "Plots"))

    time = dataframe["Time"].to_list()
    start = get_xaxis_index(time, start_time)
    end = get_xaxis_index(time, end_time)
    if start == end: start -= 1
    time = time[start:end]
    if type.lower() == "actuator":
        time.append(time[-1] + 0.01)
    for column in dataframe.columns:
        if column != "Time":
            p = plt.figure(column + "vs Time Plot")
            data = dataframe[column].to_list()[start:end]
            if type.lower() == "sensor":
                plt.plot(time, data)
            elif type.lower() == "actuator":
                plt.stairs(data, time)
            plt.title(column + " vs Time Plot")
            plt.xlabel("Time (s)")
            plt.ylabel(get_axis_title(column))
            p.show() 
            if save == 1:
                p.savefig(os.path.join(os.getcwd(), "Data", folder_name, "Plots", f"{column} vs Time Plot T[{t.strftime('%Hh%Mm%Ss', t.gmtime(start_time))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end_time))}].jpg"))

def get_xaxis_index(xaxis: list, given_time) -> int:
    if given_time == 0:
        return given_time
    elif given_time is None:
        return len(xaxis)
    else:
        for i, t in enumerate(xaxis):
            if t > given_time:
                return i - 1
            
def get_axis_title(name: str):
    axis_title = name + " ("
    unit = name[0]
    if unit == "P":
        axis_title += "psi)"
    if unit == "M":
        axis_title += "kg)"
    if unit == "B" or unit == "S" or unit == "E":
        axis_title += "On/Off)"
    return axis_title

            
def append_to_log(msg: str, mode: str = 'info') -> None:
    try:
        with open("program.log", "a") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], {mode}: {msg}\n')
            file.close()
    except Exception:
        gui_error("Error adding to program log")


