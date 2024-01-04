""" 
Handles all the backend logics
"""

from imgpile import ImgPile
import requests
import os
from os import mkdir
from os import path


class Backend:
    def __init__(self):
        self.img_api = ImgPile()
        pass

    def get_response(self, url, logwindow):
        """ 
        ### Get Response
        This method talks directly to the API and returns a response from it
        """
        return self.img_api.get(url, logwindow)

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

    def download_images(self, image_url, filename, save_path):
        """Downloads all images in local storage"""
        # Create folder
        if path.exists(save_path):
            print("Path Already Exists!")
            pass
        else:
            os.mkdir(save_path)

        # directory
        directory = path.join(save_path, filename)

        # If file does not exists, download
        if not path.exists(directory):
            # Download the image content
            raw_image_data = requests.get(image_url).content
            # Save image
            with open(directory, 'wb') as img:
                img.write(raw_image_data)
