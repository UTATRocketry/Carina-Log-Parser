from typing import Any, Tuple
from customtkinter import *

class OptionsBar(CTkFrame):
    def __init__(self, *args, master: Any, titles: list = [], choices: list = [], command = None, padx:int = 0, pady:int = 0, font:tuple = ("Arial", 16), **kwargs)->None:
        super().__init__(*args, master=master, **kwargs)

        self.num_boxes = len(titles)
        self.choices = choices
        self.padx = padx
        self.pady = pady
        self.font = font
        self.titles = titles
        self.option_boxes = []
        if command is None:
            self.command = self.add_box
        else:
            self.command = command

        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        for i, title in enumerate(titles):
            t = CTkLabel(master=self, text=title, font=self.font, anchor="center")
            t.grid(row=0, column=i, padx=self.padx, pady=self.pady, sticky="nsew")
            self.last_title = t

        for i in range(self.num_boxes):
            opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
            opt.grid(row=1, column=i, padx=10, pady=5, sticky="ew")
            self.option_boxes.append(opt)

        self.button = CTkButton(master=self, text="+", font=self.font, width = 20, command=self.command)
        self.button.grid(row=1, column=self.num_boxes, sticky="ew")

    def add_box(self)->None:
        new_opt = CTkOptionMenu(master=self, font=self.font, values=self.choices, anchor="center")
        new_opt.grid(row=1, column=self.num_boxes, padx=10, pady=5, sticky="ew")
        self.option_boxes.append(new_opt)
        self.num_boxes += 1
        self.grid_columnconfigure(self.get_column_tuple(), weight=1)
        self.button.grid(row=1, column=self.num_boxes, sticky="ew")
        self.last_title.grid(row=0, column=len(self.titles) - 1, columnspan=self.num_boxes, padx=self.padx, pady=self.pady, sticky="nsew")
        self.update()

    def get_column_tuple(self) -> tuple:
        res = ()
        for i in range(self.num_boxes + 1):
            res = (*res, i)
        return res

class RadioOptions(CTkFrame):
    pass # finsih later
        
