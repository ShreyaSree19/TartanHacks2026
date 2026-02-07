import asyncio
from stage_1.audio_separation import audio_separation
# from stage_2.dedalus import dedalus_main
from stage_2.melody_extraction import melody_main
from stage_3.rhythmic_quantization import rhythmic_main


import os
import warnings
import logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"   # hides tensorflow logs
warnings.filterwarnings("ignore")          # hides python warnings
logging.getLogger().setLevel(logging.ERROR) # hides logging warnings/errors


def user_input():
    # song_name = input("Enter the song name and movie or artist "
                    #   "(e.g., 'A Million Dreams from the Greatest Showman'): ")
    url = input("Enter the song's Url from YouTube: ")

    original, vocals, accompaniment = audio_separation(url)

    # dedalus_output = asyncio.run(dedalus_main())

    filename = melody_main(original, vocals)

    # rhythmic_main(filename)

    # print(dedalus_output)

if __name__ == "__main__":
    user_input()

