"""
### Frontend for ImgPile Scraper
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from backend import Backend
import json
from threading import Thread


class App(tk.Tk):
    # program name
    PROGRAM_NAME = "ImgCrawler"

    def __init__(self):
        super().__init__()
        self.backend = Backend()

        # * Root Configuration
        self.title(self.PROGRAM_NAME)
        self.geometry("1280x720+0+10")
        self.minsize(520, 380)
        self.state("zoomed")
        self.option_add("*tearOff", tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        # ! TEMPORARY Data Entry Stuff :: REMOVE Afterwards
        self.url_var = tk.StringVar()
        self.url_var.set("https://imgpile.com/search/images/?q=shelby+gt")
        ttk.Entry(self, textvariable=self.url_var).pack()
        self.scrape_button = ttk.Button(
            self, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack()

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

    def exit_app(self):
        """ Method for exiting the application the right way """
        self.destroy()
