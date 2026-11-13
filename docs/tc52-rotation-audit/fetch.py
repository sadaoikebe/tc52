"""Fetch the JLCPCB/LCSC side of the rotation audit for every LCSC part in the BOM.

  raw/<C>-components.json  GET https://easyeda.com/api/products/<C>/components  (EasyEDA symbol + footprint, numbered lands)
  raw/<C>-svgs.json        GET https://easyeda.com/api/products/<C>/svgs        (the data behind JLCPCB's footprint viewer)
  raw/<C>-lcsc.json        GET https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<C>  (model, maker, package)
Writes fetch-log.json (URL, date, size, SHA-256, HTTP result).  Retries with a pause on 403/429 (rate limit).
Usage: python3 -I fetch.py
"""
import csv, datetime, hashlib, json, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = HERE / "raw"
URLS = {"components": "https://easyeda.com/api/products/{}/components",
        "svgs": "https://easyeda.com/api/products/{}/svgs",
        "lcsc": "https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={}"}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (rotation-audit)", "Accept": "application/json"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 5:
                time.sleep(10 * (attempt + 1))
                continue
            return e.code, e.read()
        except Exception as e:
            if attempt < 5:
                time.sleep(5)
                continue
            return None, str(e).encode()

RAW.mkdir(exist_ok=True)
parts = [r["LCSC Part #"] for r in csv.DictReader((ROOT / "pcb/jlcpcb/assembly/ts52k-bom.csv").open())]
log = []
for part in parts:
    for kind, url in URLS.items():
        url = url.format(part)
        status, body = get(url)
        ok = status == 200
        if ok:
            try:
                j = json.loads(body)
                ok = bool(j.get("result")) and j.get("success", True) is not False
            except Exception:
                ok = False
        if ok:
            (RAW / f"{part}-{kind}.json").write_bytes(body)
        log.append(dict(part=part, kind=kind, url=url, fetched=datetime.date.today().isoformat(), http=status, ok=ok,
                        bytes=len(body), sha256=hashlib.sha256(body).hexdigest()))
        print(part, kind, status, ok, len(body))
        time.sleep(1.5)
(HERE / "fetch-log.json").write_text(json.dumps(log, indent=1) + "\n")
