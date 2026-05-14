import subprocess
import os
import sys
from pathlib import Path
import json

import Nanime

def main(inputFile):
    inputs = []
    with open(inputFile, "r") as f:
        inputs = f.read().strip().split("\n")
    for mainUrl in inputs:
        links = []
        name = None
        cache = {}
        cacheFile = os.path.join(Path.home(), "mineAnimeCache.json")
        if os.path.isfile(cacheFile):
            with open(cacheFile, 'r') as f:
                cache = json.load(f)
                if mainUrl in cache:
                    links = cache[mainUrl]["links"]
                    name = cache[mainUrl]["name"]
                else:
                    links, name = Nanime.getShow(mainUrl)
                    links = [l for l in links if not l == None]
                    if len(links) > 0:
                        cache[mainUrl] = {"links": links, "name": name}
                    else:
                        continue
        else:
            links, name = Nanime.getShow(mainUrl)
            links = [l for l in links if not l == None]
            if len(links) > 0:
                cache[mainUrl] = {"links": links, "name": name}
            else:
                continue
        with open(cacheFile, 'w') as f:
            json.dump(cache, f)
        with open("/tmp/links.txt", "w") as f:
            f.write("\n".join(links))
        os.makedirs(name, exist_ok=True)
        subprocess.Popen(("aria2c", "--summary-interval=0", "-c", "--lowest-speed-limit=50K", "-m0", "-i", "/tmp/links.txt", "-d", os.path.join(Path.home(), name))).wait()
    

main(sys.argv[1])
