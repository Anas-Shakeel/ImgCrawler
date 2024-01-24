<h1 align="center"> Img-Crawler </h1>

## **Description**
> `Img-Crawler` is a __GUI__ application that downloads bulks of images from [imgpile.com](https://imgpile.com/). </br> It uses a _Custom API_ i created in python that scraps an album's `url` and returns every image's details as `json` data.

## **Features**
- Download the images in bulk.
- Modern & User Friendly UI.
- Easy to use.
- Scrape today, Download Tommorow Functionality.
- Download in Multiple Formats.
- Original Quality Preserved.
- And more under-the-hood stuff

## **Usage**
__NOTE:__ Executable file is on it's way! and then you won't need to do the steps below!
> ### **How to install:**
> 1. Install [Python 3.x](https://www.python.org/download)
> 2. __Download__ or __clone__ this repository on your local machine.
> 3. Extract the `zip` file.
> 4. Open terminal in this folder and run `pip install -r requirements.txt`
> 5. Run `main.py` either from terminal or just by double-clicking it.
>
>
> ### **How to use:**
> - Go to [imgpile.com](https://imgpile.com/) & search for an album. </br>
> - In this demo, I will search for "_Ford Mustang_". **(WARNING: Results may include inappropriate content)** </br>
> ![search_results](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/ba388eb6-40a2-4de3-bd5b-7c8b835e988c)
> - Now, _Copy_ the **url** of this album __(make sure you are on the first page of this album because the [imgpile-scrapper-api](https://github.com/Anas-Shakeel/imgpile-custom-api) starts the scrape from the page you copied the **url** from)__. in our case, there's only one page. <br>
> - Open the `ImgCrawler` application and paste the url in __Target URL__ field.
> ![paste_url](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/c452fcf5-4d4d-41ea-a40d-1582075093db) <br>
> - Click **Scrape** button and let the app do it's thing! __(You can now do other things while this app scrapes the images. It'll let you know when the scrape is finished!)__
> - Once scraping is finished, You'll see the images and their properties.<br>
> ![scraped](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/1b7f89b3-bdcd-4d01-87f9-9692f778ec7c) <br>
> - Click __Download__ button at the _bottom-right_, a Dialog box will appear asking for some things.<br>
> ![download_dialog](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/d4b4472e-afe0-4727-91c6-1e34d15a17b3) <br>
>
> - Choose the type of data you want to download (`image`, `json` or `csv`). <br>
> - Choose the __quality__ of images (if `image` selected) <br>
> 
> - ![download_dialog_options](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/3ca28f1b-8b59-4f25-9c58-4d18c40cab73) <br>
> 
> - __OR__ Type in the **filename** (without extension) for a json or csv file (if `json` or `csv` selected) <br>
> 
> - ![json-format](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/98cb8f26-977d-443d-bf19-b396a5bd700f) <br>
> 
> - Type a directory to save the files __OR__ Choose a directory by clicking the button with folder icon, DUHH! <br>
> 
>
> - Click __Download__ and let the downloading happen! **(Do your thing again! and when the downloading is complete, You'll get notified.)** <br>
>
>
> - __Downloaded Images__:
> ![images-downloaded](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/691b83f1-8c09-44b3-978a-e59c3d6e29d9) <br>
>
> - __Download Json__:
> ![json-downloaded](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/581b6c82-845b-4b78-9d97-7679ca7e488a) <br>
>
>
> **Cool Trick:** This `Demo.json` file can now be loaded in the app! allowing you to download the scraped images whenever you want!
> 
> ### Loading Json Files
> - Once you have the json data, you can close the application!
> - Open the application again.
> - Press `CTRL+SHIFT+L` and select & open the json file when dialog appears.
> ![load-json](https://github.com/Anas-Shakeel/ImgCrawler/assets/131923402/9d0e4cb1-02d5-46e6-8125-79c830e5d1d1) <br>
> 
> The file will be loaded in the application and the imnages will start to appear as they load!<br>
> **This loading will be faster than the actual scraping!** <br>
>
> #### _Demo Ends Here!_
> Use the application and let me know if any bugs found! cuz there'll be alot of them! <br>
> ___Oh! and the `cancel` button (next to scrape button) doesn't work yet. I'm working on it!!!___
>

## Project structure
> `assets`<br>
> `main.py`
> `frontend.py`
> `backend.py`
> `imgpile.py`

## **Libraries used in this project**
> ### **Third-party**
> `CustomTkinter` `CTkTooltip` `Pandas` `BeautifulSoup` `Requests` `Pillow` `SoupSieve`
> ### **Built-in**
> `Json` `Tkinter` `Threading` `IO` `Time` `OS`
