import argparse
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
GLOBAL_URL = "https://9anime.org.lv/anime/"

def SanitizeName(name):
    return "-".join(name.replace(": ", ":").replace(":", " ").split(" "))


def updateDatabse():
    r = rq.get(GLOBAL_URL)
    soup = bs(r.content)
    groups = soup.find("ul", attrs={"class": "ulclear az-list"})
    database = {}
    for t in groups.find_all("a"):
        while True:
            r = rq.get(t["href"])
            soup = bs(r.content)
            for show in soup.find_all("div", attrs={"class": "bsx"}):
                link = show.find("a")
                database[link["title"]] = link["href"]
            curr_page = soup.find("span", attrs={"class": "page-numbers current"})
            if curr_page is None:
                break
            next_page = soup.find("a", string=str(int(curr_page.text) + 1))
            if next_page is None:
                break
            else:
                t = next_page
    os.makedirs(os.path.join(Path.home(), CACHE_PATH), exist_ok=True)
    showsCacheFile = os.path.join(Path.home(), CACHE_PATH, "showLinks.json")
    with open(showsCacheFile, 'w') as f:
        json.dump(database, f)
    return database


def search(phrase):
    showsCacheFile = os.path.join(Path.home(), CACHE_PATH, "showLinks.json")
    if os.path.isfile(showsCacheFile):
        with open(showsCacheFile, 'r') as f:
            database = json.load(f)
    else:
        updateDatabse()
    matches = []
    for (title, link) in database.items():
        if phrase.lower() in title.lower():
            matches.append((title, link))
    for (i, match) in enumerate(matches):
        print(i, ": ", match[0])
    response = input("Enter number to select match, or enter anything else to exit. ")
    try:
        getShow(matches[int(response)][1])
    except:
        return


def getShow(mainUrl):
    links = []
    name = None
    episodesCache = {}
    episodesCacheFile = os.path.join(Path.home(), CACHE_PATH, "episodeLinks.json")
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
            return
    with open(episodesCacheFile, 'w') as f:
        json.dump(episodesCache, f)
    with open("/tmp/links.txt", "w") as f:
        f.write("\n".join(links))
    name = SanitizeName(name)
    os.makedirs(os.path.join(Path.home(), name), exist_ok=True)
    subprocess.run((
        "aria2c",
        "--summary-interval=0",
        "-c",
        "--lowest-speed-limit=50K",
        "-m0",
        "-i",
        "/tmp/links.txt",
        "-d",
        os.path.join(Path.home(), name)
        ))

def fromFile(inputFile):
    inputs = []
    with open(inputFile, "r") as f:
        inputs = f.read().strip().split("\n")
    for mainUrl in inputs:
        getShow(mainUrl)
    

parser = argparse.ArgumentParser(prog='ProgramName', description='What the program does', epilog='Text at the bottom of help')
parser.add_argument('-s')
parser.add_argument('-i')
parser.add_argument('-u', action='store_true')
args = parser.parse_args()
if args.u:
    updateDatabse()
if args.s is not None:
    search(args.s)
if args.i is not None:
    fromFile(args.i)
