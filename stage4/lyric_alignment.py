import whisper
import pretty_midi
import json
import bisect


def transcribe_lyrics(audio_path, model_size="base"):
    """Transcribe lyrics from vocal audio using OpenAI Whisper with word timestamps."""
    print(f"--- Stage 4: Transcribing lyrics from {audio_path} ---")
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, word_timestamps=True)

    words = []
    for segment in result["segments"]:
        for word_info in segment["words"]:
            words.append({
                "word": word_info["word"].strip(),
                "start": round(word_info["start"], 3),
                "end": round(word_info["end"], 3),
            })

    print(f"Transcribed {len(words)} words.")
    return words


def align_lyrics_to_midi(words, midi_path):
    """Match each transcribed word to the nearest MIDI note by timestamp."""
    print(f"Aligning {len(words)} words to notes in {midi_path}...")
    pm = pretty_midi.PrettyMIDI(midi_path)

    # Collect all notes across instruments, sorted by start time
    all_notes = []
    for inst in pm.instruments:
        for note in inst.notes:
            all_notes.append(note)
    all_notes.sort(key=lambda n: n.start)

    if not all_notes:
        print("WARNING: No notes found in MIDI file.")
        return []

    note_starts = [n.start for n in all_notes]

    aligned = []
    for w in words:
        # Find the note whose start time is closest to the word's start time
        idx = bisect.bisect_left(note_starts, w["start"])
        # Check neighbors to find the actual closest
        best_idx = idx
        if idx >= len(all_notes):
            best_idx = len(all_notes) - 1
        elif idx > 0:
            if abs(note_starts[idx - 1] - w["start"]) < abs(note_starts[idx] - w["start"]):
                best_idx = idx - 1

        matched_note = all_notes[best_idx]
        aligned.append({
            "word": w["word"],
            "word_start": w["start"],
            "word_end": w["end"],
            "note_start": round(matched_note.start, 3),
            "note_pitch": matched_note.pitch,
        })

    print(f"Aligned {len(aligned)} words to MIDI notes.")
    return aligned


def run_stage4(vocal_audio_path, midi_path, output_path="aligned_lyrics.json", model_size="base"):
    """Full Stage 4 pipeline: transcribe + align."""
    words = transcribe_lyrics(vocal_audio_path, model_size=model_size)
    aligned = align_lyrics_to_midi(words, midi_path)

    with open(output_path, "w") as f:
        json.dump(aligned, f, indent=4)
    print(f"Success: Saved {output_path}")
    return aligned


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python lyric_alignment.py <vocal_audio> <melody.mid> [output.json] [whisper_model]")
        print("  vocal_audio  - path to vocals wav/mp3")
        print("  melody.mid   - path to MIDI from Stage 2/3")
        print("  output.json  - (optional) output path, default: aligned_lyrics.json")
        print("  whisper_model - (optional) tiny|base|small|medium|large, default: base")
        sys.exit(1)

    vocal = sys.argv[1]
    midi = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else "aligned_lyrics.json"
    model = sys.argv[4] if len(sys.argv) > 4 else "base"

    run_stage4(vocal, midi, output_path=out, model_size=model)
