import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from atlasrag.config import load_config, resolve
from atlasrag.ingest.arxiv_fetch import fetch_papers

ap = argparse.ArgumentParser()
ap.add_argument("--max-papers", type=int)
ap.add_argument("--keywords", nargs="*")
ap.add_argument("--date-from", help="YYYY-MM-DD (default: corpus.date_from in the config)")
ap.add_argument("--date-to", help="YYYY-MM-DD; with --date-from this samples one time WINDOW")
ap.add_argument("--sort", choices=["date", "relevance"], default="date",
                help="date = newest first; relevance = most on-topic first (use for older windows)")
args = ap.parse_args()

cfg = load_config()
c = cfg["corpus"]
n = fetch_papers(c["categories"],
                 args.keywords if args.keywords is not None else c["keywords"],
                 args.max_papers or c["max_papers"], args.date_from or c["date_from"],
                 resolve(c["raw_dir"]), c["request_delay_s"], date_to=args.date_to, sort=args.sort)
print(f"downloaded {n} new papers")
