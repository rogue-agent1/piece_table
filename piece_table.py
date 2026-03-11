#!/usr/bin/env python3
"""Piece table — text editor data structure used in VS Code.

One file. Zero deps. Does one thing well.

Two buffers (original + add) and a table of pieces pointing into them.
Insert = append to add buffer + split piece. No text is ever moved or copied.
"""
import sys, time
from enum import Enum

class Source(Enum):
    ORIGINAL = 0
    ADD = 1

class Piece:
    __slots__ = ('source', 'start', 'length')
    def __init__(self, source, start, length):
        self.source = source
        self.start = start
        self.length = length
    def __repr__(self):
        s = "orig" if self.source == Source.ORIGINAL else "add"
        return f"Piece({s}[{self.start}:{self.start+self.length}])"

class PieceTable:
    def __init__(self, text=""):
        self._original = text
        self._add = []
        self._pieces = []
        if text:
            self._pieces.append(Piece(Source.ORIGINAL, 0, len(text)))
        self._length = len(text)

    def _find_piece(self, pos):
        """Find piece index and offset within piece for position."""
        offset = 0
        for i, piece in enumerate(self._pieces):
            if offset + piece.length > pos:
                return i, pos - offset
            offset += piece.length
        return len(self._pieces), 0

    def insert(self, pos, text):
        if not text:
            return
        add_start = len(self._add)
        self._add.extend(text)
        new_piece = Piece(Source.ADD, add_start, len(text))
        if not self._pieces or pos == self._length:
            self._pieces.append(new_piece)
        elif pos == 0:
            self._pieces.insert(0, new_piece)
        else:
            idx, offset = self._find_piece(pos)
            if offset == 0:
                self._pieces.insert(idx, new_piece)
            else:
                old = self._pieces[idx]
                left = Piece(old.source, old.start, offset)
                right = Piece(old.source, old.start + offset, old.length - offset)
                self._pieces[idx:idx+1] = [left, new_piece, right]
        self._length += len(text)

    def delete(self, pos, length):
        if length <= 0:
            return
        remaining = length
        idx, offset = self._find_piece(pos)
        while remaining > 0 and idx < len(self._pieces):
            piece = self._pieces[idx]
            avail = piece.length - offset
            if offset == 0 and remaining >= piece.length:
                self._pieces.pop(idx)
                remaining -= piece.length
            elif offset == 0:
                piece.start += remaining
                piece.length -= remaining
                remaining = 0
            elif offset + remaining >= piece.length:
                removed = piece.length - offset
                piece.length = offset
                remaining -= removed
                idx += 1
            else:
                right = Piece(piece.source, piece.start + offset + remaining,
                            piece.length - offset - remaining)
                piece.length = offset
                self._pieces.insert(idx + 1, right)
                remaining = 0
            offset = 0
        self._length -= (length - remaining)

    def __len__(self):
        return self._length

    def __str__(self):
        parts = []
        for piece in self._pieces:
            if piece.source == Source.ORIGINAL:
                parts.append(self._original[piece.start:piece.start + piece.length])
            else:
                parts.append(''.join(self._add[piece.start:piece.start + piece.length]))
        return ''.join(parts)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return str(self)[idx]
        if idx < 0:
            idx += self._length
        offset = 0
        for piece in self._pieces:
            if offset + piece.length > idx:
                local = idx - offset
                if piece.source == Source.ORIGINAL:
                    return self._original[piece.start + local]
                return self._add[piece.start + local]
            offset += piece.length
        raise IndexError(idx)

    def pieces_info(self):
        return f"{len(self._pieces)} pieces, orig={len(self._original)}B, add={len(self._add)}B"

def main():
    pt = PieceTable("Hello, World!")
    print(f"Initial:  '{pt}' ({pt.pieces_info()})")

    pt.insert(7, "Beautiful ")
    print(f"Insert:   '{pt}' ({pt.pieces_info()})")

    pt.delete(7, 10)
    print(f"Delete:   '{pt}' ({pt.pieces_info()})")

    pt.insert(5, " Cruel")
    print(f"Insert:   '{pt}' ({pt.pieces_info()})")

    # Performance
    pt2 = PieceTable("x" * 10000)
    import random
    random.seed(42)
    t0 = time.perf_counter()
    for i in range(10000):
        pos = random.randint(0, len(pt2))
        pt2.insert(pos, "y")
    dt = time.perf_counter() - t0
    print(f"\n10K random inserts: {dt*1000:.1f}ms, {pt2.pieces_info()}")

if __name__ == "__main__":
    main()
