import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from customtkinter import filedialog
from tkinter import messagebox
from backend import Backend
import json
from os.path import normpath
from threading import Thread
import requests
from io import BytesIO
from PIL import Image
from time import sleep


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
        self.place_in_center(1024, 768)
        self.minsize(640, 480)
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
                                      placeholder_text="Enter Album URL Here...")
        self.entry_url.grid(row=0, column=1, sticky="we")
        # self.entry_url.focus()
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

        # * View Frame
        self.view_frame = ctk.CTkScrollableFrame(self.mainframe,
                                                 label_text="Images",
                                                 label_font=("", 18),
                                                 orientation="horizontal")
        self.view_frame.grid(row=1, column=0, sticky="new")

        # * DATA Frame
        self.data_frame = ctk.CTkFrame(self.mainframe)
        self.data_frame.grid(row=2, column=0, sticky="news")
        self.mainframe.rowconfigure(2, weight=1)

        self.textbox_log = TextBoxFrame(
            self.data_frame, label="Log View", font=("", 18))
        self.textbox_log.grid(row=0, column=0, sticky="nsew")

        self.textbox_api_data = TextBoxFrame(
            self.data_frame, label="API Data", font=("", 18))
        self.textbox_api_data.grid(row=0, column=1, sticky="nsew")

        # Making it Resizable
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.rowconfigure(0, weight=1)

        # * Other inputs Frame
        self.other_frame = ctk.CTkFrame(self.mainframe, height=50)
        self.other_frame.grid(row=3, sticky="we")

        self.dir_field = DirectoryField(self.other_frame)
        self.dir_field.grid(row=0, column=0, sticky="ew")

        self.button_download = ctk.CTkButton(self.other_frame,
                                             text="Download Images",
                                             width=90, height=35,
                                             command=self.download)
        self.button_download.grid(row=0, column=1, sticky="w")

        self.options_var = ctk.StringVar(value="JSON")
        self.options_menu = ctk.CTkOptionMenu(self.other_frame,
                                              width=100, height=35,
                                              variable=self.options_var,
                                              values=["JSON", "CSV"],
                                              )
        self.options_menu.grid(row=0, column=2, sticky="w")

        self.button_download_data = ctk.CTkButton(self.other_frame,
                                                  text="Download Data",
                                                  width=90, height=35,
                                                  command=self.download_textual)
        self.button_download_data.grid(row=0, column=3, sticky="w")

        self.other_frame.columnconfigure((0, ), weight=1)

        # ? Padding mainframe's childs
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # ? Padding otherframe's childs
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

    def start_scraping(self, _=None):
        """
        ### Start Scraping
        Get the inputs and execute scraping
        """
        url = self.entry_url.get()

        if not url or not self.validate_url(url):
            messagebox.showerror("Invalid URL",
                                 "Please enter a valid Album's URL from imgpile.com website.")
            return

        # Disable button
        self.button_scrape.configure(
            text="Please wait...", state=tk.DISABLED)

        # Start scraping in new thread
        scraping_thread = Thread(target=self.scrape_in_background, args=(
            url, self.textbox_log))
        scraping_thread.start()

    def scrape_in_background(self, url, logwidget):
        """
        ### Scrape in Background
        scrape the data in background (new thread)
        """
        try:
            result = self.backend.get_response(url, logwidget)
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
        # Do some calculations regarding the data
        self.update_properties()
        self.textbox_log.write(
            f"\n[Info] Total Extracted Images: {self.total_images}")
        self.textbox_log.write(
            f"\n[Info] Total Size of Images: {self.total_size}\n")
        self.textbox_log.write(f"\n[Success] Data Extracted.\n\n")

        self.textbox_api_data.delete_everything()
        self.textbox_api_data.write(f"Response from API:\n")
        self.textbox_api_data.write(json.dumps(self.scraped_data, indent=4))

        # Show images in 'view_frame'
        self.show_images()

        # Update 'view_frame's title
        self.view_frame.configure(
            label_text=f"{self.total_images} images were scraped")

    def update_properties(self):
        """
        ### Update Properties
        updates or adds some properties regarding the scraped data such as
        `self.total_images` and `self.total_size`
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
        """
        ### Handles errors
        handle errors which occur in scraping process
        """
        # Enable scrape button
        self.button_scrape.configure(text="Scrape", state=tk.NORMAL)

        # Show Error Dialog
        messagebox.showerror(
            "Scraping Failed", f"An error occurred: {str(error)}")

    def handle_download_errors(self, error_message):
        """
        ### Handle Download Errors
        handle errors which occur in downloading process
        """
        # Enable download button
        self.button_download.configure(text="Download Images", state=tk.NORMAL)

        # Show Error Dialog
        messagebox.showerror(
            "Downloading Failed", f"{error_message}")

    def show_images(self):
        """ Start Image Displayer Thread """
        display_thread = Thread(target=self.show_images_in_background)
        display_thread.start()

    def show_images_in_background(self):
        """ Displays images in `view_frame` in background """
        for index, image in enumerate(self.scraped_data):
            ImageBox(self.view_frame,
                     thumb_url=image['thumb_url'],).grid(row=0, column=index, padx=5)

    def cancel_scraping(self):
        """ Cancel/Terminate the scraping thread """
        ...

    def download(self):
        """ Download the images """
        savepath = self.dir_field.get_dir()
        if not savepath:
            messagebox.showinfo("No Save Location Specified",
                                "Please Enter the directory path before downloading.")
            self.dir_field.entry_field.focus()
            return

        # Disable the download button
        self.button_download.configure(
            text="Please wait", state=tk.DISABLED)

        self.downloading_thread = Thread(
            target=self.begin_dowmload, args=(savepath, ))
        self.downloading_thread.start()

    def begin_dowmload(self, save_path):
        """
        ### Begin Download
        Start the downloading process in a new thread
        """
        try:
            if not self.scraped_data:
                raise ValueError("Please Scraped the images first.")

            for image in self.scraped_data:
                filename = image['title'] + image['extension']
                self.backend.download_images(image['image_url'],
                                             filename, save_path)
        except Exception as e:
            self.after(0, self.handle_download_errors, e)

        finally:
            self.button_download.configure(
                text="Download", state=tk.NORMAL)

    def download_textual(self):
        """
        ### Download Textual
        Download the scraped data as a JSON/CSV file.
        """
        # ! DEBUG MODE:: Remove afterwards ! #
        DownloadDialog(self, )
        return

        # Scrape Validation
        if not self.scraped_data:
            # Haven't Scraped anything yet!
            messagebox.showinfo("No Data to Download",
                                "There is no data to download, Please scrape the data first!")
            self.entry_url.focus()
            return

        file_format = self.options_var.get()
        if not file_format:
            # No file_format specified
            raise ValueError("Specify a file format first")

        # Filename for the files
        filename = "Demo"

        save_path = self.dir_field.get_dir()
        if not save_path:
            # User didn't enter directory
            messagebox.showinfo("No Save Location",
                                "Please Enter the directory path before downloading.")
            self.dir_field.entry_field.focus()
            return

        try:
            data_downloading_thread = Thread(target=self.backend.download_data,
                                             args=(self.scraped_data,
                                                   file_format,
                                                   filename,
                                                   save_path))
            data_downloading_thread.start()
            data_downloading_thread.join()
            # Enable the button
            self.button_download.configure(
                text="Download Data", state=tk.NORMAL)
            self.show_popup(f"API Data has been downloaded at {save_path}")

        except Exception as error:
            # ! REMOVE THIS AFTER DEBUGGING !
            print(error)
            self.handle_download_errors(error)

    def show_popup(self, message):
        """ 
        ### Show Popup
        Shows a popup dialog displaying `message`
        """
        PopupDialog(self, message)

    def place_in_center(self, width, height):
        """ Places `self` in the center of the screen """
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        geo_string = f"{width}x{height}+{x}+{y}"
        self.geometry(geo_string)

    def get_screen_center(self):
        """
        ### Get Screen Center
        returns the center of the screen.
        """
        x = self.winfo_screenwidth() // 2
        y = self.winfo_screenheight() // 2

        return x, y

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

        self.image = ctk.CTkImage(image, size=(180, 180))

    def create_widgets(self):
        self.canvas = ctk.CTkLabel(
            self, text="", image=self.image, width=180, height=180)
        self.canvas.image = self.image
        self.canvas.grid(row=0, column=0, padx=5, pady=5)


class DirectoryField(ctk.CTkFrame):
    """ 
    ### Directory Field Widget
    A Custom-Widget used to take directory input from user
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, height=50, *args, **kwargs)

        # Entry field
        self.dir_var = ""
        self.entry_field = ctk.CTkEntry(self,
                                        placeholder_text="Enter save location",
                                        font=("", 16))
        self.entry_field.grid(row=0, column=0, sticky="ew")

        # Open File Dialog Button
        self.image = ctk.CTkImage(
            dark_image=Image.open("assets\\directory_light_16px.png"))
        self.dir_button = ctk.CTkButton(
            self, text="", image=self.image, width=30, height=30, command=self.open_dialog)
        self.dir_button.grid(row=0, column=1, sticky="e")

        self.grid_columnconfigure(0, weight=1)

        # Spacing things out
        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=1)

    def open_dialog(self):
        """
        ### Open Directory Dialog
        Opens a directory dialog and returns the user's selected dir.
        """
        try:
            dir_ = filedialog.askdirectory()
            if dir_:
                # Insert into entry field
                self.entry_field.delete(0, tk.END)
                self.entry_field.insert("1", normpath(dir_))

        except Exception as e:
            print(f"error: {e}")

    def get_dir(self):
        """ 
        ### Get Directory
        Returns the directory entered in the directory field
        """
        return self.entry_field.get()


class TextBoxFrame(ctk.CTkFrame):
    """ 
    ### TextBox Frame
    A Custom-Widget used to create a textbox frame
    """

    def __init__(self, master, width=200, label="TextBoxFrame", font=None, *args, **kwargs):
        super().__init__(master, width, bg_color="transparent",  *args, **kwargs)

        ctk.CTkLabel(self, text=label, font=("", 18),
                     height=10,
                     fg_color="#393939",
                     corner_radius=4,
                     ).grid(row=0, column=0, columnspan=2, ipadx=5, ipady=5, padx=5, pady=2, sticky="ew")

        self.text_area = ctk.CTkTextbox(self, font=font, state="disabled")
        self.text_area.grid(row=1, column=0, columnspan=2,
                            sticky="news", padx=5, pady=2)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    def write(self, data):
        """ 
        ### Write
        Write `data` into the textbox of this widget.
        """
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, data)
        self.text_area.configure(state="disabled")

    def delete_everything(self):
        """ 
        ### Clear
        Clears the text in the textbox of this widget.
        """
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.delete("1.0", "end")
        self.text_area.configure(state=tk.DISABLED)


class PopupDialog(ctk.CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(parent)

        self.overrideredirect(1)
        self.place_in_center(300, 150)

        # Set up widgets
        self.message_label = ctk.CTkLabel(self, text=message, padx=20, pady=20)
        self.ok_button = ctk.CTkButton(
            self, text="OK", font=("", 18), command=self.on_ok)

        # Pack widgets
        self.message_label.pack()
        self.ok_button.pack(pady=10)

        # Make the dialog modal
        self.transient(parent)
        # ! uncomment this: > to prevent interactions between user and other widgets
        # self.grab_set()
        parent.wait_window(self)

    def place_in_center(self, width, height):
        """ Places `self` in the center of the screen """
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        geo_string = f"{width}x{height}+{x}+{y}"
        self.geometry(geo_string)

    def on_ok(self):
        self.destroy()


class DownloadDialog(ctk.CTkToplevel):
    """ 
    ### Download Popup
    Download Popup custom widget for various downloading options & fields
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Toplevel Configurations
        self.title("Download")
        self.place_in_center(520, 140)
        self.resizable(False, False)
        self.grab_set()
        # self.wait_window(self)

        # * Mainframe
        self._mainframe = ctk.CTkFrame(self, )
        self._mainframe.grid(row=0, column=0, padx=5, pady=5, sticky="news")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # * DATATYPE Label
        ctk.CTkLabel(self._mainframe, text="Data Format", font=("", 15),
                     ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # * DATATYPES Options Dropdown
        self._options_var = ctk.StringVar(value="IMAGE")
        self._options_menu = ctk.CTkOptionMenu(self._mainframe,
                                               width=120, height=30,
                                               variable=self._options_var,
                                               values=["JSON", "CSV", "IMAGE"],
                                               command=self.on_options_changed_datatype
                                               )
        self._options_menu.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        # * Filename Entry
        self._entry_filename = ctk.CTkEntry(self._mainframe,
                                            placeholder_text="Filename", font=("", 16),
                                            width=120, height=30)
        # self._entry_filename.grid(row=0, column=2, sticky="w", padx=10, pady=10)

        # * Quality Options Dropdown
        self._options_quality = ctk.CTkOptionMenu(self._mainframe,
                                                  width=120, height=30,
                                                  values=[
                                                      "High Quality", "Low Quality"],
                                                  )
        self._options_quality.grid(
            row=0, column=2, sticky="w", padx=10, pady=10)

        # * Download button
        self._button_download = ctk.CTkButton(self._mainframe,
                                              width=120, height=30,
                                              text="Download",
                                              command=self.download_callback)
        self._button_download.grid(
            row=0, column=3, sticky="e", padx=10, pady=10)

        self._dir_field = DirectoryField(self._mainframe)
        self._dir_field.grid(row=1, column=0, columnspan=3,
                             sticky="ew", padx=10, pady=10)

        # * Cancel button
        self._button_cancel = ctk.CTkButton(self._mainframe,
                                            width=120, height=30,
                                            text="Cancel",)
        self._button_cancel.grid(
            row=1, column=3, sticky="e", padx=10, pady=10)

        # * Download button spacing
        self._mainframe.columnconfigure(3, weight=1)

        """
        # * Progress Bar
        self._progress_var = ctk.DoubleVar(value=10)
        self._progress_bar = ctk.CTkProgressBar(self, determinate_speed=1,
                                                mode="determinate",
                                                height=15,
                                                corner_radius=2,
                                                orientation="horizontal",
                                                variable=self._progress_var)
        self._progress_bar.set(0)
        self._progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # """

        self._progress_bar = ttk.Progressbar(self,)
        self._progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # ? Padding & Spacing
        # for child in self._mainframe.winfo_children():
        # child.grid_configure(padx=10, pady=10)

    def on_options_changed_datatype(self, value=None):
        """ Callback on options values change """
        if value in ["JSON", "CSV"]:
            # Textual data
            print("Textual", value)
            self._options_quality.grid_forget()
            self._entry_filename.grid(
                row=0, column=2, sticky="w", padx=10, pady=10)

        else:
            # Image data
            print("Image", value)
            self._entry_filename.grid_forget()
            self._options_quality.grid(
                row=0, column=2, sticky="w", padx=10, pady=10)

    def place_in_center(self, width, height):
        """ Places `self` in the center of the screen """
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        geo_string = f"{width}x{height}+{x}+{y}"
        self.geometry(geo_string)

    def download_callback(self):
        """ 
        ### Download Callback
        """
        tasks = 100
        download = 0
        speed = 1
        while download < tasks:
            # CODE TO EXECUTE :: DOWNLOADING...
            # sleep(0.25)
            ...
            self._progress_bar['value'] += (speed/tasks)*100
            download += speed
            self.update_idletasks()

        # TODO > Show Download Complete Dialog/Message !
        ...

        # Destroy `self` after download.
        self.destroy()
