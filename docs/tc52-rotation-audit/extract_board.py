"""Board side of the TC52 (wired) rotation audit (adapted from docs/tc52w-rotation-audit/ on tc52-wireless).

For every assembled part (CPL), read the footprint instance from pcb/ts52k.kicad_pcb, undo the bottom flip and the
placement rotation in memory (the board is not saved) and record the numbered pads in front-side footprint
coordinates (mm, x right, y down).  The library footprint is loaded too and compared pad by pad, so the audit is
about the copper that is actually on the board.  Pin names come from the schematic netlist (pin function per pad).
Usage: python3 extract_board.py <repo-root> <out.json>
"""
import csv, json, sys
from pathlib import Path
import pcbnew

def kpad(p):
    return dict(number=p.GetNumber(), x=round(p.GetPosition().x / 1e6, 6), y=round(p.GetPosition().y / 1e6, 6),
                w=round(p.GetSize().x / 1e6, 6), h=round(p.GetSize().y / 1e6, 6),
                angle=round(p.GetOrientationDegrees(), 4), shape=p.GetShape(), attr=p.GetAttribute(),
                net=p.GetNetname(), pinfunction=p.GetPinFunction())

def libdir(root, lib):
    if lib in ("ts52k", "tc52", "tag-connect", "rp2040", "MX_Only"):
        return str(root / "pcb" / f"{lib}.pretty")
    return f"/usr/share/kicad/footprints/{lib}.pretty"

def normalized(fp):
    f = pcbnew.FOOTPRINT(fp)
    if f.IsFlipped():
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT if hasattr(pcbnew, "FLIP_DIRECTION_LEFT_RIGHT") else False)
    f.SetOrientationDegrees(0)
    f.SetPosition(pcbnew.VECTOR2I(0, 0))
    return [kpad(p) for p in f.Pads()]

def extract(root, refs=None):
    board = pcbnew.LoadBoard(str(root / "pcb" / "ts52k.kicad_pcb"))
    out = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if refs is not None and ref not in refs:
            continue
        fpid = fp.GetFPIDAsString()
        lib, name = fpid.split(":")
        d = libdir(root, lib)
        lf = pcbnew.FootprintLoad(d, name) if Path(d, name + ".kicad_mod").is_file() else None
        if lf is None:
            print("no library footprint:", ref, fpid, d)
        f_ = fp.GetField("LCSC") if hasattr(fp, "GetField") else None
        lcsc = f_.GetText() if f_ else ""
        out[ref] = dict(ref=ref, fpid=fpid, lcsc=lcsc, value=fp.GetValue(), bottom=fp.IsFlipped(),
                        x=fp.GetPosition().x / 1e6, y=fp.GetPosition().y / 1e6, angle=fp.GetOrientationDegrees(),
                        pads_normalized=normalized(fp),
                        lib_pads=[kpad(p) for p in lf.Pads()] if lf else None)
    return out

def main():
    root = Path(sys.argv[1]).resolve()
    cpl = list(csv.DictReader((root / "pcb/jlcpcb/assembly/ts52k-cpl.csv").open()))
    data = dict(board=extract(root, {r["Designator"] for r in cpl}))
    Path(sys.argv[2]).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(len(data["board"]), "board instances")
    for ref, inst in sorted(data["board"].items()):
        lp = inst["lib_pads"]
        same = lp is not None and len(lp) == len(inst["pads_normalized"]) and all(
            a["number"] == b["number"] and abs(a["x"] - b["x"]) < 1e-3 and abs(a["y"] - b["y"]) < 1e-3
            for a, b in zip(*(sorted(v, key=lambda q: (q["number"], q["x"], q["y"])) for v in (inst["pads_normalized"], lp))))
        if not same:
            print("board pads differ from the library footprint:", ref, inst["fpid"])

main()
