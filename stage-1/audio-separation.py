from pathlib import Path
import yt_dlp


# need to have installed yt-dlp (found in requirements.txt)
def url_to_mp3():
    print("Url:", end = " ")
    url = input()

    out_dir = Path("./mp3-files")
    out_dir.mkdir(exist_ok=True)
    out_template = str(out_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'outtmpl': out_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = Path(filename).with_suffix(".mp3")

    print("Downloaded:", filename)
    return filename

def mp3_to_wav():
    pass

def main():
    filename = url_to_mp3()
    mp3_to_wav()

if __name__ == "__main__":
    main()
