"""A Python translation of the MuseScore tempomap.cpp file Werner Schweer,
   converted by VSCode Chat"""

from bisect import bisect_left
from typing import List, Tuple


class TempoMap:
    """A small ordered map from tick -> tempo (float).

    This mirrors the behavior in the original C++: entries are
    stored sorted by tick. Methods provided:
    - insert(tick, tempo)
    - tempo(tick)
    - time2tick(val, relTempo, division)
    """

    def __init__(self):
        self._entries: List[Tuple[int, float]] = []

    def empty(self) -> bool:
        return len(self._entries) == 0

    def insert(self, tick: int, tempo: float):
        # keep entries sorted by tick
        idx = bisect_left([e[0] for e in self._entries], tick)
        if idx < len(self._entries) and self._entries[idx][0] == tick:
            self._entries[idx] = (tick, tempo)
        else:
            self._entries.insert(idx, (tick, tempo))

    def begin(self):
        return 0

    def end(self):
        return len(self._entries)

    def lower_bound_index(self, tick: int):
        """Return index of first entry with key >= tick, or len(entries) if none."""
        return bisect_left([e[0] for e in self._entries], tick)

    def tempo(self, tick: int) -> float:
        if self.empty():
            return 2.0
        i = self.lower_bound_index(tick)
        if i == len(self._entries):
            # use last
            return self._entries[-1][1]
        if self._entries[i][0] == tick:
            return self._entries[i][1]
        if i == 0:
            return 2.0
        return self._entries[i][1]

    def time2tick(self, val: float, relTempo: float, division: int) -> int:
        time = 0.0
        tick = 0
        tempoDiv = division * relTempo

        tempo = 2.0
        # iterate entries in order
        for e in self._entries:
            delta = e[0] - tick
            time2 = time + float(delta) / (tempoDiv * tempo)
            if val > time2:
                break
            tick = e[0]
            tempo = e[1]
            time = time2
        return int(tick + (val - time) * tempoDiv * tempo)
