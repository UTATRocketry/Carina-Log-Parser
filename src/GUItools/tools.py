
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

def custom_plot_caller(func, start_box: CTkEntry, end_box: CTkEntry, options: list, save: IntVar): 
    def call_func2():
        #try:
        start = start_box.get()
        end = end_box.get()
        if start == "" and end == "":
            func(options)
        elif start == "":
            func(options, end=float(end))
        elif end == "":
            func(options, start=float(start))
        else:
            start = float(start)
            end = float(end)
            if start > end:
                gui_error("End cannot be less then Start")
                append_to_log(f"Failed to create graphs as start time was greater then end time (start:{start}, end:{end})", "ERROR")
                return
            func(options, start, end, save.get())
        #except Exception:
            #gui_error("Invalid Start or End value")
    return call_func2

def add_caller(func, button: CTkButton):
    def call():
        func(button)
    return call

def gui_error(msg: str) -> None:
    messagebox.showerror(title="Program Error", message=msg)
    append_to_log(msg, "ERROR")

def clear_gui(window: CTk) -> None:
    for child in window.children.copy():
        window.children[child].destroy() 
    append_to_log("Clearing GUI Screen", "INFO") 

def single_plot(folder_name: str, axis: list, start = 0, end = None, save:int = 0) -> None: # this isnt wokring with actuatos and sensors on same graph so fix actustor length
    if not os.path.exists(os.path.join(os.getcwd(), "Data", folder_name, "Plots")):
        os.mkdir(os.path.join(os.getcwd(), "Data", folder_name, "Plots"))

    colors = ['b','g','r','c','m','y','k']
    name = ""
    for tup in axis[1:]:
        name += tup[0] + "&"

    start_ind = get_xaxis_index(axis[0][1], start)
    end_ind = get_xaxis_index(axis[0][1], end)
    xaxis = axis[0][1][start_ind:end_ind]
    fig, ax1 = plt.subplots()
    unit = [get_units(axis[1][0])]
    ax1.plot(xaxis, axis[1][1][start_ind:end_ind], label=axis[1][0], color=colors[0])
    ax1.set_ylabel(axis[1][0] + "(" + unit[0] + ")")
    ax1.set_title(f"{name} vs {axis[0][0]} Plot")
    ax1.set_xlabel(axis[0][0] + "(" + get_units(axis[0][0]) + ")")
    i= 1
    for tup in axis[2:]:
            ax = ax1.twinx()
            ax.plot(xaxis, tup[1][start_ind:end_ind], label=tup[0], color = colors[i])
            if get_units(tup[0]) not in unit:
                ax.set_ylabel(tup[0] + "(" + get_units(tup[0]) + ")") 
                unit.append(get_units(tup[0]))
            i += 1

    fig.legend()
    fig.tight_layout()
    fig.show()

    if save == 1:
        fig.savefig(os.path.join(os.getcwd(), "Data", folder_name, "Plots", f"{name} vs {axis[0][0]} Plot {t.strftime('%Hh%Mm%Ss', t.gmtime(start))};T{t.strftime('%Hh%Mm%Ss', t.gmtime(end))}.jpg"))

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
            plt.ylabel(column + "(" + get_units(column) + ")")
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
            
def get_units(name: str)->str:
    unit = name[0]
    if unit == "B" or unit == "S" or unit == "E" or "V" in name:
        return "On/Off"
    elif unit == "P":
        return "psi"
    elif unit == "M":
        return "kg"
    elif unit == "T":
        return "s"

            
def append_to_log(msg: str, mode: str = 'info') -> None:
    try:
        with open("program.log", "a") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], {mode}: {msg}\n')
            file.close()
    except Exception:
        gui_error("Error adding to program log")


