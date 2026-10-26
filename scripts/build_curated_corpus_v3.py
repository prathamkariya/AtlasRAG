"""Build exact v3 metadata/PDF set from v2 inventory plus three arXiv records."""
import json, shutil, time, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = "2609.13266v1"
ADD = ("2510.23823", "2610.14781", "2604.08530")
NS = {"a": "http://www.w3.org/2005/Atom"}

def fetch(arxiv_id):
    with urllib.request.urlopen(f"https://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=60) as r:
        entry = ET.fromstring(r.read()).find("a:entry", NS)
    if entry is None: raise RuntimeError(f"arXiv ID not resolved: {arxiv_id}")
    ident = entry.findtext("a:id", namespaces=NS).rsplit("/", 1)[-1]
    return {"id": ident, "title": " ".join(entry.findtext("a:title", namespaces=NS).split()),
            "abstract": " ".join(entry.findtext("a:summary", namespaces=NS).split()),
            "published": entry.findtext("a:published", namespaces=NS),
            "pdf_url": f"https://arxiv.org/pdf/{ident}.pdf"}

def main():
    src = ROOT / "data/raw_v2/metadata.jsonl"; out = ROOT / "data/raw_v3"; pdf = out / "pdf"
    records = [json.loads(x) for x in src.read_text(encoding="utf8").splitlines() if x]
    if len(records) != len({x["id"] for x in records}): raise RuntimeError("v2 duplicate IDs")
    records = [x for x in records if x["id"] != EXCLUDE]
    base_ids = {x["id"].split("v")[0] for x in records}
    for ident in ADD:
        if ident not in base_ids: records.append(fetch(ident)); time.sleep(3)
    if len(records) != 121 or len({x["id"] for x in records}) != 121: raise RuntimeError(f"expected 121 unique records, got {len(records)}")
    out.mkdir(parents=True, exist_ok=True); pdf.mkdir(exist_ok=True)
    (out / "metadata.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False)+"\n" for x in sorted(records,key=lambda x:x["id"])), encoding="utf8")
    for x in records:
        target=pdf/f"{x['id']}.pdf"; candidates=[ROOT/"data/raw/pdf"/target.name, ROOT/"data/raw_v2/pdf"/target.name]
        source=next((p for p in candidates if p.exists()), None)
        if source: shutil.copy2(source,target)
        elif not target.exists(): urllib.request.urlretrieve(x["pdf_url"],target); time.sleep(3)
    missing=[x["id"] for x in records if not (pdf/f"{x['id']}.pdf").exists()]
    if missing: raise RuntimeError(f"missing PDFs: {missing}")
    print(f"wrote {len(records)} records and PDFs to {out}")
if __name__ == "__main__": main()
