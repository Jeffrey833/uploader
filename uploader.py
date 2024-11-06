import requests
import bs4
import time
import re, sys
import argparse
import os
import json
import shutil
import asyncio
from magnet_parser import magnet_decode
from main import create_jwt, upload, download_video, find_file

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

session = requests.Session()


def make_filename_safe(filename, divider):
    safe_filename = re.sub(r"[^a-zA-Z0-9]", divider, filename)

    safe_filename = re.sub(r"-+", "-", safe_filename).strip("-")
    return safe_filename


# Step 1: Define a function to convert file size to megabytes
def convert_to_mb(file_size):
    match = re.match(r"([\d.]+)\s*([KMG]iB)", file_size)
    if match:
        size = float(match.group(1))
        unit = match.group(2)
        if unit == "GiB":
            return size * 1024  # Convert GiB to MiB
        elif unit == "KiB":
            return size / 1024  # Convert KiB to MiB
        return size  # Assume it's already in MiB
    return None  # If the format is unrecognized


def cari_magnet(query, max_retries=7):
    url = f"https://tpirbay.xyz/search/{query}/1/99/200".strip()

    data = {}
    datas = []
    for attempt in range(max_retries):
        try:
            session.headers = headers
            result = session.get(url, headers=headers)
            assert result.status_code == 200, result.status_code

            soup = bs4.BeautifulSoup(result.text, "html.parser")

            # Step 2: Find all rows in the table
            rows = soup.findAll("td")

            # Step 3: Process each row
            torrent_data = []

            for row in rows:
                data = {}

                # Extract the torrent title
                title_div = row.find("div", class_="detName")
                if title_div:
                    torrent_title = title_div.find("a").text
                    data["title"] = torrent_title

                # Extract the magnet link
                magnet_link = row.find(
                    "a", href=lambda x: x and x.startswith("magnet:")
                )
                if magnet_link:
                    data["magnet"] = magnet_link["href"]

                # Extract uploaded info
                uploaded_info = row.find("font", class_="detDesc")
                if uploaded_info:
                    uploaded_text = uploaded_info.text

                    # Extract file size using regex
                    size_match = re.search(
                        r"Size\s*([\d.]+)\s*([A-Za-z]+)", uploaded_text
                    )
                    if size_match:
                        file_size = size_match.group(1) + " " + size_match.group(2)
                        data["file_size"] = file_size
                    else:
                        data["file_size"] = ""

                torrent_data.append(data)

            if torrent_data:
                torrent_data = [d for d in torrent_data if d]
                # Step 2: Filter based on conditions
                filtered_data = [
                    d
                    for d in torrent_data
                    if "720" in d["title"]
                    and (
                        (size := convert_to_mb(d["file_size"])) is not None
                        and (size < 2000)
                    )
                ]
                return filtered_data

            print(f"Unexpected response on attempt {attempt + 1}. Retrying...")
            # input()

        except Exception as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")

        time.sleep(2)

    print("Max retries exceeded. Returning None.")
    return None


def main(query, max_attempt):
    result = cari_magnet(query, max_attempt)
    if not result:
        # sys.exit(print('TPB error, there is no magnet datas'))
        return

    # os.makedirs('magnet', exist_ok=True)

    filename = make_filename_safe(result[0]["title"], "_")
    with open(f"magnet/{filename}", "w") as file:
        file.write(json.dumps(result, indent=4))
        file.close()

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch torrents from TPB by ID.")
    parser.add_argument("start_id", type=int, help="ID to start fetching from")
    args = parser.parse_args()

    start_id = args.start_id

    # Check for the last processed ID, if it exists
    last_id_file = "last_id.txt"
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            last_id = int(f.read().strip())
            start_id = max(start_id, last_id + 1)

    try:
        while True:
            print(f"Processing ID: {start_id}")
            try:
                res = session.get(
                    f"https://api.ini.wtf/items/{start_id}",
                    headers={"Content-Type": "application/json"},
                )

                res.raise_for_status
                data = res.json()

                imdb_id = data["imdb_id"]
                magnet_url = data["magnet_url"]
                title = data["title"]
                image_url = data["cover_url"]


                if magnet_url:
                    print(data)
                    # imdb_id = data["imdb_id"]
                    
                    decoded = magnet_decode(magnet_url)
                    
                    # dir_name = decoded.name
                    # print(magnet_url)
                    # print(dir_name)
                    if download_video(magnet_url):
                        print("Seems downloaded successfully")
                        files = find_file()
                        if files:
                            result = asyncio.run(
                                upload(
                                    file_to_upload=files["file"],
                                    caption=title,
                                    title=title,
                                    image_url=image_url,
                                )
                            )
                            # input('result')
                            print(json.dumps(result, indent=4))
                            if result:
                                decoded_result = create_jwt(result)
                                data["description"] = "updated"
                                data["is_uploaded"] = True
                                data["video_id"] = decoded_result
                                put_request=(session.put(f"https://api.ini.wtf/items/{imdb_id}", json=data))

                                print(
                                    json.dumps(put_request, indent=4) if put_request.json() else print('removing file root..')
                                )
                                shutil.rmtree(files["root"])
                            else:
                                sys.exit(print("Upload failed."))
                        else:
                            sys.exit(print('Download failed.'))
                    start_id += 1
                    

                # imdb_id = 
                title = make_filename_safe(data.json()["title"], " ")
                querys = title.split()
                querys.pop()

                query = " ".join(v for v in querys).lower()

                print(f"querying.. {query}")
                results = main(query, 3)

                if results:
                    new_data = data.json()
                    magnet = results[0]["magnet"]

                    new_data["magnet_url"] = magnet
                    r = requests.put(
                        f"https://api.ini.wtf/items/{imdb_id}",
                        headers={"Content-Type": "application/json"},
                        json=new_data,
                    )
                    print(r)
                print(json.dumps(results, indent=4))
            except Exception as e:
                print(f"Error posting data for '{data['title']}': {str(e)}")
            start_id += 1

            # Save the last processed ID
            with open(last_id_file, "w") as f:
                f.write(str(start_id))

    except KeyboardInterrupt:
        print(f"\nStopped by user. Last processed ID: {start_id - 1}")
        with open(last_id_file, "w") as f:
            f.write(str(start_id - 1))

    except Exception as e:
        print(f"An error occurred: {e}")
        with open(last_id_file, "w") as f:
            f.write(str(start_id - 1))
