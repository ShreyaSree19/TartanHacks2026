import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from midifile import MidiFile


def make_minimal_midi():
    # Header: MThd, len=6, format=0, ntrks=1, division=480
    hdr = b'MThd' + (6).to_bytes(4, 'big') + (0).to_bytes(2, 'big') + (1).to_bytes(2, 'big') + (480).to_bytes(2, 'big')
    # Track: delta 0, meta EOT (0xff 0x2f 0x00)
    track_data = b'\x00\xff\x2f\x00'
    trk = b'MTrk' + (len(track_data)).to_bytes(4, 'big') + track_data
    return hdr + trk


def main():
    midi_bytes = make_minimal_midi()
    tmp = os.path.join(os.path.dirname(__file__), 'tmp_smoke.mid')
    with open(tmp, 'wb') as f:
        f.write(midi_bytes)

    mf = MidiFile()
    ok = mf.read(tmp)
    print('read returned:', ok)
    print('tracks:', len(mf._tracks))
    print('tempo map:', mf._tempoMap)

    os.remove(tmp)


if __name__ == '__main__':
    main()
