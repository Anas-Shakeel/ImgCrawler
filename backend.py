""" 
Handles all the backend logics
"""

from imgpile import ImgPile
import requests
import os
from os import path
import json
import pandas as pd


class Backend:
    def __init__(self):
        self.img_api = ImgPile()
        pass

    def get_response(self, url, event):
        """ 
        ### Get Response
        This method talks directly to the API and returns a response from it
        """
        return self.img_api.get(url, event)

    def get_presaved_data(self, filepath: str) -> list:
        """ 
        ### Get Presaved Data
        Reads `filepath` and returns the json data
        """
        # Open & read the file
        with open(filepath) as datafile:
            # Get the data
            data = json.loads(datafile.read())

        # Validate the data
        if not self.validate_presaved_data(data):
            # Failed Validation
            return None

        # Return the pyobject "DATA"
        return data

    def validate_presaved_data(self, data: list) -> bool:
        """ 
        ### Validate Presaved Data
        validates the data format and returns `True` or `False`

        #### Validation Conditions:
        - `data` must be of type `list`
        - `list[0]` must be a `dict`
        - `list[0]` must have 13 `dict`s
        - `list[0]` must contain `image_url` & `image_link` keys along with 11.
        """
        if not (type(data) == list and type(data[0]) == dict):
            # Datatypes are not valid
            return False

        for dict_item in data:
            if len(dict_item.keys()) != 13:
                # Lengths are not good.
                return False

            if not (dict_item['image_url'] and dict_item['image_link']):
                # Image_url is not ok
                return False

            return True

    def to_bytes(self, _size, _unit: str):
        """
        ### To Bytes
        Converts other Data Storage units to bytes

        ### Note
        It also selects sizes like "5.2 mb" etc
        """
        # Extract values
        size = _size
        unit = _unit

        # size validation
        if size <= 0:
            return 0

        # unit validation
        if not (unit and unit.isalpha() and len(unit) in [1, 2]):
            raise ValueError(f"'{unit}' is not a valid unit")

        # Unit Factors
        factors = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3,
        }

        # Calculate and return bytes
        return round(factors[unit] * size, 3)

    def to_human_readable_storage(self, bytes_size):
        """ 
        ### To Human Readable Storage
        Converts `bytes_size` to human readable format.
        """

        units = ['B', 'KB', 'MB', 'GB', 'TB']

        size = bytes_size
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1

        # Adjust the format to avoid unnecessary decimal places for integers
        formatted_size = "{:.2f}".format(size).rstrip('0').rstrip('.')

        return f"{formatted_size} {units[unit_index]}"

    def filename_increment(self, filepath: str, dst_path=""):
        """
        ### Filename Increment
        Adds an incremented number in the `filepath` if file already exists in `dst_path`

        if `dst_path` is omitted, method will use the `filepath`'s root dir to look 
        if filename exists or not

        ```
        >> FileManager.filename_increment("C:\\file.txt")
        # if file already exists, return another name (incremented)
        'C:\\file 0.txt'

        # otherwise return same name
        'C:\\file.txt'
        ```
        """
        if not path.exists(filepath):
            return filepath

        # Extract filename and extension
        filename = path.splitext(path.basename(filepath))[0]
        ext = path.splitext(filepath)[-1]

        # Set root path
        if dst_path == "":
            root = path.split(filepath)[0]
        else:
            root = dst_path

        # Creating new_name
        new_name = path.join(root, filename + ext)

        # If file exists, Increment
        if path.exists(new_name):
            i = 0
            while (i >= 0):
                new_name = f"{path.join(root, filename)} {i}{ext}"
                if not path.exists(new_name):
                    return new_name
                i += 1
        else:
            return new_name

    def sanitize_string(self, string: str):
        """ 
        ### Sanitize String
        Replaces all invalid (illegal) characters from `string` with underscores `_`.

        ```
        # Illegal characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        ```
        """
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

        sanitized_string = string
        # Replace invalid characters with underscores
        for char in invalid_chars:
            sanitized_string = sanitized_string.replace(char, "_")

        return sanitized_string

    def download_image(self, image_url, filename, save_path, event):
        """Downloads all images in local storage"""
        # URL Check
        if not image_url:
            print(f"Image: '{filename}' has no URL on website, **Skipping**")
            return

        # Create folder
        if not path.exists(save_path):
            os.mkdir(save_path)

        # Create a dirpath, also check if it already exists
        directory = self.filename_increment(path.join(save_path, filename))

        # If file does not exists, download
        if not path.exists(directory):
            # Download the image content
            raw_image_data = requests.get(image_url).content

            # If user cancelled
            if event.is_set():
                return

            # Save image
            with open(directory, 'wb') as img:
                img.write(raw_image_data)

    def download_data(self, data, fileformat, filename, save_path, download_complete_callback):
        """ 
        ### Download DATA
        Downloads the `data` with the `filename` in `format` format in `save_path`
        """
        if not path.isdir(save_path):
            raise ValueError(
                "save_path: value must be an existing directory path.")

        save_dir = path.join(save_path, self.sanitize_string(filename))

        if fileformat == "JSON":
            # * Download as json
            with open(save_dir+".json", "w") as jsonfile:
                json.dump(data, jsonfile, indent=4)

        elif fileformat == "CSV":
            # * Download as CSV
            # Convert to Pandas Dataframe
            df = pd.DataFrame(data)
            # Save Dataframe as CSV
            df.to_csv(save_dir + ".csv", index=False)

        else:
            # Other cases
            raise ValueError(
                "Invalid Format Type: format must be 'JSON' or 'CSV'.")

        # Call `Download Complete Callback` method
        download_complete_callback()

    def download_thumbnail(self, thumb_url: str, thumb_name: str, save_path: str):
        """ 
        ### Download thumbnail
        This method downloads the `thumb_url` with a `thumb_name` in a `save_path`.
        """
        if not path.isdir(save_path):
            os.mkdir(save_path)

        raw_data = requests.get(thumb_url).content
        with open(f"{save_path}\\{thumb_name}", "wb") as thumb:
            thumb.write(raw_data)
