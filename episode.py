import subprocess
import os
import sys

import Nanime

def main(mainUrl):
    link = Nanime.downloader(mainUrl)
    subprocess.run(("aria2c", "--summary-interval=0", "-c", "--lowest-speed-limit=50K", "-s", "10", "-m0", link))
    

main(sys.argv[1])
