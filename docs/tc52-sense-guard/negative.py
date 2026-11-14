#!/usr/bin/env python3
"""negative.py : negative examples for check_spec item 6b (ground guard beside SENSE / AMP_IN / AMP_FB).

Each case copies pcb/ts52k.kicad_pcb to /tmp, adds a little copper with pcbnew, saves the copy and runs
  - the new checker   : pcb/tc52-build/check_spec.py <copy>
  - the old checker   : check_spec.py of commit OLD, run in a throw-away git worktree whose board file is the copy
The real board file is only read.  Usage (from the repo root): python3 docs/tc52-sense-guard/negative.py
"""
import os, subprocess, sys, shutil
import pcbnew
ROOT = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
BOARD = os.path.join(ROOT, 'pcb', 'ts52k.kicad_pcb')
OLD = '3367699'                         # check_spec.py before item 6b
WT = '/tmp/tc52-guard-old-wt'
MM = pcbnew.FromMM

def track(b, net, x1, y1, x2, y2, w, layer=pcbnew.B_Cu):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t)

def via(b, net, x, y):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.2))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(b.FindNet(net)); b.Add(v)

# (A via with no track at all is given the net of the GND pour around it when the copy is saved, hence the stub.)
# SENSE trunk on L4: (0.0, 118.4) - (221.5, 118.4), 0.2 mm.  AMP_IN / AMP_FB are short runs at the op amp.
CASES = {
    'N1 ROW1_DRV track 1.0 mm from SENSE, no guard (the wireless audit 2-1 pattern)':
        (lambda b: track(b, 'ROW1_DRV', 100, 117.4, 110, 117.4, 0.15), 'FAIL'),
    'N2 = N1 plus a GND track between the two (guard present)':
        (lambda b: (track(b, 'ROW1_DRV', 100, 117.4, 110, 117.4, 0.15), track(b, 'GND', 99, 117.9, 111, 117.9, 0.2)), 'ok'),
    'N3 ROW2_DRV via 0.9 mm from SENSE (centre); its only track is an L1 stub, so on L4 there is just the via':
        (lambda b: (via(b, 'ROW2_DRV', 120, 117.5), track(b, 'ROW2_DRV', 120, 117.5, 120, 115.0, 0.25, pcbnew.F_Cu)), 'FAIL'),
    'N4 ROW4 (row side of the resistor) track 1.2 mm from SENSE':
        (lambda b: track(b, 'ROW4', 180, 117.2, 186, 117.2, 0.25), 'FAIL'),
}

def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout

def main():
    subprocess.run(['git', 'worktree', 'remove', '--force', WT], cwd=ROOT, capture_output=True)
    subprocess.check_call(['git', 'worktree', 'add', '--detach', WT, OLD], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = True
    try:
        for name, (mod, want) in CASES.items():
            b = pcbnew.LoadBoard(BOARD)
            mod(b)
            cp = '/tmp/tc52-guard-neg.kicad_pcb'
            pcbnew.SaveBoard(cp, b)
            rc, out = run([sys.executable, os.path.join(ROOT, 'pcb/tc52-build/check_spec.py'), cp], ROOT)
            lines = out.splitlines()
            i = [k for k, l in enumerate(lines) if 'ground guard between SENSE' in l][0]
            got = 'ok' if lines[i].startswith('ok') else 'FAIL'
            fails = [l for l in lines if l.startswith('FAIL')]
            shutil.copy(cp, os.path.join(WT, 'pcb', 'ts52k.kicad_pcb'))
            orc, oout = run([sys.executable, 'pcb/tc52-build/check_spec.py'], WT)
            ofail = [l for l in oout.splitlines() if l.startswith('FAIL')]
            print('==', name)
            print('   new check_spec: item 6b', got, '(expected', want + ')', '| exit', rc, '| FAIL lines', len(fails))
            for l in lines[i:i + 1 + min(4, len(lines) - i - 1)]:
                print('     |', l)
            print('   old check_spec (%s): exit %d, FAIL lines %d%s' % (OLD, orc, len(ofail), ''.join('\n     | ' + l for l in ofail)))
            ok &= (got == want) and (rc == (1 if want == 'FAIL' else 0)) and len(fails) == (1 if want == 'FAIL' else 0)
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', WT], cwd=ROOT, capture_output=True)
        subprocess.run(['git', 'worktree', 'prune'], cwd=ROOT, capture_output=True)
    print('ALL CASES AS EXPECTED' if ok else 'SOME CASE NOT AS EXPECTED')
    sys.exit(0 if ok else 1)

main()
