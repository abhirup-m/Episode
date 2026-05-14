import requests as rq
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import json

def getEpisode(episode):
    soup = bs(rq.get(episode).content, "html.parser")
    downloadPage = soup.find("a", attrs={"aria-label": "Download"})["href"]
    soup = bs(rq.get(downloadPage).content, "html.parser")
    return soup.find("a", attrs={"id": "downloadBtn"})["href"]


def getShow(parentUrl):
