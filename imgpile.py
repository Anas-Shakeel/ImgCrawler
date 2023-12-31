"""
# API for imgpile.com 
This api scraps the imgpile.com website and sends back a list of 
dictionaries of images and their data.
"""

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
        # Extract all pages
        pages = self.extract_pages(url)

        # Stores all pages & images
        master_data = []
        # Iterate through every page and extract image links
        for page in pages:
            for link in self.extract_image_links(page):
                master_data.append(self.extract_image_data(link))

        return master_data

    def extract_pages(self, start_page):
        """Extracts all page links"""
        # will hold page links
        temp_pages = [start_page]

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

            # Extract next_page_link
            next_page = ""
            try:
                next_page = soup.select_one("li.pagination-next a").get("href")
            except AttributeError:
                pass
            if next_page:
                temp_pages.append(next_page)
                recurse(next_page)
            else:
                return

        # calling a recursive function to extract all pages
        recurse(start_page)
        return temp_pages

    def extract_image_links(self, page):
        """ 
        ### Extract Image Links
        extracts all image links and yields the url
        """
        # accessing current page
        r = requests.get(page, headers=self.headers)

        # Extracting its HTML
        content_div = SoupStrainer(
            "div", attrs={"id": "content-listing-tabs"})
        soup = BeautifulSoup(r.text, "html.parser", parse_only=content_div)

        # iterating through each image and extracting its image's page links
        for tag in soup.select("a.image-container"):
            # Extracting image link
            yield tag['href']

    def extract_image_data(self, image_url):
        """ 
        ### Extract Image Data
        extracts all the image data and returns it as a dictionary
        """
        # accessing image's page
        r = requests.get(image_url, headers=self.headers)

        # Extracting HTML
        link_div = SoupStrainer(
            "div", {"class": "content-width"})
        soup = BeautifulSoup(
            r.text, "html.parser", parse_only=link_div)

        # * EXTRACTING BEGINS
        title = soup.find("h1", class_="viewer-title").text
        uploader = soup.find("span", class_="breadcrum-text float-left").text.strip()

        # Image metadata
        image_metadata = soup.find(
            "a", class_="btn btn-download default")['title'].split("-")
        temp = image_metadata[1].strip().split()
        image_type = temp[0]
        image_size = f"{temp[1]} {temp[2]}"
        image_res = image_metadata[0].strip()

        # Views and likes
        views_likes_meta = soup.select(
            "div.header div.header-content-right")[-1].text.strip().split("\n")
        views = views_likes_meta[0]
        likes = views_likes_meta[1].strip()

        # Image links storage
        urls = [''] * 4
        embed_codes = soup.select("div.panel-share div.panel-share-item")[0]
        for index, code in enumerate(embed_codes.find_all("div", class_="panel-share-input-label copy-hover-display")):
            urls[index] = code.input['value']

        uploaded = soup.find(
            "p", class_="description-meta margin-bottom-5").span.text

        # ? Creating data dictionary & returning
        return {
            "image_url": urls[0],
            "image_link": urls[1],
            "thumb_url": urls[2],
            "lq_url": urls[3],
            "title": title,
            "size": image_size,
            "resolution": image_res,
            "image_type": image_type,
            "views": views,
            "likes": likes,
            "uploader": uploader,
            "uploaded": uploaded
        }
