# TartanHacks2026
Youtube video to musescore


# How to download libraries for MacOS

brew install ffmpeg

python3.10 -m venv spleeter310

source spleeter310/bin/activate

pip install --upgrade pip setuptools wheel

# Install httpx first as a wheel
python3.10 -m pip install --only-binary=:all: "httpx<0.20.0"

pip install -r requirements-macos.txt

pip install spleeter==2.3.2

# How to download libraries for Windows

choco install ffmpeg # or winget install ffmpeg

python3.10 -m venv spleeter310

source spleeter310/bin/activate

pip install --upgrade pip setuptools wheel

pip install -r requirements-windows.txt

pip install --no-deps spleeter==2.3.2
