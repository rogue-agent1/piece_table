#!/usr/bin/env python3
"""Piece Table — text editor data structure (used by VS Code)."""
class Piece:
    def __init__(self, source, start, length): self.source, self.start, self.length = source, start, length
class PieceTable:
    def __init__(self, text=""):
        self.original = text; self.added = ""
        self.pieces = [Piece('original', 0, len(text))] if text else []
    def _buf(self, source): return self.original if source == 'original' else self.added
    def insert(self, pos, text):
        add_start = len(self.added); self.added += text
        new_piece = Piece('added', add_start, len(text))
        offset = 0; new_pieces = []
        inserted = False
        for p in self.pieces:
            if not inserted and offset + p.length >= pos:
                split = pos - offset
                if split > 0: new_pieces.append(Piece(p.source, p.start, split))
                new_pieces.append(new_piece); inserted = True
                if split < p.length: new_pieces.append(Piece(p.source, p.start + split, p.length - split))
            else: new_pieces.append(p)
            offset += p.length
        if not inserted: new_pieces.append(new_piece)
        self.pieces = new_pieces
    def delete(self, pos, length):
        offset = 0; new_pieces = []; remaining = length
        for p in self.pieces:
            if remaining <= 0: new_pieces.append(p); continue
            pend = offset + p.length
            if pos >= pend: new_pieces.append(p)
            elif pos <= offset and pos + length >= pend: remaining -= p.length
            else:
                if pos > offset: new_pieces.append(Piece(p.source, p.start, pos - offset))
                skip = min(remaining, pend - max(pos, offset))
                remaining -= skip
                after = pend - (max(pos, offset) + skip)
                if after > 0: new_pieces.append(Piece(p.source, p.start + p.length - after, after))
            offset += p.length
        self.pieces = new_pieces
    def __str__(self):
        return ''.join(self._buf(p.source)[p.start:p.start+p.length] for p in self.pieces)
    def __len__(self): return sum(p.length for p in self.pieces)
if __name__ == "__main__":
    pt = PieceTable("Hello World")
    print(f"'{pt}'"); pt.insert(5, " Beautiful"); print(f"'{pt}'")
    pt.delete(5, 10); print(f"'{pt}'")
