import requests as rq
from bs4 import BeautifulSoup as bs
import subprocess
import os
import sys
from pathlib import Path
import json

import Nanime, Zoro

CALLERS = {"9anime.org.lv": Nanime, "zorotv": Zoro}
CACHE_PATH = "EpisodesCache"

def SanitizeName(name):
    return "-".join(name.replace(": ", ":").replace(":", " ").split(" "))


def updateDatabse(globalUrl):
    r = rq.get(globalUrl)
    soup = bs(r.content)
    groups = soup.find("ul", attrs={"class": "ulclear az-list"})
    database = {}
    for t in groups.find_all("a"):
        print(t.text)
        r = rq.get(t["href"])
        soup = bs(r.content)
        for show in soup.find_all("div", attrs={"class": "bsx"}):
            link = show.find("a")
            database[link["title"]] = link["href"]
    return database


def main(inputFile):
    inputs = []
    with open(inputFile, "r") as f:
        inputs = f.read().strip().split("\n")
    for mainUrl in inputs:
        links = []
        name = None
        episodesCache = {}
        os.makedirs(os.path.join(Path.home(), CACHE_PATH), exist_ok=True)
        episodesCacheFile = os.path.join(Path.home(), CACHE_PATH, "episodeLinks.json")
        showsCacheFile = os.path.join(Path.home(), CACHE_PATH, "showLinks.json")
        database = updateDatabse("https://9anime.org.lv/anime/")
        with open(showsCacheFile, 'w') as f:
            json.dump(database, f)
        if os.path.isfile(episodesCacheFile):
            with open(episodesCacheFile, 'r') as f:
                episodesCache = json.load(f)
                if mainUrl in episodesCache:
                    links = episodesCache[mainUrl]["links"]
                    name = episodesCache[mainUrl]["name"]
        if len(links) == 0:
            links, name = [v for (k, v) in CALLERS.items() if k in mainUrl][0].getShow(mainUrl)
            links = [l for l in links if not l == None]
            if len(links) > 0:
                episodesCache[mainUrl] = {"links": links, "name": name}
            else:
                print("No download links found.")
                continue
        with open(episodesCacheFile, 'w') as f:
            json.dump(episodesCache, f)
        with open("/tmp/links.txt", "w") as f:
            f.write("\n".join(links))
        name = SanitizeName(name)
        os.makedirs(name, exist_ok=True)
        subprocess.run(("aria2c", "--summary-interval=0", "-c", "--lowest-speed-limit=50K", "-m0", "-i", "/tmp/links.txt", "-d", os.path.join(Path.home(), name)))
    
# updateDatabse()
main(sys.argv[1])
