from pathlib import Path
import yt_dlp
import subprocess

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

def mp3_to_wav(mp3_file):
    mp3_file = Path(mp3_file)

    out_dir = Path("./wav-files")
    out_dir.mkdir(exist_ok=True)

    wav_file = out_dir / (mp3_file.stem + ".wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(mp3_file),
        str(wav_file)
    ]

    subprocess.run(cmd, check=True)
    print("Converted to WAV:", wav_file)

    return wav_file


# spleeter requires python 3.10.xx or less
def separate_with_spleeter(wav_file):
    wav_file = Path(wav_file)

    out_dir = Path("./separated")
    out_dir.mkdir(exist_ok=True)

    cmd = [
        "spleeter",
        "separate",
        "-p", "spleeter:2stems",
        "-o", str(out_dir),
        str(wav_file)
    ]

    subprocess.run(cmd, check=True)

    song_folder = out_dir / wav_file.stem
    vocals = song_folder / "vocals.wav"
    accompaniment = song_folder / "accompaniment.wav"

    print("Vocals:", vocals)
    print("Accompaniment:", accompaniment)

    return vocals, accompaniment


def main():
    mp3_file = url_to_mp3()
    wav_file = mp3_to_wav(mp3_file)
    vocals, accompaniment = separate_with_spleeter(wav_file)

    print("Done!")
    print("Vocals saved at:", vocals)
    print("Accompaniment saved at:", accompaniment)

if __name__ == "__main__":
    main()
