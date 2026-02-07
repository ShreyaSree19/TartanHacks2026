import asyncio
from stage_1.audio_separation import audio_separation
# from stage_2.dedalus import dedalus_main
from stage_2.melody_extraction import melody_main


def user_input():
    # song_name = input("Enter the song name and movie or artist "
                    #   "(e.g., 'A Million Dreams from the Greatest Showman'): ")
    url = input("Enter the song's Url from YouTube: ")

    original, vocals, accompaniment = audio_separation(url)

    # dedalus_output = asyncio.run(dedalus_main())

    melody_main(original, vocals)

    # print(dedalus_output)

if __name__ == "__main__":
    user_input()

