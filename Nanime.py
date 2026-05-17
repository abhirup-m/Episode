import requests as rq
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import json

def getEpisode(episode):
    soup = bs(rq.get(episode).content, "html.parser")
    nextPage = soup.find_all("script")
    malId = None
    ajaxUrl = None
    ep = None
    for t in nextPage:
        if "var malId = " in t.get_text():
            lines = t.get_text().split("\n")
            for l in lines:
                if "var malId = " in l:
                    malId = l.strip().split("'")[1]
                if "var ajaxUrl = " in l:
                    ajaxUrl = l.strip().split("'")[1]
                if "var ep = " in l:
                    ep = l.strip().split("'")[1]
                if malId is not None and ajaxUrl is not None and ep is not None:
                    break
            break

    payload = {"action": "fetch_download_links", "mal_id": malId, "ep": ep}
    nextPage = rq.post(ajaxUrl, data=payload)
    if "data" in json.loads(nextPage.content):
        if "result" in json.loads(nextPage.content)["data"]:
            soup = bs(json.loads(nextPage.content)["data"]["result"], "html.parser")
            for a in soup.find_all("a"):
                if "1080" in a.text:
                    return a["href"]
        else:
            print(episode + ": Download links not available.")
    return


def getShow(parentUrl):
    soup = bs(rq.get(parentUrl).content, "html.parser")
    name = soup.find("h1", attrs={"class": "entry-title"}).text
    ep = 0
    links = []
    while True:
        epItem = soup.find("li", attrs={"data-index": ep})
        if epItem is None:
            break
        else:
            ep += 1
            links.append(epItem.find("a")["href"])
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(getEpisode, link)
            for link in links
        ]
    return [f.result() for f in futures], name
