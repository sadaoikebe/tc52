#!/usr/bin/env python3
"""check_markers.py : clearance of the pin-1 silk markers (group "pin1-markers" in pcb/ts52k.kicad_pcb).

For every marker listed in markers.json, prints the smallest distance (mm, negative = overlap) to
  mask : the B.Mask openings of the pads (what JLCPCB clips silk against)
  silk : every other B.SilkS item (footprint lines/texts, board texts; the markers themselves excluded)
  edge : Edge.Cuts
X2's own outline is left out of 'silk' for the X2 markers: the bold L is drawn over it on purpose.
Run from the repository root with the system python (pcbnew):
  /usr/bin/python3 -I docs/tc52-silk-pin1/check_markers.py pcb/ts52k.kicad_pcb docs/tc52-silk-pin1/markers.json
"""
import json, math, sys
import pcbnew
mm = pcbnew.ToMM
ERR = pcbnew.FromMM(0.005)
board = pcbnew.LoadBoard(sys.argv[1])
markers = json.load(open(sys.argv[2]))
skip = set()
for g in board.Groups():
    if g.GetName() == "pin1-markers":
        skip = {i.m_Uuid.AsString() for i in g.GetItems()}

def polys(item, layer):
    ps = pcbnew.SHAPE_POLY_SET()
    if isinstance(item, pcbnew.PCB_TEXT):
        item.TransformTextToPolySet(ps, 0, ERR, pcbnew.ERROR_INSIDE)
    else:
        item.TransformShapeToPolygon(ps, layer, 0, ERR, pcbnew.ERROR_INSIDE)
    return [[(mm(ps.Outline(i).CPoint(k).x), mm(ps.Outline(i).CPoint(k).y)) for k in range(ps.Outline(i).PointCount())]
            for i in range(ps.OutlineCount())]

mask, silk, edge = [], [], []
for fp in board.GetFootprints():
    r = fp.GetReference()
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.B_Mask):
            mask += [(f"{r}.{p.GetNumber()}", q) for q in polys(p, pcbnew.B_Mask)]
    for it in list(fp.GraphicalItems()) + [fp.Reference(), fp.Value()]:
        if it.GetLayer() == pcbnew.B_SilkS and (not isinstance(it, pcbnew.PCB_TEXT) or it.IsVisible()):
            silk += [(r, q) for q in polys(it, pcbnew.B_SilkS)]
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.B_SilkS and d.m_Uuid.AsString() not in skip:
        silk += [("board", q) for q in polys(d, pcbnew.B_SilkS)]
    if d.GetLayer() == pcbnew.Edge_Cuts:
        edge += [("edge", q) for q in polys(d, pcbnew.Edge_Cuts)]

def dist(px, py, q):
    best, inside, n = 1e9, False, len(q)
    for i in range(n):
        x1, y1 = q[i]; x2, y2 = q[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1; L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L))
        best = min(best, math.hypot(px - x1 - t * dx, py - y1 - t * dy))
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return -best if inside else best

for m in markers:
    if m["kind"] == "dot":
        S = [(m["x"], m["y"], m["d"] / 2)]
        what = f"dot d={m['d']} at ({m['x']}, {m['y']})"
    else:
        S = [(m["x1"] + (m["x2"] - m["x1"]) * i / 60, m["y1"] + (m["y2"] - m["y1"]) * i / 60, m["w"] / 2) for i in range(61)]
        what = f"line w={m['w']} ({m['x1']}, {m['y1']})-({m['x2']}, {m['y2']})"
    x0, x1 = min(s[0] for s in S) - 3, max(s[0] for s in S) + 3
    y0, y1 = min(s[1] for s in S) - 3, max(s[1] for s in S) + 3
    out = []
    for kind, lst in (("mask", mask), ("silk", silk), ("edge", edge)):
        res = {}
        for n, q in lst:
            if kind == "silk" and m["ref"] == "X2" and n == "X2":
                continue
            if min(a for a, _ in q) > x1 or max(a for a, _ in q) < x0 or min(b for _, b in q) > y1 or max(b for _, b in q) < y0:
                continue
            res[n] = min(res.get(n, 9), min(dist(x, y, q) - r for x, y, r in S))
        top = sorted((v, k) for k, v in res.items())[:2]
        out.append(kind + " " + (", ".join(f"{k} {v:+.3f}" for v, k in top) or "> 3 mm"))
    print(f"{m['ref']:4} {what:46} " + " | ".join(out))
