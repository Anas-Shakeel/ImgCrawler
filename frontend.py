"""
### Frontend for ImgPile Scraper
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from backend import Backend
import json
from threading import Thread
import threading


class App(ctk.CTk):
    PROGRAM_NAME = "ImgCrawler"
    PROGRAM_VER = "1.0"

    def __init__(self):
        super().__init__()
        self.backend = Backend()

        # * Root Configuration
        self.title(f"{self.PROGRAM_NAME} {self.PROGRAM_VER}")
        # self.geometry("1024x768+10+10")
        self.geometry("640x480+10+10")
        self.minsize(520, 380)
        self.after(0, lambda: self.state("zoomed"))
        self.option_add("*tearOff", tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        # * Mainframe [to hold everything]
        self.mainframe = ctk.CTkFrame(self)
        self.mainframe.grid(sticky="news", padx=10, pady=10)
        self.columnconfigure((0,), weight=1)
        self.rowconfigure((0,), weight=1)

        # * Fields Frame [will hold input fields]
        self.fields_frame = ctk.CTkFrame(self.mainframe)
        self.fields_frame.grid(row=0, column=0, sticky="we")
        self.mainframe.columnconfigure((0,), weight=1)

        ctk.CTkLabel(self.fields_frame, font=("", 18), text="Target URL").grid(
            row=0, column=0)

        self.entry_url = ctk.CTkEntry(self.fields_frame,
                                      height=35, font=("", 18),
                                      text_color=("green", "#A6A6A6"),
                                      placeholder_text="Enter URL Here...")
        self.entry_url.grid(row=0, column=1, sticky="we")
        self.fields_frame.columnconfigure(1, weight=1)

        self.button_scrape = ctk.CTkButton(
            self.fields_frame, text="Scrape", width=90, height=35, command=self.start_scraping)
        self.button_scrape.grid(row=0, column=2)

        self.button_scrape = ctk.CTkButton(
            self.fields_frame, text="Cancel", width=90, height=35, command=self.cancel_scraping)
        self.button_scrape.grid(row=0, column=3)

        # ? Padding childs
        for child in self.fields_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # * Output Field
        self.view_frame = ctk.CTkScrollableFrame(
            self.mainframe, label_text="247 Images were scraped!")
        self.view_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        self.mainframe.rowconfigure(1, weight=1)

        for i in range(10):
            ctk.CTkCheckBox(self.view_frame, text=str(i)).grid(
                sticky="w", padx=5, pady=3)

        # * Other inputs Frame
        self.other_frame = ctk.CTkFrame(self.mainframe, height=50)
        self.other_frame.grid(row=2, sticky="we")

        self.button_select_all = ctk.CTkButton(self.other_frame,
                                               text="Select All",
                                               width=90, height=35)
        self.button_select_all.grid(row=0, column=0)

        self.button_deselect_all = ctk.CTkButton(self.other_frame,
                                                 text="Deselect All",
                                                 width=90, height=35)
        self.button_deselect_all.grid(row=0, column=1)

        self.button_download = ctk.CTkButton(self.other_frame,
                                             text="Download",
                                             width=90, height=35,)
        self.button_download.grid(row=0, column=2, sticky="e")
        self.other_frame.columnconfigure((2,), weight=1)

        # ? Padding childs
        for child in self.other_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # * Status bar
        self.status_bar = ctk.CTkFrame(self, height=25)
        self.status_bar.grid(sticky="ew")

        """
        
        # ! TEMPORARY Data Entry Stuff :: REMOVE Afterwards
        self.url_var = tk.StringVar()
        self.url_var.set("https://imgpile.com/search/images/?q=shelby+gt")
        ttk.Entry(self, textvariable=self.url_var).pack()
        self.scrape_button = ttk.Button(
            self, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack()
        """

    def validate_url(self, url: str):
        """ Validate URL """
        if url.startswith("http://imgpile.com/i/"):
            return False
        elif url.startswith("http://imgpile.com/"):
            return True
        else:
            return False

    def start_scraping(self, event=None):
        """
        ### Start Scraping
        Get the inputs and execute scraping
        """
        url = self.entry_url.get()
        if not url and not self.validate_url(url):
            # probably show an error dialog
            # focus on the entry
            return
        print("DATA Scraped")
        return

        # Disable button
        self.scrape_button.config(text="Please wait...", state=tk.DISABLED)

        # Start scraping in new thread
        scraping_thread = Thread(target=self.scrape_in_background, args=(
            url,), name="Scraping - Python")
        scraping_thread.start()

    def scrape_in_background(self, url):
        """ 
        ### Scrape in Background
        scrape the data in background (new thread)
        """
        try:
            result = self.backend.get_response(url)
            self.after(0, self.update_gui, result)
        except Exception as e:
            # In-case of errors, call error handler
            self.after(0, self.handle_errors, e)

    def update_gui(self, result=None):
        """ Updates the GUI """
        # Enable scrape button
        self.scrape_button.config(text="Start Scraping", state=tk.NORMAL)

        # * Change the title of view_frame
        ...

        # Dump Json data
        with open("temp.json", "w") as tempfile:
            json.dump(result, tempfile, indent=4)

        # Success Info
        messagebox.showinfo("Success", "Data Extracted Successfully!")

    def handle_errors(self, error):
        """ Handles errors """
        # Enable scrape button
        self.scrape_button.config(text="Start Scraping", state=tk.NORMAL)

        # Error info
        messagebox.showerror(
            "Error Occurred", f"An error occurred: {str(error)}")

    def cancel_scraping(self):
        """ Cancel/Terminate the scraping thread """
        ...

    def exit_app(self):
        """ Method for exiting the application the right way """
        self.destroy()
