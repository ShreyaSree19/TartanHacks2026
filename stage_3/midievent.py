"""A Python translation of the MuseScore midifile.cpp file by Werner Schweer,
   converted by VSCode Chat"""

from enum import IntEnum
from dataclasses import dataclass


class MidiEventType(IntEnum):
    NOTEOFF    = 0x80
    NOTEON     = 0x90
    POLYAFTER  = 0xa0
    CONTROLLER = 0xb0
    PROGRAM    = 0xc0
    AFTERTOUCH = 0xd0
    PITCHBEND  = 0xe0
    META       = 0xff
    SYSEX      = 0xf0
    SONGPOS    = 0xf2
    ENDSYSEX   = 0xf7
    CLOCK      = 0xf8
    START      = 0xfa
    CONTINUE   = 0xfb
    STOP       = 0xfc
    SENSE      = 0xfe


# Controller constants
class ControllerConstants(IntEnum):
    CTRL_HBANK = 0x00
    CTRL_LBANK = 0x20
    CTRL_HDATA = 0x06
    CTRL_LDATA = 0x26
    CTRL_HNRPN = 0x63
    CTRL_LNRPN = 0x62
    CTRL_HRPN = 0x65
    CTRL_LRPN = 0x64
    CTRL_MODULATION = 0x01
    CTRL_BREATH = 0x02
    CTRL_FOOT = 0x04
    CTRL_PORTAMENTO_TIME = 0x05
    CTRL_VOLUME = 0x07
    CTRL_PANPOT = 0x0a
    CTRL_EXPRESSION = 0x0b
    CTRL_SUSTAIN = 0x40
    CTRL_PORTAMENTO = 0x41
    CTRL_SOSTENUTO = 0x42
    CTRL_SOFT_PEDAL = 0x43
    CTRL_HARMONIC_CONTENT = 0x47
    CTRL_RELEASE_TIME = 0x48
    CTRL_ATTACK_TIME = 0x49
    CTRL_BRIGHTNESS = 0x4a
    CTRL_PORTAMENTO_CONTROL = 0x54
    CTRL_REVERB_SEND = 0x5b
    CTRL_CHORUS_SEND = 0x5d
    CTRL_VARIATION_SEND = 0x5e
    CTRL_ALL_SOUNDS_OFF = 0x78
    CTRL_RESET_ALL_CTRL = 0x79
    CTRL_LOCAL_OFF = 0x7a
    CTRL_ALL_NOTES_OFF = 0x7b


# Meta event constants
class MetaEventConstants(IntEnum):
    META_SEQUENCE_NUMBER = 0
    META_TEXT = 1
    META_COPYRIGHT = 2
    META_TRACK_NAME = 3
    META_INSTRUMENT_NAME = 4
    META_LYRIC = 5
    META_MARKER = 6
    META_CUE_POINT = 7
    META_PROGRAM_NAME = 8
    META_DEVICE_NAME = 9
    META_TRACK_COMMENT = 0x0f
    META_TITLE = 0x10
    META_SUBTITLE = 0x11
    META_COMPOSER = 0x12
    META_TRANSLATOR = 0x13
    META_POET = 0x14
    META_PORT_CHANGE = 0x21
    META_CHANNEL_PREFIX = 0x22
    META_EOT = 0x2f
    META_TEMPO = 0x51
    META_TIME_SIGNATURE = 0x58
    META_KEY_SIGNATURE = 0x59


@dataclass
class MidiEvent:
    _type: MidiEventType = None
    _channel: int = 0
    _dataA: int = 0
    _dataB: int = 0

    def set(self, t: MidiEventType, c: int, a: int, b: int):
        self._type = t
        self._channel = c
        self._dataA = a
        self._dataB = b

    def type(self) -> MidiEventType:
        return self._type

    def setType(self, t: MidiEventType):
        self._type = t

    def channel(self) -> int:
        return self._channel

    def dataA(self) -> int:
        return self._dataA

    def dataB(self) -> int:
        return self._dataB
