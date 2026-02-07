"""MIDI Encoding and Parsing Based on MuseScore MIDI tools, by Werner Schweer"""
"""https://github.com/musescore/MuseScore/blob/master/tools/miditools/midifile.cpp"""

from collection import defaultdict

class MidiTrack:
    mf = 0
    events = defaultdict(list)

    def __init__(self, mf_):
        mf = mf_
        events = defaultdict(list)


class MidiFile:
    tempo_map = 0
    fileIO = 0
    tracks = list()
    division = 0
    format = 0      # midi file format (0-2)

    status = 0      # running status
    sstatus = 0     # running status (not reset after meta or sysex events)
    click = 0       # current tick position in file
    curPos = 0      # current file byte position

    def _read(self, path):
        return 0
    
    def _read(self, fQIO):
        return 0
    
    def _getvl():
        return 0
    
    def _readShort():
        return 0

