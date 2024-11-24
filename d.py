_K = "telegram.php"
_J = "main.py"
_I = "python"
_H = "a.button[download]"
_G = "Not Found"
_F = "filemoon.sx"
_E = "html.parser"
_D = "links.txt"
_C = "filemoon.in"
_B = "\n"
_A = "href"
import bs4, time, os, subprocess
from telethon import TelegramClient, types, events
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
recipient = ""
group_id = ""
GREEN = "\x1b[0;32m"
RED="\x1b[0;31m"
NC = "\x1b[0m"


def get_page_source(url="https://google.com"):
    B = Options()
    B.add_argument("-private")
    A = webdriver.Firefox(service=FirefoxService(), options=B)
    A.get(url)
    try:
        WebDriverWait(A, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception as C:
        print(f"An error occurred: {C}")
    return A


def get_slug(page_source, filename):
    D = bs4.BeautifulSoup(page_source, _E)
    E = D.find_all("figure", class_="grid-poster")
    A = []
    for F in E:
        B = F.find("a")
        if B and _A in B.attrs:
            A.append(B[_A])
    if A:
        with open(filename, "a+") as C:
            C.write(_B.join([A for A in A]))
            C.write(_B)


def get_download_url(page_source):
    B = bs4.BeautifulSoup(page_source, _E)
    A = [A[_A] for A in B.select("tbody a") if _A in A.attrs]
    if A:
        return A
    else:
        return []


def get_lk21_slug():
    A = get_page_source()
    B = [
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
    for C in B:
        for D in range(300):
            E = f"https://tv.lk21official.pics/genre/{C}/page/{D+1}"
            try:
                A.get(E)
                if "404" in A.title:
                    break
                F = A.page_source
                get_slug(F)
            except Exception as G:
                print(G)


def get_lk21_download_url():
    F = open("slug.sorted.txt", "r").read().splitlines()
    A = get_page_source()
    B = 0
    for G in F:
        B += 1
        C = G.rstrip("/").split("/")[-1]
        H = f"https://dl.lk21.party/get/{C}/"
        if B % 10 == 0:
            print(B, "deleting cookies..")
            A.delete_all_cookies()
        A.get(H)
        I = A.page_source
        D = get_download_url(I)
        if D:
            with open(_D, "a+") as E:
                E.write(f"{C},{",".join([A for A in D])}")
                E.write(_B)


def get_file_size_in_mb(file_path):
    A = os.path.getsize(file_path)
    B = A / 1048576
    return B


def direct_download(url, slug):
    A = get_page_source()
    C = url.replace(_C, _F)
    A.get(C)
    A.set_window_size(489, 667)
    A.refresh()
    while True:
        try:
            if _G in A.title:
                break
            D = WebDriverWait(A, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, _H))
            )
            print(f"Download link appear")
            E = D.get_attribute(_A)
            B = f"{slug}.mp4"
            F = os.system(f"bash mcurl -s 8 -o '{B}' '{E}'")
            if F == 0:
                subprocess.Popen([_I, _J, B])
            break
        except Exception as G:
            print(f"{GREEN}Lagi nungguin tombol download..{NC}")


def telegram_sender():
    A = TelegramClient("iuploadyou", api_id, api_hash)

    @A.on(events.NewMessage(from_users=recipient))
    async def C(event):
        B = event
        print(f"Received message from bot: {B.message.message}")
        if B.message.media:
            await A.send_file(group_id, B.message.media, caption=B.message.message)

    async def B():
        await A.start()
        D = open(_D, "r").read().splitlines()
        for E in D:
            B = E.split(",")
            F = [A for A in B if _C in A]
            C = [A for A in B if _K in A]
            if C:
                time.sleep(5)
                await A.send_message(recipient, f"/start {C[0].split("id=")[-1]}")

    with A:
        A.loop.run_until_complete(B())


def get_top_movie():
    B = "https://tv.lk21official.pics/top-movie-today"
    C = 1134
    A = get_page_source()
    for D in range(C):
        try:
            E = f"{B}/page/{D}"
            A.get(E)
            F = A.page_source
            get_slug(F, "slug_top_movie.txt")
            if "404" in A.title:
                break
        except Exception as G:
            print({"error": G})
            continue


def download():
    H = " || "
    D = "ini_download_link.temp"
    B = open(_D, "r").read().splitlines()
    A = get_page_source()
    C = 0
    L = [A.split(",") for A in B]
    for B in L:
        C += 1
        M = B[0]
        I = [A for A in B if _C in A]
        N = [A for A in B if _K in A]
        E = open(D, "a+")
        F = open(D, "r").read().splitlines()
        print("len link", len(F))
        if len(F) >= 10:
            input(f"saatnyua download {GREEN}(!){NC} ")
            for J in F:
                O = J.split(H)[0]
                K = J.split(H)[1]
                try:
                    assert (
                        os.system(f'bash mcurl.sh -s 8 -o "{K}" "{O}"') == 0
                    ), "download error"
                    subprocess.Popen(["./upload/main", K])
                except AssertionError:
                    print(f"download {RED} error {NC} ko")
            os.remove(D)
        if N:
            print(f"{RED} skipping {NC}", C)
            continue
        print(C)
        if C % 10 == 0:
            A.delete_all_cookies()
            A.refresh()
        if I:
            G = I[0]
            G = G.replace(_C, _F)
            A.get(G)
            A.set_window_size(667, 667)
            time.sleep(2)
            print("refresing..")
            A.refresh()
            while True:
                try:
                    if _G in A.title:
                        break
                    P = WebDriverWait(A, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, _H))
                    )
                    print(f"Download link appear {GREEN}(!){NC}")
                    Q = P.get_attribute(_A)
                    R = f"{M}.mp4"
                    E.write(f"{Q} || {R}")
                    E.write(_B)
                    E.close()
                    break
                except Exception as S:
                    print(f"{GREEN} Lagi nungguin tombol download.. {NC}", S)


if __name__ == "__main__":
    download()
