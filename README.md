<h1 align="center"> Img-Crawler </h1>

## **Description**
> `Img-Crawler` is a __GUI__ application that downloads bulks of images from [imgpile.com](https://imgpile.com/). </br> It uses a _Custom API_ i created in python that scraps an album's `url` and returns every image's details as `json` data.

## **Usage**
1. Install [Python 3.x](https://www.python.org/download)
2. __Download__ or __clone__ this repository on your local machine.
3. Extract the `zip` file.
4. Open terminal in this folder and run `pip install -r requirements.txt`
5. Run `main.py` either from terminal or just by double-clicking it.


## **Libraries used in this project**
> ### **Third-party**
> `CustomTkinter` `CTkTooltip` `Pandas` `BeautifulSoup` `Requests` `Pillow` `SoupSieve`
> ### **Built-in**
> `Json` `Tkinter` `Threading` `IO` `Time` `OS`


## **imgpile API**
> [**imgpile**](https://github.com/Anas-Shakeel/imgpile-custom-api) is a custom _API_ i wrote in python that extracts data of every image in an album from [impile.com](https://imgpile.com) website and sends a `json` response back. It's not an actual proper "API", it just acts like one! </br>

__Response:__ Below is the response that this API returns:
``` json
[
    {
        "image_url": "URL of image.extension",
        "image_link": "Link to the image",
        "thumb_url": "URL of thumbnail.extension",
        "lq_url": "URL of low-quality image.extension",
        "title": "Image title",
        "size": "32.2 MB",
        "resolution": "5232 x 7845",
        "image_type": "JPG",
        "views": "View count of this image",
        "likes": "Like count of this image",
        "uploader": "Name of uploader of this image",
        "uploaded": "1 year ago"
    },
    {
        ...
    },
    {
        ...
    }
]
```

## **Note**
> I am currently working on this project so the code will be under development for a week or two!