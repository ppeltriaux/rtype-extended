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

VERSION = '2026-10-20 (7d13fb5)'
PATCH = """
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
x6kfc13KdA9r5wExBTPQgu+6DnoccwzV6hI3/mhaau05lNTn71OEleJ5hWbKYa32akrV55DT8R9q
yrlDYPCXUklzFZ3BQ1dnjLj30+y0tEZ3aY1mA0B+hW6YjShaOfPQDJspR9YZzFKtlB9wrp1Eosvy
xi7ejkGe/XakcLjR1TNYKarSo3kvP2IJNvp5APun9YXN/cXogmLQU8sPBg9kCqiA0Q4i3SR8muCL
3tSJM6LHZria2O+2uJtyXHqJXqS6bYqbG29LxV5LB1/6LcihZEaTRvEUrURThXc49hEV+y3QY/lt
rblbu6Ag64mkk56ydl1VNuru0D9mOGn03R2j1df/QSshVVcRyTWgaSllkt7P4o6igPLSE2f+nuKh
v07tMpEaxZcBBxBgXN1X2IbcyiW5mHKXpqTroOOdr8E2Vy8vhv1uP8FvCu0u3ZbuInEntREkeMBN
6t+yEYpZRQ2s/W5VqxIM5x5FsUHvVjXMpbd36fSE+LqZa2sXvs71XJ0Wsjs9mWNhNLqugTeldH5v
qmQQL/6CjZ80KFrdPLemsmRQNXkxHKaYkhD1oM0ZIZy2OPDRYC5oaieXjlg3mKz2rdzqmjjZl7FJ
fURbe/QOTNSYcjo26O2Kskpc3+38pn0OuzHoK/XKwALvXTaYuUxKMltPYi2xxLEosTSdi7piuSAJ
dj7EP80fgRH1EGa0RanzSHbVAuaNZhwu3ewftDVwWRnMOOsLeIiuoEk4YVXN8I6Dnwb1KWhFPi32
U5p4k3ZeJNXznjrfvvfyvbl4aYxKwA6KQ3/NexI67CdVjpaeXUIQIbVhDLNvbff6K66gZu7GQcNx
cWBr5p42XZa2HR7JWZWlBS+YGpMe60WDWpk9dXfdsywDnWxBsDvvYjcFi+7ZN40qJG3WWRGrkwGM
psoaV0lDJGcsxVSJMU6RepweQXHbMZPcskAsZhi4mFLW5u7GSIlYYjPtdrrZ5mhXAyN6XWp6Nj1j
AX0zH6PRrxaDlpDEN+bVjD9Ho0dl6DkHU1AsTC3pBedp00y1Nt1jeo++mi3WuTttu3TDdHUDA9QM
H/RCHzFvy1LxmL6AU588snR5+h1Hb3TI5i/HsB8DZdIfJNoDW9PzTrvh7cqliR8m4OFQ3QLPyzF5
wI6Th62uj+4WYEd2sHhPMM4zhTmbLlzpXxu7Ga8qs2dKoUAsOZvJa7IabDO88butGk9WxVWjm6C4
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
bH9XDv6uHPznKwf/8R//H0swslQ=
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
