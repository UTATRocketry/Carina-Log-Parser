from _thread import *
from customtkinter import *
from queue import Queue
from datetime import datetime
from src.carina_parser import parser 
from src.GUItools import tools


class Carina_Plotter(CTk):
    def __init__(self, Title: str) -> None:
        super().__init__()
        self.queue = Queue()
        with open("program.log", "w") as file:
            file.write(f'[T {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}], INFO: Program Started\n')
            file.close()
        set_appearance_mode("dark")
        set_default_color_theme("blue")
        self.title(Title)
        self.boot_screen()
        self.mainloop()
        
    def boot_screen(self) -> None:
        tools.clear_gui(self)
        boot_frm = CTkFrame(master=self)
        greeting_lbl = CTkLabel(master=boot_frm, text="Welcome to the Carina Data Plotter", text_color="lightblue", font=("Arial", 30))
        prompt_frm = CTkFrame(master=boot_frm)
        prompt_lbl = CTkLabel(master=prompt_frm, text='Enter folder name which contains the data and events logs in a "\\raw" sub folder (Data\\_____\\raw):  ', font=("Arial", 16), anchor="center")
        folder_ent = CTkEntry(master=prompt_frm, font=("Arial", 12), width=150)
        start_program_btn = CTkButton(master=boot_frm, text="Start Program", font=("Arial", 20), width=120, anchor="center", command=tools.textbox_caller(self.loading_screen, folder_ent))
        greeting_lbl.pack(pady=20)
        prompt_lbl.pack(pady=5, padx=10)
        folder_ent.pack(pady=10, padx=10)
        prompt_frm.pack(padx=5, expand=True)
        start_program_btn.pack(pady=20)
        boot_frm.pack(pady=20, padx=30, fill="both", expand=True)

    def loading_screen(self, folder_name: str) -> None:
        tools.clear_gui(self)
        self.folder_name = folder_name
        messages = ["Initalizing Parser", "Reading data.log", "Reading events.log", "Parsing Sensor Lines", "Parsing Actuator Lines", "Reformating Actuators Data and Converting to Dataframes", "Creating Graphs", "Complete"]
        loading_frm = CTkFrame(master=self)
        loading_lbl = CTkLabel(master=loading_frm, text="Loading...", font=("Arial", 25))
        progress_bar = CTkProgressBar(master=loading_frm, orientation="horizontal", width = 190, height = 25)
        progress_bar.set(0)
        info_lbl = CTkLabel(master=loading_frm, text=messages[0], font=("Arial", 14))
        loading_lbl.pack(pady=15)
        progress_bar.pack(padx = 30,)
        info_lbl.pack(pady=5, padx=5)
        loading_frm.pack(padx=20, pady=30)
        self.update()
        start_new_thread(self.data_processor, (folder_name, ))
        progress = 0
        while progress < 0.85:
            val = self.queue.get()
            progress = val/7
            progress_bar.set(progress)
            info_lbl.configure(text=messages[val])
            tools.append_to_log(messages[val], "INFO")
            self.update()
        self.plot_all()
        progress_bar.set(1)
        info_lbl.configure(text=messages[7])
        self.update()
        tools.append_to_log(f"Data Parsing and Plotting Complete", "INFO")
        self.data_screen()

    def data_processor(self, folder_name: str) -> None:
        self.queue.put(0)
        parser.init(folder_name)
        self.queue.put(1)
        sensors, actuators = parser.parse_from_raw(self.queue)
        self.queue.put(5)
        self.sensor_df, self.actuator_df = parser.dataframe_format(sensors, actuators)
        self.queue.put(6)
        return
    
    def plot_all(self, start_time = 0, end_time = None) -> None:
        tools.generate_plots(self.folder_name, self.sensor_df, "sensor", start_time, end_time)
        tools.generate_plots(self.folder_name, self.actuator_df, "actuator", start_time, end_time)
        tools.append_to_log(f'Generated {len(self.sensor_df.columns) + len(self.actuator_df.columns) - 2} Plots', "INFO")

    def custom_plot(self, xaxis_key: str, yaxis_key: str, start = 0, end = None):
        if xaxis_key in self.sensor_df.columns:
            xaxis = (xaxis_key, self.sensor_df[xaxis_key].to_list())
        else:
            xaxis = (xaxis_key, self.actuator_df[xaxis_key].to_list())
        if yaxis_key in self.sensor_df.columns:
            yaxis = (yaxis_key, self.sensor_df[yaxis_key].to_list())
        else:
            yaxis = (yaxis_key, self.actuator_df[yaxis_key].to_list())
        tools.single_plot(self.folder_name, xaxis, yaxis, start, end)
        tools.append_to_log("Created a new custom plot", "INFO:")
            
    def data_screen(self) -> None:
        tools.clear_gui(self)

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        title_frm = CTkFrame(master=self)
        title_frm.grid_columnconfigure((0, 1), weight=1)
        title_lbl = CTkLabel(master=title_frm, text="Data Plot Controller", text_color="lightblue", font=("Arial", 30))
        title_lbl.grid(row = 0, column = 0, pady=30, columnspan=2, sticky="nsew")
        title_frm.grid(row = 0, column = 0, padx=10, pady=5, columnspan=3, sticky="nsew")

        replot_frm = CTkFrame(master=self)
        replot_frm.grid_columnconfigure((0, 1), weight=1)
        replot_frm.grid_rowconfigure((0, 1, 2, 3), weight=1)
        replot_lbl = CTkLabel(master=replot_frm, text="Replot All", font=("Arial", 22))
        replot_lbl.grid(row = 0, column = 0, padx=10, pady=10, columnspan=2, sticky="ew")
        start_time_lbl = CTkLabel(master=replot_frm, text="Start Time:", font=("Arial", 14))
        start_time_lbl.grid(row=1, column=0, pady=10, padx=(10, 5), sticky="ew")
        start_time_ent = CTkEntry(master=replot_frm, font=("Arial", 14), width=60)
        start_time_ent.grid(row=1, column=1, pady=10, padx=(0, 10), sticky="ew")
        end_time_lbl = CTkLabel(master=replot_frm, text="End Time:", font=("Arial", 14))
        end_time_lbl.grid(row=2, column=0, pady=10, padx=(10, 5), sticky="ew")
        end_time_ent = CTkEntry(master=replot_frm, font=("Arial", 14), width=60)
        end_time_ent.grid(row=2, column=1, pady=10, padx=(0, 10), sticky="ew")
        replot_btn = CTkButton(master=replot_frm, text="Replot", width=140, font=("Arial", 18), anchor="center", command=tools.replot_caller(self.plot_all, start_time_ent, end_time_ent))
        replot_btn.grid(row=3, column=0, columnspan=2, pady=20, padx=10)
        replot_frm.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), rowspan=3, sticky="nsew")

        custom_plot_frm = CTkFrame(master=self)
        custom_plot_frm.grid_columnconfigure((0, 1, 2, 3), weight=1)
        custom_plot_frm.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        cutom_plot_lbl = CTkLabel(master=custom_plot_frm, text="Create Custom Plot", font=("Arial", 22))
        cutom_plot_lbl.grid(row = 0, column = 0, padx=10, pady=10, columnspan=4, sticky="ew")
        start_lbl = CTkLabel(master=custom_plot_frm, text="Start:", font=("Arial", 16))
        start_lbl.grid(row=1, column=0, pady=10, padx=(10, 0), sticky="ew")
        start_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=60)
        start_ent.grid(row=1, column=1, pady=10, padx=(0, 10), sticky="ew")
        end_lbl = CTkLabel(master=custom_plot_frm, text="End:", font=("Arial", 16))
        end_lbl.grid(row=1, column=2, pady=10, padx=(10, 0), sticky="ew")
        end_ent = CTkEntry(master=custom_plot_frm, font=("Arial", 16), width=60)
        end_ent.grid(row=1, column=3, pady=10, padx=(0, 10), sticky="ew")
        xaxis_lbl = CTkLabel(master=custom_plot_frm, text="X Axis", font=("Arial", 16), anchor="center")
        xaxis_lbl.grid(row=2, column=0, padx=20, pady=5, columnspan=2, sticky="ew")
        yaxis_lbl = CTkLabel(master=custom_plot_frm, text="Y Axis", font=("Arial", 16), anchor="center")
        yaxis_lbl.grid(row=2, column=2, padx=20, pady=5, columnspan=2, sticky="ew")
        xaxis_opt = CTkOptionMenu(master=custom_plot_frm, font=("Arial", 14), values=self.sensor_df.columns.to_list() + self.actuator_df.columns.to_list(), anchor="center")
        xaxis_opt.grid(row=3, column=0, padx=20, pady=5, columnspan=2, sticky="ew")
        yaxis_opt = CTkOptionMenu(master=custom_plot_frm, font=("Arial", 14), values=self.sensor_df.columns.to_list() + self.actuator_df.columns.to_list(), anchor="center")
        yaxis_opt.grid(row=3, column=2, padx=20, pady=5, columnspan=2, sticky="ew")
        custom_plot_btn = CTkButton(master=custom_plot_frm, text="Create Plot", font=("Arial", 18), command=tools.custom_plot_caller(self.custom_plot, start_ent, end_ent, xaxis_opt, yaxis_opt)) # change command
        custom_plot_btn.grid(row=4, column=1, columnspan=2, pady=(25, 20), sticky="ew")
        custom_plot_frm.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), rowspan=5, columnspan=2, sticky="nsew")

        visual_switch = CTkSwitch(master=self, text="Visual Mode", command=self.switch_visual_mode)
        visual_switch.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="")

        buttons_frm = CTkFrame(master=self)
        buttons_frm.grid_columnconfigure((0, 1), weight=1)
        back_btn = CTkButton(master=buttons_frm, text="Return", font=("Arial", 16), anchor="center", command=self.boot_screen)
        back_btn.grid(row=0, column=0, pady=10, padx=(10, 5), sticky="nsew")
        log_btn = CTkButton(master=buttons_frm, text="Logs", font=("Arial", 16), anchor="center", command=self.logs_screen)
        log_btn.grid(row=0, column=1, pady=10, padx=(5, 10), sticky="nsew")
        buttons_frm.grid(row=5, column=0, padx=5, pady=(0, 10), sticky="nsew")
    
    def logs_screen(self):
        tools.clear_gui(self)
        logs_lbl = CTkLabel(master=self, text="Program Log", font=("Arial", 20))
        logs_lbl.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="nsew")
        return_btn = CTkButton(master=self, text="Return", font=("Arial", 18), command=self.data_screen)
        return_btn.grid(row=0, column=2, padx=10, pady=(20, 10))
        logs_txt = CTkTextbox(master=self, font=("Arial", 16), width=700)
        logs_txt.grid(row=1, column=0, columnspan=3, rowspan=5, padx=10, pady=10, sticky="nsew")
        with open("program.log", "r") as file:
            for line in file:
                logs_txt.insert("end", line)
        logs_txt.configure(state="disabled")
        logs_txt.see("end")

    def switch_visual_mode(self):
        if get_appearance_mode() == "Dark":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")
        tools.append_to_log(f"Changed appearance mode to {get_appearance_mode()}", "INFO")
        
if __name__ == "__main__":
    app = Carina_Plotter("Carina Data Proccesor")