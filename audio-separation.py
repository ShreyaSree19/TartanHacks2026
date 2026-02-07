import subprocess
from pathlib import Path

# might have to run "chmod +x yt-dlp" in lib/ to make sure it is an executable
# then check "./yt-dlp --version"
def url_to_mp3():
    print("Url:", end = " ")
    url = input()

    out_dir = Path("./mp3-files")
    out_dir.mkdir(exist_ok=True)
    out_template = str(out_dir / "%(title)s.%(ext)s")

    cmd = [
        "lib/yt-dlp",
        "-q",
        "--no-warnings",
        "-x",
        "--audio-format", "mp3",
        "-o", out_template,
        "--print", "filename",
        url
    ]

    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=True)

    filename = result.stdout.strip()
    print("Downloaded:", filename)
    return filename

def mp3_to_wav():
    pass

def main():
    filename = url_to_mp3()
    mp3_to_wav(filename)

if __name__ == "__main__":
    main()
