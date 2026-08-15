# -*- coding: utf-8 -*-
"""Fix all level files: ensure box count == goal count for every level."""
import os

LEVELS_DIR = os.path.join(os.path.dirname(__file__), "levels")

def make_row(width, mapping=None):
    """Build a row string of given width. mapping={col: char} dict."""
    row = [' '] * width
    if mapping:
        for c, ch in mapping.items():
            row[c] = ch
    return ''.join(row)


def write_file(name, rows):
    path = os.path.join(LEVELS_DIR, name)
    with open(path, 'w') as f:
        for r in rows:
            f.write(r + '\n')


print("========================================")
print("FIXING LEVEL FILES")
print("========================================\n")

# ====================== LEVEL 01: already OK (1 box, 1 goal) ======================
with open(os.path.join(LEVELS_DIR, "level_01.txt")) as f:
    lines = f.read().strip().split('\n')
b = sum(1 for l in lines for c in l if c == '$')
g = sum(1 for l in lines for c in l if c == '.')
print(f"  level_01.txt: {len(lines)}rows {len(lines[0])}cols  boxes={b} goals={g} [OK]")

# ====================== LEVEL 02: already fixed (2 boxes, 2 goals) ======================
with open(os.path.join(LEVELS_DIR, "level_02.txt")) as f:
    lines = f.read().strip().split('\n')
b = sum(1 for l in lines for c in l if c == '$')
g = sum(1 for l in lines for c in l if c == '.')
print(f"  level_02.txt: {len(lines)}rows {len(lines[0])}cols  boxes={b} goals={g} [OK]")

# ====================== LEVEL 03: already fixed (2 boxes, 2 goals) ======================
with open(os.path.join(LEVELS_DIR, "level_03.txt")) as f:
    lines = f.read().strip().split('\n')
for l in lines:
    print(f"  L3 row '{l}' (len={len(l)})")
b = sum(1 for l in lines for c in l if c == '$')
g = sum(1 for l in lines for c in l if c == '.')
if b != g:
    print("  --- NEEDS FIX ---\n")
else:
    print(f"  level_03.txt: {len(lines)}rows {len(lines[0])}cols  boxes={b} goals={g} [OK]\n")

# ====================== LEVEL 04: 2 boxes, 2 goals, 10 cols ======================
print("--- Fixing level_04.txt ---")
w = 10
L4_rows = []
L4_rows.append(make_row(w, {c:'#' for c in range(w)}))           # r0: top wall
L4_rows.append(make_row(w, {0:'#',9:'#'}))                       # r1: side walls
L4_rows.append(make_row(w, {0:'#',2:'.',5:'$',9:'#'}))           # r2: goal(2,2), box(2,5)
L4_rows.append(make_row(w, {0:'#',3:' ',6:'@',9:'#'}))           # r3: player(3,6)
L4_rows.append(make_row(w, {0:'#',2:'.',5:'$',9:'#'}))           # r4: goal(4,2), box(4,5)... wait that's another pair
# Nope, need total 2 boxes & 2 goals only
L4_rows = []
L4_rows.append(make_row(w, {c:'#' for c in range(w)}))           # r0
L4_rows.append(make_row(w, {0:'#',9:'#'}))                        # r1
L4_rows.append(make_row(w, {0:'#',2:'.',4:'$',9:'#'}))           # r2: goal col2, box col4
L4_rows.append(make_row(w, {0:'#',3:'@',6:'.',9:'#'}))           # r3: player col3, goal col6
L4_rows.append(make_row(w, {0:'#',4:'$',9:'#'}))                 # r4: box col4
L4_rows.append(make_row(w, {c:'#' for c in range(w)}))           # r5
boxes = sum(1 for r in L4_rows for c in r if c == '$')
goals = sum(1 for r in L4_rows for c in r if c == '.')
print(f"  Proposed: {len(L4_rows[0])}cols x {len(L4_rows)}rows  boxes={boxes} goals={goals}")
assert boxes == goals == 2, f"L4 counts wrong: {boxes}b {goals}g"
write_file("level_04.txt", L4_rows)
print("  Written!\n")

# ====================== LEVEL 05: 2 boxes, 2 goals ======================
print("--- Fixing level_05.txt ---")
w = 10
L5 = [
    make_row(w, {c:'#' for c in range(w)}),         # r0
    make_row(w, {0:'#',9:'#'}),                      # r1
    make_row(w, {0:'#',3:'.',9:'#'}),                # r2: 1 goal
    make_row(w, {0:'#',3:'$',9:'#'}),                # r3: 1 box
    make_row(w, {0:'#',3:'@',9:'#'}),                # r4: 1 player
    make_row(w, {0:'#',3:'.',9:'#'}),                # r5: 1 goal ... still only 1 box
]
# Need 2 of each:
L5 = [
    make_row(w, {c:'#' for c in range(w)}),           # r0
    make_row(w, {0:'#',9:'#'}),                        # r1
    make_row(w, {0:'#',2:'.',8:'.',9:'#'}),            # r2: 2 goals
    make_row(w, {0:'#',2:'$',8:'$',9:'#'}),            # r3: 2 boxes
    make_row(w, {0:'#',2:'@',9:'#'}),                  # r4: 1 player
    make_row(w, {c:'#' for c in range(w)}),             # r5
]
boxes = sum(1 for r in L5 for c in r if c == '$')
goals = sum(1 for r in L5 for c in r if c == '.')
print(f"  Proposed: {len(L5[0])}cols x {len(L5)}rows  boxes={boxes} goals={goals}")
assert boxes == goals == 2
write_file("level_05.txt", L5)
print("  Written!\n")

# ====================== LEVEL 06: 2 boxes, 2 goals ======================
print("--- Fixing level_06.txt ---")
w = 10
L6 = [
    make_row(w, {c:'#' for c in range(w)}),           # r0
    make_row(w, {0:'#',9:'#'}),                        # r1
    make_row(w, {0:'#',3:'.',7:'.',9:'#'}),            # r2: 2 goals
    make_row(w, {0:'#',3:'$',7:'$',9:'#'}),            # r3: 2 boxes
    make_row(w, {0:'#',3:'@',9:'#'}),                  # r4: player
    make_row(w, {c:'#' for c in range(w)}),             # r5
]
boxes = sum(1 for r in L6 for c in r if c == '$')
goals = sum(1 for r in L6 for c in r if c == '.')
print(f"  Proposed: {len(L6[0])}cols x {len(L6)}rows  boxes={boxes} goals={goals}")
assert boxes == goals == 2
write_file("level_06.txt", L6)
print("  Written!\n")

# ====================== LEVEL 07: 2 boxes, 2 goals ======================
print("--- Fixing level_07.txt ---")
w = 12
L7 = [
    make_row(w, {c:'#' for c in range(w)}),           # r0
    make_row(w, {0:'#',11:'#'}),                       # r1
    make_row(w, {0:'#',3:'.',9:'.',11:'#'}),           # r2: 2 goals
    make_row(w, {0:'#',4:'$',8:'$',11:'#'}),           # r3: 2 boxes offset
    make_row(w, {0:'#',3:'@',11:'#'}),                 # r4: player
    make_row(w, {c:'#' for c in range(w)}),             # r5
]
boxes = sum(1 for r in L7 for c in r if c == '$')
goals = sum(1 for r in L7 for c in r if c == '.')
print(f"  Proposed: {len(L7[0])}cols x {len(L7)}rows  boxes={boxes} goals={goals}")
assert boxes == goals == 2
write_file("level_07.txt", L7)
print("  Written!\n")

# ====================== FINAL VERIFICATION ======================
print("="*40)
print("FINAL VERIFICATION OF ALL LEVELS")
print("="*40)
all_ok = True
for i in range(1, 8):
    path = os.path.join(LEVELS_DIR, f"level_{i:02d}.txt")
    with open(path) as f:
        lines = f.read().strip().split('\n')
    w_set = set(len(l) for l in lines)
    b = sum(1 for l in lines for c in l if c == '$')
    g = sum(1 for l in lines for c in l if c == '.')
    p = sum(1 for l in lines for c in l if c in ('@', '+'))
    s = sum(1 for l in lines for c in l if c in ('*', '!'))
    ok = (b == g and len(w_set) == 1 and p > 0 and s == 0)
    status = "OK" if ok else "ISSUE"
    if not ok:
        all_ok = False
    print(f"\n  level_{i:02d}.txt [{status}]")
    max_w = max(w_set)
    for ri, lr in enumerate(lines):
        marker = f" <<< WIDTH MISMATCH ({lr} vs expected {max_w})" if len(lr) != max_w else ""
        print(f"      r{ri:2d}: |{lr}| len={len(lr)}{marker}")

print("\n" + "="*40)
if all_ok:
    print("ALL LEVELS PASS!")
else:
    print("SOME LEVELS STILL HAVE ISSUES!")
print("="*40)
