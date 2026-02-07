import subprocess


# might have to run "chmod +x yt-dlp" in lib/ to make sure it is an executable
# then check "./yt-dlp --version"
def url_to_mp3():
    print("Url:", end = " ")
    url = input()

    cmd = [
        "lib/yt-dlp",
        "-q",
        "--no-warnings",
        "-x",
        "--audio-format", "mp3",
        "-o", "./mp3-files/%(title)s.%(ext)s",
        url
    ]

    subprocess.run(cmd, check=True)

def mp3_to_wav():
    pass

def main():
    url_to_mp3()

if __name__ == "__main__":
    main()
