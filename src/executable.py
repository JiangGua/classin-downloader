import shutil

import bbparser
from config import TEMP_FOLDER

if __name__ == "__main__":
    bbparser.download_all_videos_from_bb_txt()
    shutil.rmtree(TEMP_FOLDER)