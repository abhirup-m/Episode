import requests as rq
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor

def getShow(parentUrl):
    soup = bs(rq.get(parentUrl).content, "html.parser")
    episodes = soup.find_all("a", attrs={"class": "item ep-item"})
    name = soup.find("h1", attrs={"class": "entry-title"}).text
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(getEpisode, ep["href"])
            for ep in episodes
        ]
    return [f.result() for f in futures], name
 
