import subprocess

print("Url:", end = " ")
url = input()

cmd = [
    "lib/yt-dlp",
    "-q",
    "--no-warnings",
    "-x",
    "--audio-format", "mp3",
    "-o", "./downloads/%(title)s.%(ext)s",
    url
]

subprocess.run(cmd, check=True)
