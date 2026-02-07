"""MIDI Encoding and Parsing Based on MuseScore MIDI tools, by Werner Schweer"""
"""https://github.com/musescore/MuseScore/tree/master/tools/miditools"""

from midifile import MidiFile
from midifile import MidiTrack
from midievent import MidiEventType
from tempomap import TempoMap

def ticks_to_seconds(delta_tick, tempo, division):
    return (delta_tick * (1 / division) * (1 / tempo)) * 60.0

def seconds_to_ticks(seconds, tempo, division):
    return int((seconds / 60.0) * tempo * division)

def round_to_unit(seconds, unit):
    return round(seconds / unit) * unit

def read_midi():
    return

def align_midi_ticks(midi, bpm, sixteenth, triplet_u):
    aligned = MidiFile()
    
    # 1) Copy Header
    aligned.curPos = 0

    aligned._format = midi._format
    aligned._division = midi._division
    # aligned._tempoMap = midi._tempoMap
    aligned._tempoMap[0] = 1000000.0 / bpm
    aligned._tracks.clear()

    for og_track in midi._tracks:
        aligned._tracks.append(MidiTrack(aligned))
        align_click = 0

        # 2) For each OG Track Event
        for click, og_event in og_track.events().items():
            print(click)
            # og_track_tempo = midi._tempoMap[click]
            og_track_tempo = midi._tempoMap[0] # assuming for now the base midi don't change tempo

            # a) Convert delta ticks to seconds using track tempo
            # b) Round the event delta to multiple of 16th note duration
            # c) Round the event delta to multiple of "12th note" duration
            # d) Compare, use more accurate one
            og_seconds = ticks_to_seconds(click, og_track_tempo, midi._division)
            track_16th = round_to_unit(og_seconds, sixteenth)
            track_12th = round_to_unit(og_seconds, triplet_u)
            rounded_seconds = 0
            if (abs(og_seconds - track_16th) <= abs(og_seconds - track_12th)):
                rounded_seconds = track_16th
            else:
                rounded_seconds = track_12th

            # e) Convert delta time to ticks in new tempo
            # f) Create new track event
            new_ticks = seconds_to_ticks(rounded_seconds, bpm, midi._division)
            aligned._tracks[len(aligned._tracks) - 1].events()[align_click] = og_event
            
            align_click += new_ticks
    aligned.status = midi.status
    aligned.sstatus = midi.sstatus
    print(midi._division)
    return aligned

def verify_header(midi):
    hdr = midi._read(4)
    length = midi.read_long()
    if hdr != b'MThd' or length < 6:
        raise ValueError('bad midifile: MThd expected, got {this} of length {L} instead', hdr, length)
    return

def main():
    # 0) input: MIDI, tempo
    base_midi = MidiFile()
    aligned_midi = MidiFile()
    base_midi.read("stage-3/mil_dreams_low_priority.mid")

    song_tempo = float(input("Enter a tempo (beats per minute): "))

    sixteenth_note_duration = 0
    eighth_triplet_unit_duration = 0

    # 1) Pre-Processing:
    if base_midi._division > 0:
        sixteenth_note_duration = song_tempo / (240.0)
        eighth_triplet_unit_duration = song_tempo / (180.0)
        aligned_midi = align_midi_ticks(base_midi, song_tempo, sixteenth_note_duration, eighth_triplet_unit_duration)
    else:
        print("TODO: Implementation for SMPTE timecode division")
        return

    f = open("stage-3/mil_dreams_aligned.mid", 'wb')
    aligned_midi.write_to_file(f)

    # verification
    aligned_midi.read("stage-3/mil_dreams_aligned.mid")

    # verify_header(base_midi)
    # verify_header(aligned_midi)

    return
    # align_midi_ticks(tempo, sixteenth_note_duration, eighth_triplet_unit_duration)

if __name__ == "__main__":
    main()