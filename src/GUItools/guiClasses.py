from typing import Any, Tuple
from customtkinter import *

class OptionsBar(CTkFrame):
    def __init__(self, *args, master: Any, titles: list = [], choices: list = [], addcommand = None, removecommmand = None, padx:int = 0, pady:int = 0, font:tuple = ("Arial", 16), **kwargs)->None:
        super().__init__(*args, master=master, **kwargs)

        self.num_boxes = len(titles) + 2
        self.choices = choices
        self.padx = padx
        self.pady = pady
        self.font = font
        self.titles = titles
        self.option_boxes = []
        if addcommand is None:
            self.addcommand = self.add_box
        else:
            self.addcommand = addcommand
        if removecommmand is None:
            self.removecommand = self.remove_box
        else:
            self.removecommand = removecommmand

        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        for i, title in enumerate(titles):
            t = CTkLabel(master=self, text=title, font=self.font, anchor="center")
            t.grid(row=0, column=i, padx=self.padx, pady=self.pady, sticky="nsew")
            self.last_title = t

        for i in range(self.num_boxes - 2):
            opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
            opt.grid(row=1, column=i, padx=5, pady=5, sticky="ew")
            self.option_boxes.append(opt)

        self.addbutton = CTkButton(master=self, text="+", font=self.font, width = 30, command=self.addcommand)
        self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
        self.removebutton = CTkButton(master=self, text="-", font=self.font, width = 30, fg_color="darkred", hover_color="red", command=self.removecommand)
        self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")

    def add_box(self)->None:
        new_opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
        new_opt.grid(row=1, column=self.num_boxes - 2, padx=10, pady=5, sticky="ew")
        self.option_boxes.append(new_opt)
        self.num_boxes += 1
        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
        self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")
        self.last_title.grid(row=0, column=len(self.titles) - 1, columnspan=self.num_boxes, padx=self.padx, pady=self.pady, sticky="nsew")
        self.update()

    def remove_box(self):
        if self.num_boxes - 2 > len(self.titles):
            last_box = self.option_boxes.pop()
            last_box.destroy()
            self.num_boxes -= 1
            self.grid_columnconfigure(self.get_column_tuple(), weight=1)
            self.addbutton.grid(row=1, column=self.num_boxes - 2, padx=5, pady=5, sticky="ew")
            self.removebutton.grid(row=1, column=self.num_boxes - 1, padx=5, pady=5, sticky="ew")
            self.last_title.grid(row=0, column=len(self.titles) - 1, columnspan=self.num_boxes, padx=self.padx, pady=self.pady, sticky="nsew")
            self.update()

    def get_column_tuple(self) -> tuple:
        res = ()
        for i in range(self.num_boxes):
            res = (*res, i)
        return res

class RadioOptions(CTkFrame):
    pass # finsih later
        
