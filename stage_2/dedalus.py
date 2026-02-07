from dedalus_labs import AsyncDedalus, DedalusRunner

def get_input(song):
    return f'''What is the beats per minute (BPM) and time signature of the song {song}?
        In the format:
BPM: [number]
Time Signature: [number]/[number]
'''

song_name = ""

async def dedalus_main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    # 3. Reference the global variable here
    response = await runner.run(
        input=get_input(song_name), 
        model="anthropic/claude-opus-4-6",
    )

    print(response.final_output)
    
    return response.final_output

# if __name__ == "__main__":
#     # song_name = input("Enter the song name and movie or artist (e.g., 'A Million Dreams from the Greatest Showman'): ")
#     asyncio.run(main())

# chat_completion = client.chat.completions.create(
#     model="openai/gpt-5-nano",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a professional coder who thinks and comes up with simple and correct solutions.",
#         },
#         {
#             "role": "user",
#             "content": '''
# We need toimplement stage 3 of our project given stag 2, which now has one note per timestep but we need to detect the correct time signature and bpm and assign durations to the notes (only quarter, eigth, or sixteethn)
#             Project: Youtube Audio to MuseScore Converter (Etracts Melody and Chords)
# Stage 1: Audio Acquisition & Stem Separation
# What it does: Downloads the youtube audio and isolates the voice (for melody) from the instruments (for chords).
# Tools/APIs: yt-dlp (Library) for downloading; Spleeter (Open Source) or LALAL.AI API for separation.
# https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation
# https://github.com/ytdl-org/youtube-dl?tab=readme-ov-file#output-template-examples -> don’t have sudo, so not using
# https://www.lalal.ai/api/v1/docs/
# https://github.com/OmniSaleGmbH/lalalai/tree/master/api-v1/python
# https://github.com/deezer/spleeter
# Output: vocals.wav and instrumental.wav.
# Stage 2: Feature Extraction (Melody & Chords)
# What it does: Converts the isolated audio files into raw musical data.
# Melody: Use Spotify’s Basic Pitch (Open Source/Python). It extracts MIDI notes from the vocal stem.
# Chords: Use Chordify API or Librosa (Python library). Librosa analyzes the "chroma" (harmonic content) of the instrumental stem to guess chords.
# Output: Raw MIDI file (melody.mid) and a text/JSON list of chords with timestamps.
# https://www.freeconvert.com/download - Convert Mid to Wav/Mp3
# Overview of MIDI File
# MIDI File Decoder
# MIDI File Decoder 2
# Keyboard Visualizer
# Stage 3: Rhythm Processing (Quantization & Beat Tracking)**
# *Based on Market Research this is a very important step to be better than competitors!
# What it does: This is the critical "cleaning" step. It calculates the BPM and "snaps" the raw MIDI events to a musical grid (e.g., 16th notes).
# API/Tool: Librosa (librosa.beat.beat_track).
# Logic: 1. Detect global BPM. 2. Map second-based timestamps to "ticks" or "quarter lengths." 3. Use Music21’s .quantize() function to ensure a note starting at 1.002s is treated as starting exactly on Beat 2.
# Output: Cleaned MIDI data aligned to a steady tempo
# ''',
#         },
#     ],
# )
# print(chat_completion.id)