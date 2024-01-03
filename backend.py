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

    def to_bytes(self, _size=137.5, _unit="MB"):
        """
        ### To Bytes
        Converts other Data Storage units to bytes

        ### Note
        It also selects sizes like "5.2 mb" etc

        ```
        >> fm._to_bytes(_size="5.0 kb")
        5120

        >> fm._to_bytes(_size="5.0 mb")
        5242880
        ```
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

        # ? Calculate bytes
        # Unit Factors
        factors = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 ** 2,
            "GB": 1024 ** 3,
        }

        # ? Calculate bytes
        return factors[unit] * size
