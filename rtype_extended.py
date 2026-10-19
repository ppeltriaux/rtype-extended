#!/usr/bin/env python3
"""R-Type Extended: patch your own arcade R-Type ROMs (MAME's "rtype" set, World) into the game
with a two-player co-op mode, a stage select, an Armour mode and a Boss Rush.

  python3 rtype_extended.py <your rtype.zip, or a folder of its files> [--set rtype|rtypeu] [-o DIR]

Your ROMs are found by their contents (SHA1), whatever their names, in a zip or a folder (a
merged set with the clones in it is fine). The patch holds no 3 bytes in a row of the original:
the program gets the hack's own bytes, and any 3 bytes or more in a row your program already has
(the instructions each hook moves aside, short sequences the new code shares with the original)
are copied from where they are in yours; the new graphics and player 2's palettes are made from
your ROMs by the code below; every file written is checked against the SHA1 it must have. Writes DIR/rtype.zip (or DIR/rtypeu.zip with --set rtypeu: the same game as
MAME's R-Type (US) clone, to sit beside an original rtype.zip), DIR being ./rtype-extended unless
-o says otherwise. Your files are only read. Standard library only (Python 3.8 or later).
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import zipfile
import zlib

VERSION = '2026-10-20 (baee820)'
PATCH = """
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
sP1dOfi7cvCfrxz8x3/8f2rssn8=
"""
# --- the new tiles and player 2's palettes, made from your ROMs ---
import colorsys

# the program ROMs: (even-byte ROM, odd-byte ROM, CPU address); the fg and sprite ROMs' planes,
# plane 0 first (each sprite plane a 64K + 32K pair)
PROGRAM = [("rt_r-l0-b.3b", "rt_r-h0-b.1b", 0x00000), ("rt_r-l1-b.3c", "rt_r-h1-b.1c", 0x20000)]
FG_PLANES = [("rt_b-a0.3c",), ("rt_b-a1.3d",), ("rt_b-a2.3a",), ("rt_b-a3.3e",)]
SPRITE_PLANES = [("rt_r-00.1h", "rt_r-01.1j"), ("rt_r-10.1k", "rt_r-11.1l"),
                 ("rt_r-20.3h", "rt_r-21.3j"), ("rt_r-30.3k", "rt_r-31.3l")]

PAL_BASE = 0x3B000               # ROM palettes (3B00:0000): 16 colours x (R, G, B), 0-31 each
P2_PALETTES = {2: 176, 86: 177}  # player 2's copies of the R-9's and the Force's palettes, in
                                 # zero-filled entries no code reads (108-191: an invulnerable
                                 # run through all eight stages read none); src/v30/coop.asm MapPal
# Co-op: player 2's colours (the Neo Geo port's too). Per ROM sprite
# palette, its colour groups: the R-9's (palette 2, also its shots and wave cannon) canopy / nose /
# flame, red stripe, gold markings; the Force's (86) fire. A scheme gives each group a hue
# (saturation and value kept, so fades still work); groups it leaves out keep their colours.
# Player 2's sprites show these palettes in place of their slot's. Previewed schemes, P2_SCHEME
# picks one:
P2_GROUPS = {2: {"canopy": (3, 4, 5), "stripe": (6, 7), "marks": (11, 12, 13)},
             86: {"fire": (10, 11, 12, 13, 14)}}
P2_SCHEMES = {"crimson": dict(canopy=352, stripe=45, marks=45, fire=330),
              "emerald": dict(canopy=140, stripe=45, marks=45, fire=125),
              "violet": dict(canopy=275, stripe=320, marks=45, fire=285),
              "sunset": dict(canopy=22, stripe=205, marks=50, fire=200),
              "ice": dict(canopy=205, stripe=190, marks=190, fire=195)}
P2_SCHEME = "crimson"
# Player 2's HUD text in crimson: copies of the original's HUD glyphs drawing with the HUD
# palette's (slot 15, ROM palette $1F) red pens instead (11 red, 12 dark red)
P2_PENS = {2: 11, 3: 12, 6: 12, 7: 11, 8: 11}
# The arcade hack's new fg tiles go on blank codes the game never writes (an invulnerable run
# through all eight stages wrote none of them), from the top down; the 1P / 2P tags on two blank
# sprite tiles outside every sprite that run drew (each sprite's tiles: code + 8 x + y over its size)
P2_GLYPHS = [0x30 + d for d in range(10)] + [0x011, 0x065, 0x066, 0x063, 0x064, 0x06A] + \
    [ord(c) for c in "PRESTA"]   # digits, the score's blank, "2P-", the ship icon, PRESS START
GAUGE_TILES = list(range(0x6AD, 0x6C0))     # the beam gauge's caps and cells
FG_SPARE = range(0xF63, 0xF00, -2)  # blank codes never written: the odd ones $F63-$F01 (the
                                     # even blank ones there are written: a stage's empty cells)
ARMOUR_PENS = {14: 8, 15: 12}   # the Armour cells' green / yellow (3+ ships, 2): the HUD's tile
                                # palette has neither and no pen to spare (stage tiles drawn with
                                # it use its black pens 14 / 15), so its light blue and amber
TAG_TILES = (0x97C, 0x97D)      # the 2P and 1P tags (sprite tiles)


def read_program(roms):
    """the program as the CPU sees it (256 KB) from the program ROMs ({board name: contents})"""
    data = bytearray(0x40000)
    for lo, hi, base in PROGRAM:
        data[base:base + 2 * len(roms[lo]):2] = roms[lo]
        data[base + 1:base + 2 * len(roms[hi]):2] = roms[hi]
    return data


def split_program(data):
    """{board name: contents} of the program ROMs holding data"""
    out = {}
    for lo, hi, base in PROGRAM:
        out[lo] = bytes(data[base:base + 0x20000:2])
        out[hi] = bytes(data[base + 1:base + 0x20000:2])
    return out


def p2_palettes(prog):
    """Player 2's palettes: the R-9's (2) and the Force's (86) with their colour groups turned to
    the scheme (hue set, saturation and value kept), written to their P2_PALETTES entries."""
    scheme = P2_SCHEMES[P2_SCHEME]
    for n, dest in P2_PALETTES.items():
        src = PAL_BASE + 48 * n
        pal = [list(prog[src + 3 * i:src + 3 * i + 3]) for i in range(16)]
        for g, idx in P2_GROUPS[n].items():
            if g not in scheme:
                continue
            for i in idx:
                h, sat, v = colorsys.rgb_to_hsv(*(c / 31 for c in pal[i]))
                if g == "fire":
                    sat = max(0.25, sat)
                pal[i] = [round(c * 31) for c in colorsys.hsv_to_rgb(scheme[g] / 360, sat, v)]
        at = PAL_BASE + 48 * dest
        if any(prog[at:at + 48]):
            raise ValueError("palette %d is not free" % dest)
        prog[at:at + 48] = bytes(c for col in pal for c in col)


def fg_tiles(roms):
    """The fg ROM as 4096 8x8 tiles of pens (rows of 8)."""
    pl = [roms[f[0]] for f in FG_PLANES]
    tiles = []
    for c in range(len(pl[0]) // 8):
        tiles.append([[sum(((pl[p][c * 8 + y] >> (7 - x)) & 1) << p for p in range(4))
                       for x in range(8)] for y in range(8)])
    return tiles


def put_fg(roms, code, tile):
    for p, f in enumerate(FG_PLANES):
        data = bytearray(roms[f[0]])
        for y in range(8):
            data[code * 8 + y] = sum(((tile[y][x] >> p) & 1) << (7 - x) for x in range(8))
        roms[f[0]] = bytes(data)


def put_sprite(roms, code, tile):
    """A 16x16 sprite tile (rows of 16 pens) at code: each plane is a 64K + 32K ROM pair, 32
    bytes a tile, a row's left 8 pixels at + y, its right 8 at + 16 + y."""
    for p, (lo, hi) in enumerate(SPRITE_PLANES):
        data = bytearray(roms[lo] + roms[hi])
        for y in range(16):
            for half in range(2):
                data[code * 32 + half * 16 + y] = sum(((tile[y][half * 8 + x] >> p) & 1) << (7 - x)
                                                      for x in range(8))
        roms[lo], roms[hi] = bytes(data[:len(roms[lo])]), bytes(data[len(roms[lo]):])


def armour_tiles(fg):
    """Armour's ship gauge in the beam gauge's style, 6 tiles: a cell green, yellow, red, empty;
    the left cap; the right cap. A cell is the gauge's body ($6BA full, $6AE empty) with a light
    line (pen 4, the frame's) down each side in the fill rows, so cells meet in a 2-pixel
    separator like the walls; the fill is flat: pen 14 (green) or 15 (yellow) (the Neo Geo's
    HUD palette's unused pens; the arcade maps them, ARMOUR_PENS), or 11 (the HUD's red). The caps
    are the original's ($6AD, $6BF) with their nub and wall moved against the cells (shifted 4
    pixels inwards, the 4 pixels of box inside them gone) so a cap does not read as half a cell."""
    def cell(src, pen):
        t = [list(row) for row in src]
        for y in range(2, 7):
            for x in range(1, 7):
                if pen:
                    t[y][x] = pen
            t[y][0] = t[y][7] = 4
        return t
    left = [[9] * 4 + row[:4] for row in fg[0x6AD]]
    right = [row[4:] + [9] * 4 for row in fg[0x6BF]]
    return [cell(fg[0x6BA], 14), cell(fg[0x6BA], 15), cell(fg[0x6BA], 11), cell(fg[0x6AE], 0), left, right]


def colon_tile(fg):
    """Boss Rush's timer: a colon (the font has none), the full stop's dot and a copy 4 lines up
    (the font's background is pen 1, its glyphs pens 2 and 3)."""
    dot = fg[0x2E]
    return [[dot[y + 4][x] if y + 4 < 8 and dot[y + 4][x] > 1 else dot[y][x] for x in range(8)]
            for y in range(8)]


def hud_tiles(roms):
    """Player 2's crimson glyphs and mirrored gauge, Armour's cells, the tags, Boss Rush's colon,
    written into roms ({board name: contents}); -> their codes: glyphs [(the original's code, its
    copy's)], gauge [codes], armour [codes], colon code."""
    fg = fg_tiles(roms)
    spare = [c for c in FG_SPARE if not any(any(r) for r in fg[c])]
    if len(spare) < len(P2_GLYPHS) + len(GAUGE_TILES) + 7:
        raise ValueError("not enough spare fg codes")
    glyphs, gauge, armour = [], [], []
    for c in P2_GLYPHS:
        code = spare.pop(0)
        put_fg(roms, code, [[P2_PENS.get(v, v) for v in row] for row in fg[c]])
        glyphs.append((c, code))
    for c in GAUGE_TILES:
        code = spare.pop(0)
        put_fg(roms, code, [[P2_PENS.get(v, v) for v in row[::-1]] for row in fg[c]])
        gauge.append(code)
    for t in armour_tiles(fg):
        code = spare.pop(0)
        put_fg(roms, code, [[ARMOUR_PENS.get(v, v) for v in row] for row in t])
        armour.append(code)
    colon = spare.pop(0)
    put_fg(roms, colon, colon_tile(fg))
    for tile, digit in zip(TAG_TILES, (0x32, 0x31)):
        # the HUD font's digit and P (fg, 8x8 each) on 16 x 16, in ship palette pens: outline
        # black (1) only around the glyph, the light pen the canopy's brightest (5), the
        # shadow its darkest (3); the rest transparent
        tag = [[0] * 16 for _ in range(16)]
        for k, c in enumerate((digit, 0x50)):
            for y in range(8):
                for x in range(8):
                    tag[4 + y][k * 8 + x] = {1: 1, 2: 5, 3: 3}.get(fg[c][y][x], 0)
        lit = {(y, x) for y in range(16) for x in range(16) if tag[y][x] in (5, 3)}
        for y in range(16):
            for x in range(16):
                if tag[y][x] == 1 and not any((y + dy, x + dx) in lit for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    tag[y][x] = 0
        put_sprite(roms, tile, tag)
    return glyphs, gauge, armour, colon
# --- end of the tiles and palettes ---
MAX_SIZE = 0x20000                 # (the largest ROM in the set: files above it are not looked at)
SETS = ("rtype", "rtypeu")


class PatchError(Exception):
    pass


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def load_inputs(src):
    """{sha1: contents} of every file up to MAX_SIZE in the zip or folder src"""
    found = {}
    if os.path.isdir(src):
        for root, _, names in os.walk(src):
            for n in names:
                path = os.path.join(root, n)
                if os.path.getsize(path) <= MAX_SIZE:
                    with open(path, "rb") as f:
                        data = f.read()
                    found[sha1(data)] = data
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for info in z.infolist():
                if not info.is_dir() and info.file_size <= MAX_SIZE:
                    data = z.read(info)
                    found[sha1(data)] = data
    else:
        raise PatchError("%s: not a zip file or a folder" % src)
    return found


def decode(text):
    return json.loads(zlib.decompress(base64.b64decode("".join(text.split()))))


def build(patch, inputs, set_name):
    """[(file name, contents)] of the patched set set_name from inputs ({sha1: contents})"""
    missing = sorted((v["name"], v["size"], h) for h, v in patch["inputs"].items() if h not in inputs)
    if missing:
        raise PatchError("not found in your files (by content), so they are not MAME's \"rtype\" (World) set:\n" +
                         "\n".join("  %s  %6d bytes  SHA1 %s" % m for m in missing))
    roms = {v["name"]: inputs[h] for h, v in patch["inputs"].items()}
    orig = bytes(read_program(roms))
    prog = read_program(roms)
    try:
        p2_palettes(prog)                           # (made from your ROMs, as are the tiles)
        files = dict(roms)
        hud_tiles(files)
    except ValueError as e:
        raise PatchError(str(e))
    for op in patch["program"]:                     # ["L", address, our bytes] or
        if op[0] == "L":                            # ["C", address, your program's address, length]
            new = bytes.fromhex(op[2])
            prog[op[1]:op[1] + len(new)] = new
        else:
            prog[op[1]:op[1] + op[3]] = orig[op[2]:op[2] + op[3]]
    files.update(split_program(prog))
    out = []
    for e in patch["sets"][set_name]:
        data = files[e["board"]] if e["board"] else bytes(e["size"])
        if len(data) != e["size"] or sha1(data) != e["sha1"]:
            raise PatchError("%s: the result is not what it must be (SHA1 %s, wanted %s)" % (e["name"], sha1(data), e["sha1"]))
        out.append((e["name"], data))
    return out


def write_zip(files, path):
    tmp = path + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files:
            z.writestr(name, data)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="R-Type Extended %s: patch your own arcade R-Type ROMs "
                                 "(MAME's \"rtype\" set)." % (VERSION or "(development)"))
    ap.add_argument("roms", help="your rtype.zip, or a folder with its files")
    ap.add_argument("--set", choices=SETS, default="rtype",
                    help="rtype (default): replaces the World set; rtypeu: as MAME's R-Type (US) clone, beside an original rtype.zip")
    ap.add_argument("-o", "--out", default="rtype-extended", help="the folder to write the zip to (default: ./rtype-extended)")
    args = ap.parse_args(argv)
    if PATCH is None:
        print("this copy of the patcher carries no patch", file=sys.stderr)
        return 2
    path = os.path.join(args.out, args.set + ".zip")
    if os.path.exists(path) and os.path.exists(args.roms) and os.path.samefile(path, args.roms):
        print("%s is your input: pick another output folder (-o), so your original stays as it is" % path, file=sys.stderr)
        return 2
    try:
        patch = decode(PATCH)
        files = build(patch, load_inputs(args.roms), args.set)
    except PatchError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)
    write_zip(files, path)
    ours = sum(len(op[2]) // 2 for op in patch["program"] if op[0] == "L")
    copied = sum(op[3] for op in patch["program"] if op[0] == "C")
    print("wrote %s: %d files; the program: %d bytes of the hack's, %d copied from your own; the graphics\n"
          "and palettes made from yours. Put it where MAME looks for ROMs (it warns that the checksums\n"
          "are wrong: the ROMs are changed) and run \"%s\"." % (path, len(files), ours, copied, args.set))
    return 0


if __name__ == "__main__":
    sys.exit(main())
