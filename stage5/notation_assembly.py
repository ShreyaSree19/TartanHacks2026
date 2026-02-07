import json
import pretty_midi
from music21 import stream, note, chord, meter, tempo, key, metadata, expressions


def load_midi_notes(midi_path):
    """Load notes from a MIDI file, sorted by start time."""
    pm = pretty_midi.PrettyMIDI(midi_path)
    notes = []
    for inst in pm.instruments:
        for n in inst.notes:
            notes.append({
                "pitch": n.pitch,
                "start": n.start,
                "end": n.end,
                "velocity": n.velocity,
            })
    notes.sort(key=lambda n: n["start"])
    return notes, pm


def load_chords(chords_path):
    """Load chord timeline from JSON."""
    with open(chords_path, "r") as f:
        return json.load(f)


def load_aligned_lyrics(lyrics_path):
    """Load aligned lyrics from Stage 4 JSON."""
    with open(lyrics_path, "r") as f:
        return json.load(f)


def parse_chord_symbol(chord_str):
    """Convert chord string like 'C Maj' or 'A min' to music21 chord symbol."""
    parts = chord_str.split()
    root = parts[0]
    quality = parts[1] if len(parts) > 1 else "Maj"

    # Normalize sharp notation for music21
    root = root.replace("#", "#")

    if quality.lower() in ("min", "minor"):
        return f"{root}m"
    else:
        return root


def seconds_to_quarter_length(seconds, bpm):
    """Convert a duration in seconds to quarter-note lengths given a BPM."""
    beats_per_second = bpm / 60.0
    return seconds * beats_per_second


def build_score(midi_path, chords_path, lyrics_path=None, bpm=None):
    """
    Assemble melody, chords, and lyrics into a music21 Score.

    Args:
        midi_path: path to melody.mid (from Stage 2/3)
        chords_path: path to chords.json (from Stage 2)
        lyrics_path: path to aligned_lyrics.json (from Stage 4), optional
        bpm: override BPM; if None, estimate from MIDI
    """
    print("--- Stage 5: Assembling notation ---")

    # Load data
    notes, pm = load_midi_notes(midi_path)
    chords_data = load_chords(chords_path)
    lyrics_data = load_aligned_lyrics(lyrics_path) if lyrics_path else []

    # Estimate BPM from MIDI if not provided
    if bpm is None:
        tempo_changes = pm.get_tempo_changes()
        if len(tempo_changes[1]) > 0:
            bpm = tempo_changes[1][0]
        else:
            bpm = 120.0
    print(f"Using BPM: {bpm}")

    # Build lyrics lookup: note_start -> word
    lyrics_by_time = {}
    for entry in lyrics_data:
        lyrics_by_time[round(entry["note_start"], 3)] = entry["word"]

    # Create score
    s = stream.Score()
    s.metadata = metadata.Metadata()
    s.metadata.title = "Lead Sheet"

    # Add tempo marking
    mm = tempo.MetronomeMark(number=bpm)

    # Melody part
    melody_part = stream.Part()
    melody_part.partName = "Melody"
    melody_part.insert(0, mm)
    melody_part.insert(0, meter.TimeSignature("4/4"))

    # Add melody notes
    for n_data in notes:
        pitch_midi = n_data["pitch"]
        duration_sec = n_data["end"] - n_data["start"]
        offset_sec = n_data["start"]

        ql = seconds_to_quarter_length(duration_sec, bpm)
        offset_ql = seconds_to_quarter_length(offset_sec, bpm)

        # Clamp minimum duration
        if ql < 0.125:
            ql = 0.125

        m21_note = note.Note(pitch_midi)
        m21_note.quarterLength = ql

        # Attach lyric if available
        note_key = round(n_data["start"], 3)
        if note_key in lyrics_by_time:
            m21_note.lyric = lyrics_by_time[note_key]

        melody_part.insert(offset_ql, m21_note)

    # Add chord symbols above the melody
    for c_data in chords_data:
        c_time = c_data["time"]
        c_name = c_data["chord"]
        offset_ql = seconds_to_quarter_length(c_time, bpm)

        symbol_str = parse_chord_symbol(c_name)
        cs = chord.ChordSymbol(symbol_str)
        melody_part.insert(offset_ql, cs)

    s.insert(0, melody_part)

    print(f"Score built: {len(notes)} notes, {len(chords_data)} chord symbols, {len(lyrics_data)} lyrics")
    return s


def run_stage5(midi_path, chords_path, lyrics_path=None, output_path="lead_sheet.musicxml", bpm=None):
    """Full Stage 5 pipeline: build score and export MusicXML."""
    s = build_score(midi_path, chords_path, lyrics_path=lyrics_path, bpm=bpm)

    s.write("musicxml", fp=output_path)
    print(f"Success: Saved {output_path}")
    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python notation_assembly.py <melody.mid> <chords.json> [aligned_lyrics.json] [output.musicxml] [bpm]")
        print("  melody.mid          - MIDI from Stage 2/3")
        print("  chords.json         - chord timeline from Stage 2")
        print("  aligned_lyrics.json - (optional) lyrics from Stage 4")
        print("  output.musicxml     - (optional) output path, default: lead_sheet.musicxml")
        print("  bpm                 - (optional) override BPM")
        sys.exit(1)

    midi = sys.argv[1]
    chords = sys.argv[2]
    lyrics = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].endswith(".musicxml") else None
    out = "lead_sheet.musicxml"
    override_bpm = None

    for arg in sys.argv[3:]:
        if arg.endswith(".musicxml"):
            out = arg
        elif arg.replace(".", "", 1).isdigit():
            override_bpm = float(arg)

    run_stage5(midi, chords, lyrics_path=lyrics, output_path=out, bpm=override_bpm)
