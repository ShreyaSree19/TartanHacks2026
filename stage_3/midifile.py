"""
A Python translation of the MuseScore midifile.cpp file by Werner Schweer,
converted by VSCode Chat

This is a functional, fairly direct port using built-in file I/O.
It implements reading and writing of basic MIDI files (format 0/1),
including variable-length values, running status, and tempo meta events.
"""
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, BinaryIO
from midievent import MidiEventType
from midievent import ControllerConstants
from midievent import MetaEventConstants
from midievent import MidiEvent
from tempomap import TempoMap


# class MidiEventType(IntEnum):
#     NOTEOFF = 0x80
#     NOTEON = 0x90
#     POLYAFTER = 0xa0
#     CONTROLLER = 0xb0
#     PROGRAM = 0xc0
#     AFTERTOUCH = 0xd0
#     PITCHBEND = 0xe0
#     SYSEX = 0xf0
#     META = 0xff


# META_TEMPO = 0x51
# META_EOT = 0x2f


# @dataclass
# class MidiEvent:
#     type: MidiEventType = None
#     channel: int = 0
#     a: int = 0
#     b: int = 0

#     def set(self, t: MidiEventType, channel: int, a: int, b: int):
#         self.type = t
#         self.channel = channel
#         self.a = a
#         self.b = b


class MidiTrack:
    def __init__(self, mf: 'MidiFile'):
        self.mf = mf
        self._events: Dict[int, MidiEvent] = {}

    def events(self):
        return self._events


class MidiFile:
    def __init__(self):
        self.fp: BinaryIO = None
        self._format = 1
        self._division = 480 # ticks per beat
        self._tracks: List[MidiTrack] = []
        self.curPos = 0
        self.status = -1
        self.sstatus = -1
        self.click = 0
        self._tempoMap: Dict[int, float] = {} # beats per second

    # ------------------------- low-level reads -------------------------
    def _read(self, n: int) -> bytes:
        data = self.fp.read(n)
        # print(bytes(data), '\n')
        if data is None or len(data) != n:
            raise EOFError(f"bad midifile: unexpected EOF (got to position 0x{self.curPos:02x}, tried to read n bytes: {n} with data left: {len(data)})")
            # raise EOFError("bad midifile: unexpected EOF")
        self.curPos += n
        return data

    def _read_byte(self) -> int:
        return self._read(1)[0]

    def read_short(self) -> int:
        b = self._read(2)
        return int.from_bytes(b, byteorder='big', signed=False)

    def read_long(self) -> int:
        b = self._read(4)
        return int.from_bytes(b, byteorder='big', signed=False)

    def skip(self, n: int):
        if n <= 0:
            return
        _ = self._read(n)

    def getvl(self) -> int:
        l = 0
        for i in range(16):
            c = self._read_byte()
            l = (l << 7) | (c & 0x7f)
            if not (c & 0x80):
                return l
            # l <<= 7
        return -1

    # ------------------------- high-level read -------------------------
    def read(self, path: str) -> bool:
        with open(path, 'rb') as f:
            return self.read_from_file(f)

    def read_from_file(self, f: BinaryIO) -> bool:
        self.fp = f
        self._tracks.clear()
        self.curPos = 0

        hdr = self._read(4)
        length = self.read_long()
        if hdr != b'MThd' or length < 6:
            raise ValueError('bad midifile: MThd expected')

        self._format = self.read_short()
        ntracks = self.read_short()
        self._division = self.read_short()

        if self._division < 0:
            # SMPTE style division handling (port of original logic)
            self._division = (- (self._division // 256)) * (self._division & 0xff)
        if length > 6:
            self.skip(length - 6)

        if self._format == 0:
            self.read_track()
        elif self._format == 1:
            for i in range(ntracks):
                print(f"ReadING track {i+1} of {ntracks} at 0x{self.curPos:x}...")
                self.read_track()
                print(f"Read track {i+1} of {ntracks} ending at 0x{self.curPos:x}!\n")
        else:
            raise NotImplementedError(f'midi file format {self._format} not implemented')
        return True

    def read_track(self) -> bool:
        hdr = self._read(4)
        if hdr != b'MTrk':
            raise ValueError('bad midifile: MTrk expected')
        length = self.read_long()
        endPos = self.curPos + length
        self.status = -1
        self.sstatus = -1
        self.click = 0
        track = MidiTrack(self)
        self._tracks.append(track)

        while True:
            event = MidiEvent()
            rv = self.read_event(event)
            # print("Read an event!")
            if rv == 0:
                track.events()[self.click] = event
            elif rv == 2:
                break

        if self.curPos != endPos:
            # attempt to skip remaining bytes if any
            if self.curPos < endPos:
                self.skip(endPos - self.curPos)
        return True

    def read_event(self, event: MidiEvent) -> int:
        nclick = self.getvl()
        if nclick == -1:
            raise ValueError('readEvent: error 1(getvl)')
        self.click += nclick

        # read status or system bytes, skipping unknown F1..FE except F7
        while True:
            me = self._read_byte()
            if 0xf1 <= me <= 0xfe and me != 0xf7:
                # skip/ignore
                continue
            break

        # sysex
        if me == 0xf0 or me == 0xf7:
            self.status = -1
            length = self.getvl()
            if length == -1:
                raise ValueError('readEvent: error 3')
            data = self._read(length)
            if data and data[-1] != 0xf7:
                # could be more to come; ignore
                pass
            return 1

        # meta
        if me == 0xff:
            self.status = -1
            mtype = self._read_byte()
            dataLen = self.getvl()
            if dataLen == -1:
                raise ValueError('readEvent: error 6')
            data = b''
            if dataLen:
                data = self._read(dataLen)
            if mtype == MetaEventConstants.META_TEMPO and dataLen >= 3:
                tempo = (data[0] << 16) + (data[1] << 8) + data[2] # stored as usec per beat
                t = 1000000.0 / float(tempo) # 1,000,000 usec per second / tempo in usec per beat = beats per second
                self._tempoMap[self.click] = t
            if mtype == MetaEventConstants.META_EOT:
                return 2
            return 1

        # normal midi events: running status support
        if me & 0x80:
            self.status = me
            self.sstatus = self.status
            a = self._read_byte()
        else:
            if self.status == -1:
                if self.sstatus == -1:
                    return 0
                self.status = self.sstatus
            a = me

        channel = self.status & 0x0f
        b = 0
        t = MidiEventType(self.status & 0xf0)
        if t in (MidiEventType.NOTEOFF, MidiEventType.NOTEON, MidiEventType.POLYAFTER,
                 MidiEventType.CONTROLLER, MidiEventType.PITCHBEND):
            b = self._read_byte()

        if t in (MidiEventType.NOTEOFF, MidiEventType.NOTEON, MidiEventType.CONTROLLER,
                 MidiEventType.PITCHBEND, MidiEventType.POLYAFTER):
            event.set(t, channel, a, b)
        elif t in (MidiEventType.PROGRAM, MidiEventType.AFTERTOUCH):
            event.set(t, channel, a, 0)
        else:
            raise ValueError(f'BAD STATUS: 0x{me:02x} at 0x{self.curPos:x}', t)

        if (a & 0x80) or (b & 0x80):
            if b & 0x80:
                # try to fix: interpret as status
                self.status = b
                self.sstatus = self.status
                return 0
            raise ValueError('readEvent: error 16')
        return 0

    # ------------------------- write support -------------------------
    def write(self, path: str) -> bool:
        with open(path, 'wb') as f:
            return self.write_to_file(f)

    def write_to_file(self, f: BinaryIO) -> bool:
        self.fp = f
        self._write(b'MThd')
        self.write_long(6)
        self.write_short(self._format)
        self.write_short(len(self._tracks))
        self.write_short(self._division)
        for t in self._tracks:
            self.write_track(t)
        return True

    def _write(self, data: bytes):
        written = self.fp.write(data)
        if written != len(data):
            raise IOError('write midifile failed')

    def put(self, val: int):
        self._write(bytes([val & 0xff]))

    def write_short(self, i: int):
        self._write(i.to_bytes(2, byteorder='big'))

    def write_long(self, i: int):
        self._write(i.to_bytes(4, byteorder='big'))

    def putvl(self, val: int):
        # buf = val & 0x7f
        # v = (val + (1 << 32)) & 0xffffffff # ensure treated as unsigned
        # while (v >> 7) > 0:
        #     v >>= 7
        #     buf <<= 8
        #     buf |= 0x80
        #     buf += (v & 0x7f)
        # while True:
        #     self.put(buf & 0xff)
        #     if buf & 0x80:
        #         buf >>= 8
        #     else:
        #         break
        # Standard VLQ encoder (most-significant 7-bit groups first,
        # continuation bit set on all but last byte)
        if val == 0:
            self.put(0)
            return
        parts = []
        v = int(val)
        while v > 0:
            parts.append(v & 0x7f)
            v >>= 7
        for i in range(len(parts) - 1, -1, -1):
            byte = parts[i]
            if i != 0:
                byte |= 0x80
            self.put(byte)

    def write_status(self, st: MidiEventType, c: int):
        nstat = (int(st) & 0xff) | (c & 0xf)
        if ((nstat & 0xf0) != 0xf0) and (nstat != self.status):
            self.status = nstat
            self.put(nstat)

    def write_event(self, event: MidiEvent):
        if event.type in (MidiEventType.NOTEON, MidiEventType.NOTEOFF,
                          MidiEventType.CONTROLLER, MidiEventType.PITCHBEND):
            self.write_status(event.type, event.channel)
            self.put(event.a & 0x7f)
            self.put(event.b & 0x7f)
        elif event.type in (MidiEventType.PROGRAM, MidiEventType.AFTERTOUCH):
            self.write_status(event.type, event.channel)
            self.put(event.a & 0x7f)
        elif getattr(event, "type", None) == MidiEventType.META or hasattr(event, "meta_type"):
            # meta event: 0xFF, type, length (vlq), data
            # meta events are not subject to running status
            self.status = -1
            self.put(0xff)
            self.put(event.meta_type & 0xff)
            self.putvl(len(event.meta_data))
            if event.meta_data:
                self._write(event.meta_data)
        else:
            # unsupported: sysex etc in this writer
            pass

    def write_track(self, t: MidiTrack) -> bool:
        self._write(b'MTrk')
        lenpos = self.fp.tell()
        self.write_long(0)  # dummy
        self.status = -1

        # write tempo event at start of track
        # kinda scuffed since it only adds the starting tempo but hackathon lol
        self.put(0x00)
        self.put(0xff)
        self.put(MetaEventConstants.META_TEMPO)
        self.put(3)
        bps = self._tempoMap.get(0, 2.0)
        print("Tempo in beats per second: ", bps)
        tempo = int((1.0/bps) * 1000000) # convert to microseconds per beat for MIDI storage
        print("Tempo in microseconds per beat:", tempo)
        self.put((tempo >> 16) & 0xff)
        self.put((tempo >> 8) & 0xff)
        self.put(tempo & 0xff)

        tick = 0
        for ntick, ev in sorted(t.events().items()):
            self.putvl(ntick - tick)
            self.write_event(ev)
            tick = ntick
        # write end of track
        self.putvl(1)
        self.put(0xff)
        self.put(MetaEventConstants.META_EOT)
        self.putvl(0)
        endpos = self.fp.tell()
        # go back and write track length
        self.fp.seek(lenpos)
        self.write_long(endpos - lenpos - 4)
        self.fp.seek(endpos)
        return True


if __name__ == '__main__':
    # simple smoke test when run directly
    import sys
    if len(sys.argv) < 2:
        print('Usage: midifile.py <midi-file>')
    else:
        mf = MidiFile()
        mf.read(sys.argv[1])
        print('Read OK, tracks:', len(mf._tracks))
