import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox
from customtkinter import filedialog
from CTkToolTip import CTkToolTip
from backend import Backend
import os
from os.path import normpath
from threading import Thread, Event
import requests
from io import BytesIO
from PIL import Image
from time import sleep
import pyperclip


class App(ctk.CTk):
    PROGRAM_NAME = "ImgCrawler"
    PROGRAM_VER = "1.0"

    def __init__(self):
        super().__init__(fg_color="#1F1F1F")
        self.backend = Backend()

        # * Colors & Fonts
        self.font_ = "Segoe UI"

        fg = "#292929"
        bg = "#1F1F1F"
        title_color = "#999999"
        border_color = "#353535"
        primary_color = "#fe771d"

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
        self.mainframe = ctk.CTkFrame(self, fg_color=bg)
        self.mainframe.grid(sticky="news", padx=10, pady=10)
        self.columnconfigure((0,), weight=1)
        self.rowconfigure((0,), weight=1)

        # * Fields Frame [will hold input fields]
        self.fields_frame = ctk.CTkFrame(self.mainframe,
                                         border_width=1,
                                         border_color=border_color,
                                         fg_color=fg,
                                         corner_radius=2,
                                         )
        self.fields_frame.grid(row=0, column=0, padx=5, pady=5, sticky="we")
        self.mainframe.columnconfigure((0,), weight=1)

        ctk.CTkLabel(self.fields_frame, font=(f"{self.font_} bold", 20), text_color=title_color, text="Target URL").grid(
            row=0, column=0)

        self.entry_url = ctk.CTkEntry(self.fields_frame,
                                      height=35, font=(self.font_, 18),
                                      text_color=title_color,
                                      fg_color=fg,
                                      corner_radius=3,
                                      border_width=1, border_color="#404040",
                                      placeholder_text="Enter Album URL Here...")
        self.entry_url.grid(row=0, column=1, sticky="we")
        # Focus on entry url
        self.entry_url.after(1000, self.entry_url.lift)
        self.entry_url.after(1000, self.entry_url.focus_force)
        # Tooltip for entry url
        CTkToolTip(self.entry_url,
                   follow=False, delay=0.5,
                   message="Enter the URL of the album you want to scrape",)

        self.fields_frame.columnconfigure(1, weight=1)

        self.button_scrape = ctk.CTkButton(self.fields_frame,
                                           text="Scrape",
                                           width=90, height=35,
                                           corner_radius=4,
                                           font=(f"{self.font_} bold", 16),
                                           text_color="#c8c8c8",
                                           hover_color="#0E4F81",
                                           fg_color="#046DB9",
                                           command=self.start_scraping)
        self.button_scrape.grid(row=0, column=2)
        # Tooltip for button
        CTkToolTip(self.button_scrape,
                   follow=False, delay=0.5,
                   message="Scrape the url",)

        self.button_scrape_cancel = ctk.CTkButton(self.fields_frame,
                                                  text="Cancel",
                                                  width=90, height=35,
                                                  corner_radius=4,
                                                  font=(
                                                      f"{self.font_} bold", 15),
                                                  text_color="#c8c8c8",
                                                  border_width=1,
                                                  border_color="#404040",
                                                  hover_color="#7C0902",
                                                  fg_color="#353535",
                                                  state="disabled",
                                                  command=self.cancel_scraping)
        self.button_scrape_cancel.grid(row=0, column=3)
        # Tooltip for button
        CTkToolTip(self.button_scrape_cancel,
                   follow=False, delay=0.5,
                   message="Cancel the scrape.",)

        # ? Padding childs
        for child in self.fields_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # Scrape Progress bar
        self.scrape_progress_bar = ctk.CTkProgressBar(self.mainframe,
                                                      height=5,
                                                      mode="indeterminate",
                                                      corner_radius=2)

        # * View Frame
        self.view_frame = ctk.CTkScrollableFrame(self.mainframe, fg_color=fg,
                                                 label_text="Images",
                                                 label_text_color=title_color,
                                                 label_fg_color="#353535",
                                                 border_width=1,
                                                 border_color="#404040",
                                                 label_font=(
                                                     f"{self.font_} bold", 18),
                                                 scrollbar_button_color="#353535",
                                                 scrollbar_button_hover_color="#505050",
                                                 orientation="vertical")
        self.view_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nesw")
        self.mainframe.rowconfigure(2, weight=1)
        self.view_frame.columnconfigure(0, weight=1)

        # * Other inputs Frame
        self.other_frame = ctk.CTkFrame(
            self.mainframe, border_width=1, border_color=border_color, fg_color=fg, height=50)
        self.other_frame.grid(row=3, padx=5, pady=5, sticky="wes")

        self.button_download_data = ctk.CTkButton(self.other_frame,
                                                  text="Download",
                                                  width=95, height=35,
                                                  corner_radius=4,
                                                  font=(
                                                      f"{self.font_} bold", 16),
                                                  text_color="#c8c8c8",
                                                  border_width=1,
                                                  border_color="#404040",
                                                  hover_color="#046DB9",
                                                  fg_color="#353535",
                                                  command=self.download)
        self.button_download_data.grid(row=0, column=0, sticky="e")
        # Tooltip for button
        CTkToolTip(self.button_download_data,
                   follow=False, delay=0.5,
                   message="Download the scraped data",)

        self.other_frame.columnconfigure((0, ), weight=1)

        # ? Padding otherframe's childs
        for child in self.other_frame.winfo_children():
            child.grid_configure(padx=10, pady=10)

        # * Keyboard & Mouse Bindings (Shortcuts)
        # Shortcut Binding for entry url
        self.entry_url.bind("<Double-Button-3>", self.paste_to_entry_url)
        # Root Bindings
        self.bind("<Control-Shift-l>", self.load_presaved_data)
        self.bind("<Control-Shift-L>", self.load_presaved_data)
        # UrlEnry bindings > scrape
        self.entry_url.bind("<Return>", self.start_scraping)

    def load_presaved_data(self, _=None):
        """ 
        ### Load Presaved Data
        Loads a presaved json data to avoid scraping again!

        `Data` must be in a json format similar to that json created by this app.
        """
        # * Get Data from Backend
        filepath = filedialog.askopenfilename(title="Open a Json File",
                                              filetypes=[("Json Files", "*.json")])
        if not filepath:
            return
        presaved_data = self.backend.get_presaved_data(filepath=filepath)
        if presaved_data == None:
            messagebox.showerror("Load Failed",
                                 "Your json file did not loaded. This app supports json files created by this app only or a file with similar format.")
            return

        # * Load Data in the App!
        self.scraped_data = presaved_data
        self.update_properties()

        # Instantiate the progress bar
        self.scrape_progress_bar.grid(row=1, column=0,
                                      padx=10, pady=0, sticky="ew")
        self.scrape_progress_bar.start()

        # Shows the loaded images
        self.show_images()

        self.view_frame.configure(
            label_text=f"{self.total_images} images were loaded")

        messagebox.showinfo("Load Success",
                            "Your json file has been successfully loaded into the app. You can now download the images or csv.")

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

        # Disable scrape button
        self.button_scrape.configure(
            text="Please wait...", state="disabled")

        # Enable cancel button
        self.button_scrape_cancel.configure(state="normal")

        # Instantiate the progress bar
        self.scrape_progress_bar.grid(
            row=1, column=0, padx=10, pady=0, sticky="ew")
        self.scrape_progress_bar.start()

        # Scraping thread event
        self.scraping_event = Event()

        # Start scraping in new thread
        scraping_thread = Thread(target=self.scrape_in_background, args=(
            url, self.scraping_event,))
        scraping_thread.start()

    def scrape_in_background(self, url, event: Event):
        """
        ### Scrape in Background
        scrape the data in background (new thread)
        """
        try:
            result = self.backend.get_response(url, event)
            if result:
                self.after(0, self.update_gui, result)
        except Exception as e:
            # In-case of errors, call error handler
            self.after(0, self.handle_scrape_errors, e)

    def scrape_completed(self):
        """ 
        ### Scrape Completed
        Code to run when the scraping process is finished
        """
        self.button_scrape.configure(text="Scrape", state="normal")
        self.button_scrape_cancel.configure(state="disabled")
        messagebox.showinfo("Scraping Complete",
                            "Target URL has been scraped successfully.")

    def update_gui(self, result=None):
        """ Updates the GUI """
        self.scrape_completed()

        # Save the response "class"ically :)
        self.scraped_data = result
        self.update_properties()

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

    def handle_scrape_errors(self, error):
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
        print("{}".format(error_message))
        # Show Error Dialog
        messagebox.showerror(
            "Downloading Failed", f"{error_message}")

    def download_thumbnails(self, event):
        """
        ### Download Thumbnails
        this method downloads the thumbnails in local storage for ease of access later
        """
        for image in self.scraped_data:
            try:
                self.backend.download_thumbnail(
                    image['thumb_url'],
                    os.path.basename(os.path.normpath(image['thumb_url'])),
                    "thumbnails\\")

            except Exception as e:
                print(e)

        messagebox.showinfo("Thumbnails Downloaded",
                            "Thumbnails have been downloaded successfully.")

    def show_images(self):
        """ Start Image Displayer Thread """
        # Create a image event, to stop thread at will... :)
        self.show_image_event = Event()
        display_thread = Thread(
            target=self.show_images_in_background, args=(self.show_image_event, ))
        display_thread.start()

    def show_images_in_background(self, event: Event):
        """ Displays images in `view_frame` in background """
        # Clear the existing images first (if any)
        for child in self.view_frame.winfo_children()[::-1]:
            child.grid_forget()
            child.destroy()

        for index, image in enumerate(self.scraped_data):
            # If event is set, stop immediately!
            if event.is_set():
                break
            ImageItemFrame(self.view_frame,
                           title=image['title'],
                           thumb_url=image['thumb_url'],
                           image_type=image['image_type'], size=image['size'],
                           dimensions=image['resolution'], uploaded=image['uploaded'],
                           uploader=image['uploader'], views=image['views'],
                           likes=image['likes'],).grid(row=index, padx=10, pady=3, sticky="ew")
        # disable progressbar
        self.scrape_progress_bar.grid_forget()

    def cancel_scraping(self):
        """ 
        ### Cancel Scraping
        cancel or terminate the scraping thread  AKA (stop the scraping)
        """
        # Stop the thread
        self.scraping_event.set()

        # Do some stuff relating UI!
        self.scrape_progress_bar.grid_forget()
        self.button_scrape.configure(text="Scrape", state="normal")
        self.button_scrape_cancel.configure(state="disabled")

        # Show a message of cancellation
        messagebox.showerror("Scraping Cancelled",
                             "Target URL has not been scraped successfully. Request was cancelled by User!")

    def download(self):
        """ 
        ### Download
        Initiate the download dialog
        """
        # Scrape Validation
        if not self.scraped_data:
            # Haven't Scraped anything yet!
            messagebox.showinfo("No Data to Download",
                                "There is no data to download, Please scrape the data first!")
            self.entry_url.focus()
            return

        # * Show Download Dialog
        self.download_dialog = DownloadDialog(self,
                                              self.image_downloader,
                                              self.text_downloader)
        # Give the focus to download dialog
        self.download_dialog.get_focus_force(200)

    def image_downloader(self, save_path, image_quality,  step_callback, event: Event):
        """
        ### Image Downloader
        Begin image downloading process/thread.

        ```
        save_path = path to save images
        image_quality = quality of images to download
        step_callback = called everytime an image is downloaded
        ```
        """
        self.image_download_thread = Thread(target=self.download_images,
                                            args=(save_path,
                                                  image_quality,
                                                  step_callback,
                                                  event))
        self.image_download_thread.start()

    def download_images(self, save_path, image_quality, step_callback, event: Event):
        """
        ### Begin Download
        Start the downloading process in a new thread
        """
        try:
            # Reset the progress bar (if downloading again!)
            self.download_dialog.reset_progress_bar()

            # Download imnages
            for image in self.scraped_data:
                if image_quality == "High Quality":
                    filename = self.backend.sanitize_string(
                        image['title']) + image['extension']
                    image_url = image['image_url']
                else:
                    filename = f"{self.backend.sanitize_string(image['title'])}_Lq_{image['extension']}"
                    image_url = image['lq_url']

                self.backend.download_image(image_url,
                                            filename, save_path)
                # Increase progress (progressbar)
                step_callback(self.total_images)

                if event.is_set():  # Incase user cancels downloading
                    return

            # Incase download is completed
            self.download_completed()

        except Exception as e:
            self.after(0, self.handle_download_errors, e)

    def download_completed(self):
        """
        ### Download Completed
        Code to execute when the download is completed
        """
        # Show Download Complete Popup!
        messagebox.showinfo("Download Complete",
                            "Your Download has been completed.")
        self.after(0, self.download_dialog.hide_progress_bar)
        self.download_dialog._button_cancel.configure(state="disabled")
        self.download_dialog._button_download.configure(state="normal")
        self.download_dialog.image_downloading_event.clear()
        self.download_dialog.get_focus_force(0)

    def text_downloader(self, format_, filename_, directory_):
        """
        ### Text Downloader
        Download the scraped data as a JSON/CSV file.
        """
        try:
            data_downloading_thread = Thread(target=self.backend.download_data,
                                             args=(self.scraped_data,
                                                   format_,
                                                   filename_,
                                                   directory_,
                                                   self.download_completed))
            data_downloading_thread.start()

        except Exception as error:
            self.handle_download_errors(error)

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

    def paste_to_entry_url(self, _=None):
        """ 
        ### Paste to Entry Url
        Paste the text copied to clipboard into entry on `Right-Mouse-Click`
        """
        # Get text from clipboard & insert
        self.entry_url.delete(0, "end")
        self.entry_url.insert(0, pyperclip.paste())

    def exit_app(self):
        """
        ### Exit App
        Close the application by destroying everything and killing all background
        threads (if running)
        """
        # Kill the show_image Thread
        try:
            self.show_image_event.set()
        except AttributeError:
            pass

        # Wait for the main_thread to come into mainloop!
        self.update()
        self.after(1500, self.destroy)


class DirectoryField(ctk.CTkFrame):
    """
    ### Directory Field Widget
    A Custom-Widget used to take directory input from user
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, height=50, fg_color="transparent", *args, **kwargs)

        # Entry field
        self.dir_var = ""
        self.entry_field = ctk.CTkEntry(self,
                                        placeholder_text="Enter save location",
                                        font=("Segoe UI", 16),
                                        text_color="#bbb",
                                        fg_color="#292929",
                                        corner_radius=5,
                                        border_width=1, border_color="#404040",
                                        )
        self.entry_field.grid(row=0, column=0, sticky="ew")
        # Tooltip for Directory Field
        CTkToolTip(self.entry_field,
                   follow=False, delay=0.5,
                   message="Enter a directory/location where you want to save the data",)

        # Open File Dialog Button
        self.image = ctk.CTkImage(
            dark_image=Image.open("assets\\directory_light_16px.png"))
        self.dir_button = ctk.CTkButton(self, text="", image=self.image,
                                        width=30, height=30,
                                        fg_color="#404040",
                                        border_width=1,
                                        border_color="#505050",
                                        hover_color="#046DB9",
                                        command=lambda: self.open_dialog(master))
        self.dir_button.grid(row=0, column=1, sticky="e")
        # Tooltip for Dir Button
        CTkToolTip(self.dir_button,
                   follow=False, delay=0.5,
                   message="Open directory dialog",)

        self.grid_columnconfigure(0, weight=1)

        # Spacing things out
        for child in self.winfo_children():
            child.grid_configure(padx=2, pady=1)

    def open_dialog(self, master):
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

        finally:
            # Giving focus back to parent
            master.after(5, master.lift)
            master.after(5, master.focus_force)

    def get_dir(self):
        """
        ### Get Directory
        Returns the directory entered in the directory field
        """
        return self.entry_field.get()


class DownloadDialog(ctk.CTkToplevel):
    """
    ### Download Dialog
    Download Popup Dialog custom widget for various downloading options & fields
    """

    def __init__(self, master, image_downlod_callback, text_download_callback, *args, **kwargs):
        super().__init__(master, fg_color="#1f1f1f", *args, **kwargs)

        # * Colors & Fonts
        FONT = "Segoe UI"
        TEXT_COLOR = "#bbbbbb"
        FG_COLOR = "#292929"
        BG_COLOR = "#1f1f1f"
        BORDER_COLOR = "#404040"
        FIELD_COLOR = "#353535"
        FIELD_HOVER_COLOR = "#046DB9"
        PRIMARY_COLOR = "#046DB9"

        self.image_downloading_event = Event()  # Download event
        self.image_downloader = image_downlod_callback
        self.text_downloader = text_download_callback

        # Toplevel Configurations
        self.title("Download")
        self.place_in_center(520, 140)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)
        # self.grab_set()

        # * Mainframe
        self._mainframe = ctk.CTkFrame(self, border_width=1,
                                       border_color=BORDER_COLOR)
        self._mainframe.grid(row=0, column=0, padx=5, pady=5, sticky="news")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # * DATATYPE Label
        ctk.CTkLabel(self._mainframe, text="Data Format", font=(f"{FONT} semibold", 16),
                     text_color=TEXT_COLOR,).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # * DATATYPES Options Dropdown
        self._options_var = ctk.StringVar(value="IMAGE")
        self._options_menu = ctk.CTkOptionMenu(self._mainframe,
                                               width=120, height=30,
                                               variable=self._options_var,
                                               values=["JSON", "CSV", "IMAGE"],
                                               fg_color=FIELD_COLOR,
                                               corner_radius=5,
                                               button_color="#404040",
                                               button_hover_color=FIELD_HOVER_COLOR,
                                               dropdown_hover_color=PRIMARY_COLOR,
                                               font=(f"{FONT}", 13),
                                               dropdown_font=(
                                                   f"{FONT}", 12),
                                               text_color=TEXT_COLOR,
                                               command=self.on_options_changed_datatype
                                               )
        self._options_menu.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        # Tooltip for Options Menu
        CTkToolTip(self._options_menu,
                   follow=False, delay=0.5,
                   message="Select the format of data you want to download",)

        # * Filename Entry
        self._entry_filename = ctk.CTkEntry(self._mainframe,
                                            placeholder_text="Filename",
                                            width=120, height=30,
                                            font=(FONT, 16),
                                            text_color=TEXT_COLOR,
                                            fg_color=FG_COLOR,
                                            corner_radius=3,
                                            border_width=1,
                                            border_color=BORDER_COLOR)
        # Tooltip for Entry filename
        CTkToolTip(self._entry_filename,
                   follow=False, delay=0.5,
                   message="Type in the name for the selected file (without extension)",)

        # * Quality Options Dropdown
        self._options_quality = ctk.CTkOptionMenu(self._mainframe,
                                                  width=120, height=30,
                                                  values=[
                                                      "High Quality", "Low Quality"],
                                                  fg_color=FIELD_COLOR,
                                                  corner_radius=5,
                                                  button_color="#404040",
                                                  button_hover_color=FIELD_HOVER_COLOR,
                                                  dropdown_hover_color=PRIMARY_COLOR,
                                                  font=(
                                                      f"{FONT}", 13),
                                                  dropdown_font=(
                                                      f"{FONT}", 12),
                                                  text_color=TEXT_COLOR,
                                                  )
        self._options_quality.grid(
            row=0, column=2, sticky="w", padx=10, pady=10)
        # Tooltip for Quality Options
        CTkToolTip(self._options_quality,
                   follow=False, delay=0.5,
                   message="Choose the quality of image",)

        # * Download button
        self._button_download = ctk.CTkButton(self._mainframe,
                                              width=120, height=30,
                                              text="Download",
                                              corner_radius=4,
                                              font=(f"{FONT} bold", 15),
                                              text_color=TEXT_COLOR,
                                              hover_color="#0E4F81",
                                              fg_color="#046DB9",
                                              command=self.start_download)
        self._button_download.grid(
            row=0, column=3, sticky="e", padx=10, pady=10)
        # Tooltip for Download button
        CTkToolTip(self._button_download,
                   follow=False, delay=0.5,
                   message="Start download",)

        self._dir_field = DirectoryField(self._mainframe)
        self._dir_field.grid(row=1, column=0, columnspan=3,
                             sticky="ew", padx=10, pady=10)

        # * Cancel button
        self._button_cancel = ctk.CTkButton(self._mainframe,
                                            width=120, height=30,
                                            state="disabled",
                                            text="Cancel",
                                            corner_radius=4,
                                            font=(
                                                f"{FONT} bold", 15),
                                            text_color=TEXT_COLOR,
                                            border_width=1,
                                            border_color="#404040",
                                            hover_color="#7C0902",
                                            fg_color="#353535",
                                            command=self.cancel_download)
        self._button_cancel.grid(
            row=1, column=3, sticky="e", padx=10, pady=10)
        # Tooltip for Cancel button
        CTkToolTip(self._button_cancel,
                   follow=False, delay=0.1,
                   message="Cancel download",)

        # * Download button spacing
        self._mainframe.columnconfigure(3, weight=1)

        # * Progress Bar
        self._progress_bar = ttk.Progressbar(self,)

    def on_options_changed_datatype(self, value=None):
        """ Callback on options values change """
        if value in ["JSON", "CSV"]:
            # Textual data
            self._options_quality.grid_forget()
            self._entry_filename.grid(
                row=0, column=2, sticky="w", padx=10, pady=10)

        else:
            # Image data
            self._entry_filename.grid_forget()
            self._options_quality.grid(
                row=0, column=2, sticky="w", padx=10, pady=10)

    def place_in_center(self, width, height):
        """ Places `self` in the center of the screen """
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        geo_string = f"{width}x{height}+{x}+{y}"
        self.geometry(geo_string)

    def show_progress_bar(self):
        """
        ### Show Progress bar
        shows the progress bar
        """
        # Place the bar
        self._progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    def hide_progress_bar(self):
        """
        ### Hide Progress bar
        hides the progress bar
        """
        # Reset & Hide the bar
        self.reset_progress_bar()
        self._progress_bar.grid_forget()

    def reset_progress_bar(self):
        """
        ### Reset Progress Bar
        Reset the progress bar back to default state
        """
        self._progress_bar['value'] = 0

    def start_download(self):
        """
        ### Start Download
        Gets user data and Starts the downloaders
        """
        # * Data Format
        format_ = self._options_menu.get()

        quality_, filename_ = None, None
        if format_ == "IMAGE":
            quality_ = self._options_quality.get()
        else:
            filename_ = self._entry_filename.get()
            if not filename_:
                messagebox.showerror("Invalid Filename",
                                     "Filename not found.\nPlease enter a filename for your file.")
                self.get_focus_force(0)
                return

        # * Get Save Path
        directory_ = self._dir_field.get_dir()
        if not directory_:
            messagebox.showerror(
                "Invalid Directory", "Directory not found.\nPlease enter a folder to save your data.")
            self.get_focus_force(0)
            return

        # Initiate Download
        self._button_download.configure(state="disabled")
        self.show_progress_bar()
        self._button_cancel.configure(state="normal")
        if format_ == "IMAGE":
            self.image_downloader(
                directory_, quality_, self.on_progress, self.image_downloading_event)
        else:
            self.text_downloader(format_, filename_, directory_)

    def on_progress(self, tasks_):
        """
        ### On Progress
        call this function at each download
        """
        # Increase the Progress
        self._progress_bar['value'] += round((1/tasks_)*100, 5)

    def get_focus_force(self, after: int):
        """ 
        ### Get Focus Force
        `DownloadDialog` gets focus forcefully after `after` milliseconds.
        """
        self.after(after, self.lift)
        self.after(after, self.focus_force)

    def cancel_download(self):
        """ 
        ### Cacnel Download
        Cancel the download by setting `image_downloading_event`  to true.
        """
        self._button_cancel.configure(state="disabled")
        self.image_downloading_event.set()
        self.after(0, self.hide_progress_bar)
        self._button_download.configure(state="normal")
        messagebox.showinfo("Download Cancelled",
                            "Your Download has been cancelled!")
        self.get_focus_force(0)

    def close_dialog(self):
        """
        ### Close Dialog
        Close the dialog aka DESTROY!
        """
        try:
            if not self.image_downloading_event.is_set():
                self.image_downloading_event.set()
        except Exception as e:
            print("Error occurred:", e)

        self.after(0, self.destroy)


class ImageItemFrame(ctk.CTkFrame):
    """ 
    ### Image Item Frame
    This custom widget will be a image item frame that will display the information
    about an image in a more UI friendly way.
    """

    def __init__(self, master,
                 title, thumb_url,
                 image_type, size,
                 dimensions, uploaded,
                 uploader, views, likes,
                 *args, **kwargs):

        super().__init__(master, height=100,
                         corner_radius=5,
                         border_width=1, fg_color="#353535",
                         *args, **kwargs)

        # Colors
        title_color = "#bbbbbb"
        details_color = "#999999"

        # * Add thumbnail
        self.thumbnail = None
        self.load_thumbnail(thumb_url, size=80)
        ctk.CTkLabel(self, text="", image=self.thumbnail).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")

        # * Create a description frame
        self.description_frame = ctk.CTkFrame(
            self, height=80, corner_radius=0, fg_color="transparent")
        self.description_frame.grid(
            row=0, column=1, padx=5, pady=5, sticky="news")
        self.columnconfigure(1, weight=1)
        self.description_frame.columnconfigure(0, weight=1)
        self.description_frame.rowconfigure(0, weight=1)
        self.description_frame.rowconfigure(1, weight=1)

        # Create a title
        ctk.CTkLabel(self.description_frame, text=title,
                     font=("Segoe UI Bold", 20), anchor="sw",
                     text_color=title_color,).grid(row=0, column=0,
                                                   padx=5, pady=5, sticky="news")

        # Create details_frame
        self.details_frame = ctk.CTkFrame(
            self.description_frame, fg_color="transparent", corner_radius=0)
        self.details_frame.grid(row=1, column=0, padx=0, pady=2, sticky="wn")

        # Add items in details_frame
        items_values = {
            "Type": f"{image_type} File",
            "Size": size,
            "Dimensions": dimensions,
            "Uploaded": uploaded,
            "Uploader": uploader,
        }
        for index, key_value in enumerate(items_values.items()):
            ctk.CTkLabel(self.details_frame, text=f"{key_value[0]}: {key_value[1]}",
                         font=("Segoe UI bold", 13), text_color=details_color,
                         anchor="nw").grid(row=0, column=index,
                                           padx=5, pady=1, sticky="nw")

        # * Create view_likes frame
        self.view_likes_frame = ctk.CTkFrame(
            self, height=80, corner_radius=0,
            fg_color="transparent",
        )
        self.view_likes_frame.grid(
            row=0, column=2, padx=5, pady=5, sticky="ens")
        self.view_likes_frame.rowconfigure(0, weight=1)

        # Views label
        self.views_icon = ctk.CTkImage(
            dark_image=Image.open("assets\\views_light_16px.png"))
        ctk.CTkLabel(self.view_likes_frame, text=f"{views} ", image=self.views_icon,
                     font=("Segoe UI bold", 15), text_color=details_color, compound="right",
                     anchor="s").grid(row=0, padx=5, pady=5, sticky="e")

        # Likes Label
        self.likes_icon = ctk.CTkImage(
            dark_image=Image.open("assets\\likes_light_16px.png"))
        ctk.CTkLabel(self.view_likes_frame, text=f" {likes} likes ", image=self.likes_icon,
                     font=("Segoe UI bold", 15), text_color=details_color, compound="right",
                     anchor="n").grid(row=1, padx=5, pady=5, sticky="e")

    def load_thumbnail(self, url, size=90):
        """ 
        ### Load thumbnail
        loads the thumbnail and stores a reference in `self.thumbnail`
        """
        try:
            raw_data = requests.get(url).content
            image = Image.open(BytesIO(raw_data))

            self.thumbnail = ctk.CTkImage(image, size=(size, size))
        except Exception as e:
            # ? Uncomment to print error
            # print("Thumbnail not found: {}".format(e))
            # ? Load default image thumbnail
            self.thumbnail = ctk.CTkImage(Image.open(
                "assets\\thumb_preview.jpg"), size=(80, 80))

