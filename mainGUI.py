from _thread import *
from customtkinter import *
from queue import Queue
from src.carina_parser import parser 
from src.GUItools import tools

class Carina_Plotter():
    def __init__(self, Title: str, size: str = "850x275") -> None:
        self.queue = Queue()
        self.window = CTk()
        self.window.geometry(size)
        set_appearance_mode("dark")
        set_default_color_theme("blue")
        self.window.title(Title)
        self.boot_screen()
        self.window.mainloop()
        
    
    def boot_screen(self) -> None:
        boot_frm = CTkFrame(master=self.window)
        greeting_lbl = CTkLabel(master=boot_frm, text="Welcome to the Carina Data Plotter", text_color="lightblue", font=("Arial", 30))
        prompt_frm = CTkFrame(master=boot_frm)
        prompt_lbl = CTkLabel(master=prompt_frm, text='Enter folder name which contains the data and events logs in a "\\raw" sub folder (Data\\_____\\raw):  ', font=("Arial", 16), anchor="center")
        folder_ent = CTkEntry(master=prompt_frm, font=("Arial", 12), width=150)
        start_program_btn = CTkButton(master=boot_frm, text="Start Program", font=("Arial", 20), width=120, anchor="center", command=tools.textbox_caller(self.loading_screen, folder_ent, self.window))
        greeting_lbl.pack(pady=20)
        prompt_lbl.pack(pady=5, padx=10)
        folder_ent.pack(pady=10, padx=10)
        prompt_frm.pack(padx=5, expand=True)
        start_program_btn.pack(pady=20)
        boot_frm.pack(pady=20, padx=30, fill="both", expand=True)

    def loading_screen(self, folder_name: str):
        self.folder_name = folder_name
        messages = ["Initalizing Parser", "Reading data.log", "Reading events.log", "Parsing Sensor Lines", "Parsing Actuator Lines", "Reformating Actuators Data and Converting to Dataframes", "Creating Sensor Graphs", "Creating Actuator Graphs", "Complete"]
        loading_frm = CTkFrame(master=self.window)
        loading_lbl = CTkLabel(master=loading_frm, text="Loading...", font=("Arial", 25))
        progress_bar = CTkProgressBar(master=loading_frm, orientation="horizontal", width=150, height=60)
        progress_bar.set(0)
        info_lbl = CTkLabel(master=loading_frm, text=messages[0], font=("Arial", 14))
        loading_lbl.pack(pady=15, padx=10)
        progress_bar.pack()
        info_lbl.pack(pady=5)
        loading_frm.pack(padx=20, pady=30, fill="both")
        self.window.update()
        start_new_thread(self.data_processor, (folder_name, ))
        progress = 0
        while progress < 1:
            self.window.update()
            val = self.queue.get()
            progress = val/8
            progress_bar.set(progress)
            loading_frm.children[list(loading_frm.children.keys())[-1]].destroy()
            info_lbl = CTkLabel(master=loading_frm, text=messages[val], font=("Arial", 14))
            info_lbl.pack(pady=5)
            self.window.update()

        tools.clear_gui(self.window)
        self.data_screen()

    def data_processor(self, folder_name: str):
        parser.init(folder_name)
        self.queue.put(1)
        sensors, actuators = parser.parse_from_raw(self.queue)
        self.queue.put(5)
        self.sensor_df, self.actuator_df = parser.dataframe_format(sensors, actuators)
        self.queue.put(6)
        tools.generate_plots(self.sensor_df, self.folder_name)
        self.queue.put(7)
        tools.generate_plots(self.actuator_df, self.folder_name, "actuators")
        self.queue.put(8)
        return
            
    def data_screen(self):
        data_frm = CTkFrame(master=self.window)
        title_lbl = CTkLabel(master=data_frm, text="Data Plot Controller", font=("Arial", 25), pady=10)
        log_lbl = CTkLabel(master=data_frm, text="Program Event Log", font=("Arial", 15), anchor="w")
        log_txt = CTkTextbox(master=data_frm, insertborderwidth=4)
        title_lbl.pack()
        log_lbl.pack()
        log_txt.pack(fill=X)
        data_frm.pack(pady=10, expand=True)
        
if __name__ == "__main__":
    app = Carina_Plotter("Carina Data Proccesor")