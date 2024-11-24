import undetected_chromedriver as uc
import bs4, time, os, subprocess

from telethon import TelegramClient, types, events

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Replace these with your own values
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

recipient = ""  # Username or ID of the recipient
group_id = ""

# Define color codes
GREEN = '\033[0;32m'  # Green color
NC = '\033[0m'        # No Color (reset)

def get_page_source(url: str = "https://google.com"):
    # Set up the WebDriver for Firefox
    options = Options()
    options.add_argument("-private")
    # Uncomment the line below if you want to run in headless mode
    # options.add_argument("--headless")

    # Create a new instance of the Firefox driver
    d = webdriver.Firefox(service=FirefoxService(), options=options)
    # d = uc.Chrome(version_main=129)
    d.get(url)
    try:
        WebDriverWait(d, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    except Exception as e:
        print(f"An error occurred: {e}")

    return d


def get_slug(page_source: str, filename: str):
    soup = bs4.BeautifulSoup(page_source, "html.parser")

    # Find all <figure> elements with class 'grid-poster'
    figures = soup.find_all("figure", class_="grid-poster")

    # Extract links from each figure
    links = []
    for figure in figures:
        a_tag = figure.find("a")
        if a_tag and "href" in a_tag.attrs:
            links.append(a_tag["href"])

    if links:
        with open(filename, "a+") as file:
            file.write("\n".join([v for v in links]))
            file.write("\n")


def get_download_url(page_source: str):
    # Parse the HTML with BeautifulSoup
    soup = bs4.BeautifulSoup(page_source, "html.parser")

    # Find all <a> tags in the table
    download_links = [a["href"] for a in soup.select("tbody a") if "href" in a.attrs]

    if download_links:
        return download_links

    else:
        return []


def get_lk21_slug():
    driver = get_page_source()
    genres = [
        "action",
        "adventure",
        "animation",
        "biography",
        "comedy",
        "crime",
        "documentary",
        "drama",
        "family",
        "fantasy",
        "film-noir",
        "history",
        "horror",
        "music",
        "musical",
        "mystery",
        "romance",
        "sci-fi",
        "sport",
        "thriller",
        "war",
        "western",
    ]
    for genre in genres:
        for i in range(300):
            url = f"https://tv.lk21official.pics/genre/{genre}/page/{i+1}"
            try:
                driver.get(url)
                if "404" in driver.title:
                    break

                page_source = driver.page_source
                get_slug(page_source)
            except Exception as e:
                print(e)


def get_lk21_download_url():
    slugs = open("slug.sorted.txt", "r").read().splitlines()

    d = get_page_source()
    i = 0
    for slug in slugs:
        i += 1
        title = slug.rstrip("/").split("/")[-1]
        url = f"https://dl.lk21.party/get/{title}/"

        if i % 10 == 0:
            print(i, "deleting cookies..")
            d.delete_all_cookies()
        d.get(url)
        page_source = d.page_source

        download_links = get_download_url(page_source)
        if download_links:
            with open("download_links.txt", "a+") as file:
                file.write(f"{title},{','.join([v for v in download_links])}")
                file.write("\n")


def get_file_size_in_mb(file_path):
    # Get the file size in bytes
    file_size_bytes = os.path.getsize(file_path)

    # Convert bytes to megabytes
    file_size_mb = file_size_bytes / (1024 * 1024)

    return file_size_mb



def direct_download(url: str, slug: str):
    d = get_page_source()
    filemoon_download_url = url.replace(
        "filemoon.in", "filemoon.sx"
    )
    d.get(filemoon_download_url)
    d.set_window_size(489, 667)
    d.refresh()

    # Wait indefinitely until the specific element is present
    while True:
        try:
            if "Not Found" in d.title:
                break
            # Adjust the selector as needed to target the specific <a> element
            element = WebDriverWait(d, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.button[download]")
                )
            )

            print(f"Download link appear")
            download_link = element.get_attribute("href")

            filename = f"{slug}.mp4"
            result = os.system(
                f"bash mcurl -s 8 -o '{filename}' '{download_link}'"
            )

            if result == 0:
                # assert (
                #     os.system(f"python main.py {filename}") == 0
                # ), "download error"

                subprocess.Popen(["python", "main.py", filename])
                # os.remove(filename)
            # elif result == 2:
            #     d.delete_all_cookies()
            #     d.refresh()

            break  # Exit the loop if the element is found
        except Exception as e:
            # print(e)
            print(f"{GREEN}Lagi nungguin tombol download..{NC}")

    # input()

def telegram_sender():
    client = TelegramClient("iuploadyou", api_id, api_hash)

    @client.on(events.NewMessage(from_users=recipient))
    async def handler(event):
        # This will handle the messages received from the bot
        print(f"Received message from bot: {event.message.message}")
        if event.message.media:
            # Send the video file to the group
            await client.send_file(
                group_id, event.message.media, caption=event.message.message
            )

    async def send_message():
        await client.start()  # Start the client

        urls = open("download_links.txt", "r").read().splitlines()
        # d = get_page_source()

        for url in urls:
            download_urls = url.split(",")
            download_url = [u for u in download_urls if "filemoon.in" in u]
            telegram_url = [u for u in download_urls if "telegram.php" in u]
            if telegram_url:
                # print(telegram_url)
                # Send a message

                time.sleep(5)
                await client.send_message(
                    recipient, f"/start {telegram_url[0].split('id=')[-1]}"
                )

    # Run the client
    with client:
        client.loop.run_until_complete(send_message())


def get_top_movie():
    BASE_URL = 'https://tv.lk21official.pics/top-movie-today'

    MAX_PAGE = 1134
    d = get_page_source()

    for c in range(MAX_PAGE):
        try:
            url = f'{BASE_URL}/page/{c}'
            
            d.get(url)
            page_source = d.page_source
            get_slug(page_source, 'slug_top_movie.txt')
            if "404" in d.title:
                break

        except Exception as e:
            print({"error":e})
            continue

def download():
    urls = open("download_links.txt", "r").read().splitlines()
    d = get_page_source()

    i = 0
    download_urls = [url.split(",") for url in urls]
    for urls in download_urls:
        i += 1

        slug = urls[0]
        download_url = [u for u in urls if "filemoon.in" in u]
        telegram_url = [u for u in urls if "telegram.php" in u]

        file = open('iniDownloadLink.temp', 'a+')
        link = file.read().splitlines()
        
        if len(link)>=3:
            input('saatnyua download y/n')
            for l in link:
                dlink = l.split(' || ')[0]
                fname = l.split(' || ')[1]
                assert os.system(f'bash mcurl -s 8 -o "{fname}" "{dlink}"') == 0, 'download error'

        if telegram_url:
            print("skipping", i)
            continue

        print(i)
        if i % 10 == 0:
            d.delete_all_cookies()
            d.refresh()

        if download_url:
            filemoon_download_url = download_url[0]
            filemoon_download_url = filemoon_download_url.replace(
                "filemoon.in", "filemoon.sx"
            )
            d.get(filemoon_download_url)
            d.set_window_size(667, 667)
            time.sleep(2)

            d.refresh()

            # Wait indefinitely until the specific element is present
            while True:
                try:
                    if "Not Found" in d.title:
                        break
                    # Adjust the selector as needed to target the specific <a> element
                    element = WebDriverWait(d, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "a.button[download]")
                        )
                    )

                    print(f"Download link appear")
                    download_link = element.get_attribute("href")

                    filename = f"{slug}.mp4"
                    # result = os.system(
                    #     f"bash mcurlv3.sh -o \"{filename}\" \"{download_link}\""
                    # )

                    if not len(link)>=3:
                        file.write(f'{download_link} || {filename}')
                        file.write('\n')

                    break

                        

                        

                    # if result == 0:
                        # assert (
                        #     os.system(f"python main.py {filename}") == 0
                        # ), "download error"

                        # subprocess.Popen(["python", "main.py", filename])
                        # os.remove(filename)
                    # elif result == 2:
                    #     d.delete_all_cookies()
                    #     d.refresh()

                except Exception as e:
                    # print(e)
                    print(f"{GREEN}Lagi nungguin tombol download..{NC}")

            # input()

if __name__ == "__main__":
    download()
    # direct_download('https://filemoon.in/download/y3asnqmmn2ue', 'zombieland-double-tap-2019')

    # get_top_movie()
