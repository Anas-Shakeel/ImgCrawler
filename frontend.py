import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from backend import Backend
import json
from threading import Thread
import requests
from io import BytesIO
from PIL import Image


class App(ctk.CTk):
    PROGRAM_NAME = "ImgCrawler"
    PROGRAM_VER = "1.0"

    def __init__(self):
        super().__init__()
        self.backend = Backend()

        # * Will hold All scraped data
        self.scraped_data = None
        self.total_images = None
        self.total_size = None

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

        self.button_scrape_cancel = ctk.CTkButton(
            self.fields_frame, text="Cancel", width=90, height=35, command=self.cancel_scraping)
        self.button_scrape_cancel.grid(row=0, column=3)

        # ? Padding childs
        for child in self.fields_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # * Output View
        self.view_frame = ctk.CTkScrollableFrame(
            self.mainframe, label_text="Images", orientation="horizontal")
        self.view_frame.grid(row=1, column=0, pady=10, sticky="new")
        self.mainframe.rowconfigure(1, weight=1)

        # * Other inputs Frame
        self.other_frame = ctk.CTkFrame(self.mainframe, height=50)
        self.other_frame.grid(row=2, sticky="we")

        self.dir_field = DirectoryField(self.other_frame)
        self.dir_field.grid(row=0, column=0, sticky="e")

        self.button_download = ctk.CTkButton(self.other_frame,
                                             text="Download",
                                             width=90, height=35,
                                             command=self.download)
        self.button_download.grid(row=0, column=1, sticky="e")
        self.other_frame.columnconfigure((0, 1,), weight=1)

        # ? Padding childs
        for child in self.other_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # * Status bar
        self.status_bar = ctk.CTkFrame(self, height=25)
        self.status_bar.grid(sticky="ew")

    def validate_url(self, url: str):
        """ Validate URL """
        if url.startswith("https://imgpile.com/i/"):
            return False

        if url.startswith("https://imgpile.com/"):
            return True
        else:
            return False

    def start_scraping(self, event=None):
        """
        ### Start Scraping
        Get the inputs and execute scraping
        """
        url = self.entry_url.get()

        if not url:
            messagebox.showerror("Invalid URL",
                                 "Please enter a valid Album's URL from imgpile.com website.")
            return

        # URL Validation
        if not self.validate_url(url):
            messagebox.showerror("Invalid URL",
                                 "Please enter a valid Album's URL from imgpile.com website.")
            return

        # Disable button
        self.button_scrape.configure(text="Please wait...", state=tk.DISABLED)

        # Create log window
        self.logwindow = LogWindow(master=self, title="Crawl Log")

        # Start scraping in new thread
        scraping_thread = Thread(target=self.scrape_in_background, args=(
            url, self.logwindow))
        scraping_thread.start()

    def scrape_in_background(self, url, logwindow):
        """ 
        ### Scrape in Background
        scrape the data in background (new thread)
        """
        try:
            result = self.backend.get_response(url, logwindow)
            self.after(0, self.update_gui, result)
        except Exception as e:
            # In-case of errors, call error handler
            self.after(0, self.handle_errors, e)

    def update_gui(self, result=None):
        """ Updates the GUI """
        # Enable scrape button
        self.button_scrape.configure(text="Scrape", state=tk.NORMAL)

        # Save the response "class"ically :)
        self.scraped_data = result
        self.logwindow.write(f"[Success] Images Extracted.\n")
        # Do some calculations regarding the data
        self.update_properties()
        self.logwindow.write(
            f"\n[Info] Total Extracted Images: {self.total_images}")
        self.logwindow.write(
            f"\n[Info] Total Size of Images: {self.total_size}")
        self.logwindow.write(f"\n[Info] Showing JSON:\n")
        self.logwindow.write(json.dumps(self.scraped_data, indent=4))

        # Show images in 'view_frame'
        self.show_images()

        # Update 'view_frame's title
        self.view_frame.configure(
            label_text=f"{self.total_images} images were scraped")

    def update_properties(self):
        """ 
        ### Update Properties
        updates or adds some properties regarding the scraped data such as
        `len(total_images)`, `size(total_images)`, `links(all_images)` etc
        """
        # * Get the number of total images
        self.total_images = len(self.scraped_data)

        # * Calculate the size of total images
        total_bytes = 0.0
        for image in self.scraped_data:
            size_unit = image['size'].split()
            total_bytes += self.backend.to_bytes(
                float(size_unit[0]), size_unit[1])
        self.total_size = self.backend.to_human_readable_storage(total_bytes)

    def handle_errors(self, error):
        """ Handles errors """
        # Enable scrape button
        self.button_scrape.configure(text="Scrape", state=tk.NORMAL)

        self.button_download.configure(text="Download", state=tk.NORMAL)

        # Error info
        messagebox.showerror(
            "Error Occurred", f"An error occurred: {str(error)}")

    def show_images(self):
        """ Start Image Displayer Thread """
        display_thread = Thread(target=self.show_images_in_background)
        display_thread.start()

    def show_images_in_background(self):
        """ Displays images in `view_frame` in background """
        for index, image in enumerate(self.scraped_data):
            ImageBox(self.view_frame,
                     thumb_url=image['thumb_url'],).grid(row=0, column=index, padx=5, pady=5)

    def cancel_scraping(self):
        """ Cancel/Terminate the scraping thread """
        ...

    def download(self):
        """ Download the images """
        # Disable the download button first!!!
        self.button_download.configure(text="Please wait", state=tk.DISABLED)

        savepath = "saves\\"
        self.downloading_thread = Thread(
            target=self.begin_dowmload, args=(savepath, ))
        self.downloading_thread.start()

    def begin_dowmload(self, save_path):
        """ 
        ### Begin Download
        Start the downloading process in a new thread
        """
        try:
            for image in self.scraped_data:
                filename = image['title'] + image['extension']
                self.backend.download_images(image['image_url'],
                                             filename, save_path)
        except Exception as e:
            self.after(0, self.handle_errors, e)

        finally:
            self.button_download.configure(text="Download", state=tk.NORMAL)

    def exit_app(self):
        """ Method for exiting the application the right way """
        self.destroy()


class ImageBox(ctk.CTkFrame):
    """ An Imagebox that takes `thumb_url` and displays it """

    def __init__(self, master, thumb_url,  *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.thumb_url = thumb_url

        self.load_image()
        self.create_widgets()

    def load_image(self):
        raw_data = requests.get(self.thumb_url).content
        image = Image.open(BytesIO(raw_data))

        self.image = ctk.CTkImage(image, size=(200, 200))

    def create_widgets(self):
        self.canvas = ctk.CTkLabel(
            self, text="", image=self.image, width=200, height=200)
        self.canvas.image = self.image
        self.canvas.grid(row=0, column=0, padx=5, pady=5)


class LogWindow(ctk.CTkToplevel):
    def __init__(self, master, title, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Window Configuration
        self.title(title)
        self.geometry("500x350+25+25")
        self.after(0, lambda: self.state("zoomed"))
        self.grab_set()
        self.after(0, lambda: self.focus_set())

        self.text_area = ctk.CTkTextbox(self, font=("", 18))
        self.text_area.grid(sticky="news", padx=10, pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def write(self, text):
        """ Write `text` in the textarea """
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, text)
        self.text_area.configure(state="disabled")

    def close_window(self):
        """ Destroy this widget """
        self.destroy()


class DirectoryField(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, height=50, *args, **kwargs)

        # Entry field
        self.dir_var = ctk.StringVar()
        self.entry_field = ctk.CTkEntry(self, textvariable=self.dir_var)
        self.entry_field.grid(row=0, column=0, sticky="ew")

        # Open File Dialog Button
        self.image = ctk.CTkImage(
            dark_image=Image.open("assets\\directory_16px.png"))
        self.dir_button = ctk.CTkButton(
            self, text="", image=self.image, width=30, height=30, command=self.open_dialog)
        self.dir_button.grid(row=0, column=1, sticky="e")

        self.grid_columnconfigure(0, weight=1)

    def open_dialog(self):
        ...

    def get_dir(self):
        """ 
        ### Get Directory
        Returns the directory entered in the directory field
        """
        return self.dir_var.get()
