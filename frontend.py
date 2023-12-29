""" 
### Frontend for ImgPile Scraper
"""
import tkinter as tk
from tkinter import ttk
from backend import ImgPile


class App(tk.Tk):
    # program name
    PROGRAM_NAME = "ImgCrawler"
    
    def __init__(self):
        super().__init__()

        # * Root Configuration
        self.title(self.PROGRAM_NAME)
        self.geometry("1280x720+0+10")
        self.minsize(520, 380)
        self.state("zoomed")
        self.option_add("*tearOff", tk.FALSE)
