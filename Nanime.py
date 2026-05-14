import requests as rq
from bs4 import BeautifulSoup as bs
import json

def downloader(episode):
    soup = bs(rq.get(episode).content, "html.parser")
    nextPage = soup.find_all("script")
    malId = None
    ajaxUrl = None
    ep = None
    proc = None
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
