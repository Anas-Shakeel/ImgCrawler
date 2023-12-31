"""
# API for imgpile.com 
This api scraps the imgpile.com website and sends back a list of 
dictionaries of images and their data.
"""

import os
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


class ImgPile:
    def __init__(self) -> None:
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def get(self, url: str):
        """ 
        ### Get
        This method will get the data you need regarding given `url`.
        """
        # Stores all pages after calling 'extract_pages()' method
        self.all_pages = [url]

        # stores all images after calling 'extract_images()' method
        self.all_images = []

        return url
        ...

    def get_title(self):
        """extract Title from Webpage"""
        # access main url
        r = requests.get(self.url, headers=self.headers)

        # extract title
        head_title = SoupStrainer("title")
        soup = BeautifulSoup(r.text, 'html.parser', parse_only=head_title)

        # return title
        return soup.text

    def extract_pages(self):
        """Extracts all page links"""
        print("Extracting pages...")

        def recurse(page):
            # accessing page
            try:
                response = requests.get(page, headers=self.headers)
            except requests.exceptions.MissingSchema:
                return

            # extracting next_page_link
            pagination = SoupStrainer(
                "ul", {"class": "content-listing-pagination visible"})
            soup = BeautifulSoup(response.text, 'html.parser',
                                 parse_only=pagination)

            # extract next_page_link
            # if link found, store and call next iteration
            next_page = ""
            try:
                next_page = soup.select_one("li.pagination-next a").get("href")
            except AttributeError:
                pass
            if next_page is not None:
                self.all_pages.append(next_page)
                recurse(next_page)
            else:
                return

        # calling a recursive function to extract all pages
        recurse(self.url)

    def extract_images(self):
        """Extract all image links from current page"""
        # from each page, extract images
        for page in self.all_pages:
            if page == "":
                break
            # accessing current page
            r = requests.get(page, headers=self.headers)

            # Extracting its HTML
            content_div = SoupStrainer(
                "div", attrs={"id": "content-listing-tabs"})
            soup = BeautifulSoup(r.text, "html.parser", parse_only=content_div)

            # iterating through each image and extracting its image's page links
            for tag in soup.select("a.image-container"):
                # printing image links
                print("Extracting: ", tag['href'])

                # accessing image's page
                r = requests.get(tag['href'], headers=self.headers)

                # extracting its HTML
                # link_div = SoupStrainer("div", {"class":"header-content-right"})
                link_div = SoupStrainer(
                    "a", {"class": "btn btn-download default"})
                soup = BeautifulSoup(
                    r.text, "html.parser", parse_only=link_div)

                # extracting download link and storing in 'all_images' list
                self.all_images.append(soup.a['href'])

    def download_images(self):
        """Downloads all extracted images"""
        # create folder
        if os.path.exists(self.title):
            print("Path Already Exists!")
        else:
            os.mkdir(self.title)
            print(f"Created Folder: {self.title}")

        print(f"*** {len(self.all_images)} images will be download ***")

        # downloading images one by one
        for link in self.all_images:
            try:
                # get file name
                name = os.path.basename(link)

                # directory
                directory = os.path.join(self.title, name)

                # if file exists, skip
                if os.path.exists(directory):
                    continue
                else:
                    # download the image, otherwise
                    response = requests.get(link, headers=self.headers)
                    # saving image
                    with open(directory, 'wb') as img:
                        img.write(response.content)
            except:
                continue

    def execute(self):
        """ Executes the whole Scrap """
        self.extract_pages()
        self.extract_images()
        self.download_images()


# ! What This API Sould Have?
""" 
Must have a function that takes a url repeatedly!
Give back the result.
"""

# ! What This API Sould Do?
"""
take a url as input
extract the data required!
return the data back as a list of dicts of data
"""

# ! What This API Shouldn't Do?
"""
Downloading
printing anything to the console
getting the title

"""
