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
    # program name
    PROGRAM_NAME = "ImgCrawler"

    def __init__(self):
        super().__init__()
        self.backend = Backend()

        # * Root Configuration
        self.title(self.PROGRAM_NAME)
        # self.geometry("1024x768+10+10")
        self.geometry("640x480+10+10")
        self.minsize(520, 380)
        # self.after(0, lambda: self.state("zoomed"))
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

        ctk.CTkLabel(self.fields_frame, text="Target URL").grid(
            row=0, column=0)

        self.entry_url = ctk.CTkEntry(self.fields_frame,
                                      width=200,
                                      placeholder_text="Enter URL Here...")
        self.entry_url.grid(row=0, column=1, sticky="w")
        
        self.button_scrape = ctk.CTkButton(self.fields_frame, text="Scrape", width=15, command=self.start_scraping)
        self.button_scrape.grid(row=0, column=2)
        
        self.button_scrape = ctk.CTkButton(self.fields_frame, text="Cancel", width=15, command=self.cancel_scraping)
        self.button_scrape.grid(row=0, column=3)
        
        # for child in self.fields_frame.winfo_children():
            # child.configure(padding="10")
        
        # * Output Field
        self.view_frame = ctk.CTkScrollableFrame(self.mainframe, label_text="Images")
        self.view_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        self.mainframe.rowconfigure(1, weight=1)
        
        for i in range(10):
            ctk.CTkCheckBox(self.view_frame, text=str(i)).grid(sticky="w", padx=5, pady=3)
        
        # * Other Field
        self.other_frame = ctk.CTkFrame(self.mainframe, height=50)
        self.other_frame.grid(row=2, sticky="we")

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

    def start_scraping(self, event=None):
        """
        ### Get Data
        Get the image data from backend
        """
        url = self.url_var.get()

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
        print(self.entry_url.get())


    def exit_app(self):
        """ Method for exiting the application the right way """
        self.destroy()
