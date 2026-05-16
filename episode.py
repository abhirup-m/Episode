import argparse
from urllib import parse
from tqdm import tqdm
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
GLOBAL_URLs = ["https://zorotv.com.ro/anime/list-mode/", "https://9anime.org.lv/anime/list-mode/"]

def SanitizeName(name):
    return "-".join(name.replace(": ", ":").replace(":", " ").split(" "))



def updateDatabse():
    database = {}
    for url in GLOBAL_URLs:
        r = rq.get(url)
        soup = bs(r.content, "html.parser")
        for link in tqdm(soup.find_all("a", attrs={"class": "series tip"})):
            if link.text in database:
                database[link.text].append(link["href"])
            else:
                database[link.text] = [link["href"]]
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
    catches = []
    while True:
        matches = []
        for (title, link) in database.items():
            if phrase.lower() in title.lower():
                matches.append((title, link))
        for (i, match) in enumerate(matches):
            print(i, ": ", match[0])
        response = input("Enter number to select match. Enter anything else to exit. --> ")
        catches.append(matches[int(response)][1])
        response = input("You selected \"{}\".\nEnter d to start downloading. Enter s to search again and add to bucket. Enter q to quit. --> ".format(matches[int(response)][0]))
        if response == "d":
            break
        if response == "s":
            phrase = input("Enter phrase to search for: ")
        if response == "q":
            return
    for link in catches:
        getShow(link)


def searchTorrent(phrase):
    r = rq.get("https://nyaa.si/?f=1&c=1_3&q=" + parse.quote(phrase) + "&s=comments&o=desc")
    soup = bs(r.content, "html.parser")
    while True:
        links = []
        names = []
        count = 1
        for t in soup.find_all("tr", attrs={"class": "success"}):
            size = None
            for a in t.find_all("a"):
                if a["title"].strip() == a.text.strip():
                    names.append(a["title"].strip())
                    break
            for a in t.find_all("a"):
                if a["href"].startswith("magnet:?"):
                    links.append(a["href"])
                    size = a.find_next("td").text
                    break
            seeds = t.find_all("td")[-3].text
            leeches = t.find_all("td")[-2].text
            print(str(count) + ".\t S: " + seeds + ", L: " + leeches + ", \t" + size + ",\t " + names[-1])
            count += 1
        for t in soup.find_all("tr", attrs={"class": "default"}):
            size = None
            for a in t.find_all("a"):
                if a["title"].strip() == a.text.strip():
                    names.append(a["title"].strip())
                    break
            for a in t.find_all("a"):
                if a["href"].startswith("magnet:?"):
                    links.append(a["href"])
                    size = a.find_next("td").text
                    break
            seeds = t.find_all("td")[-3].text
            leeches = t.find_all("td")[-2].text
            print(str(count) + ".\t S: " + seeds + ", L: " + leeches + ", \t" + size + ",\t " + names[-1])
            count += 1
        choice = input("Enter number to download. Enter 0 to search again. Enter anything else to quit. ")
        try:
            choice = int(choice)
            if choice == 0:
                phrase = input("Enter phrase to search for: ")
                continue
            elif 0 < choice <= len(links):
                return links[choice - 1], names[choice - 1]
            else:
                return
        except:
            return


def getTorrent(phrase):
    link, name = searchTorrent(phrase)
    cmd = (
            "aria2c",
            "--summary-interval=0",
            "-c",
            "--lowest-speed-limit=50K",
            # "-q",
            "--console-log-level=notice",
            "--log-level=notice",
            "-m0",
            "-x16",
            "-s16",
            "-k1M",
            "--log=/tmp/{}-log".format(name),
            "--dir={}".format(os.path.join(Path.home(), name)),
            link
            )
    subprocess.run(cmd)


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
    cmd = (
            "aria2c",
            "--summary-interval=0",
            "-c",
            "--lowest-speed-limit=50K",
            # "-q",
            "--console-log-level=notice",
            "--log-level=notice",
            "-m0",
            "-x16",
            "-s16",
            "-k1M",
            "--log=/tmp/{}-log".format(name),
            "--input-file=/tmp/links.txt",
            "--dir={}".format(os.path.join(Path.home(), name)),
            )
    tries = 1
    while tries < 10:
        proc = subprocess.run(cmd)

        if proc.returncode != 0:
            print("Errors happened in download. Trying again.")
            tries += 1
            continue
        else:
            break


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
parser.add_argument('-t')
args = parser.parse_args()
if args.t:
    getTorrent(args.t)
if args.u:
    updateDatabse()
if args.s is not None:
    search(args.s)
if args.i is not None:
    fromFile(args.i)
