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

VERSION = '2026-10-20 (decdf1f)'
PATCH = """
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
B9vflYO/Kwf/+crBf/zH/wcXnLLl
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
