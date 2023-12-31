""" 
Handles all the backend logics
"""

from imgpile import ImgPile


class Backend:
    def __init__(self):
        self.img_api = ImgPile()
        pass

    def get_response(self, url):
        """ 
        ### Get Response
        This method talks directly to the API and returns a response from it
        """
        return self.img_api.get(url)