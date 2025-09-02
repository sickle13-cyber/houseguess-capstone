# haytham: CLI to test the API without running the GUI
from __future__ import annotations
import argparse, json
from houseguess.api_client import nominatim_search, rapidapi_search

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["nominatim", "rapidapi"], default="nominatim")  # haytham
    ap.add_argument("--query", required=True)                                             # haytham
    ap.add_argument("--limit", type=int, default=5)                                       # haytham
    ap.add_argument("--param", action="append", default=[], help="extra key=value (repeat)")  # haytham
    ap.add_argument("--dump", help="write results to JSON")                                # haytham
    args = ap.parse_args()

    extra = {}
    for kv in args.param:
        if "=" in kv:
            k, v = kv.split("=", 1)
            extra[k] = v

    if args.provider == "nominatim":
        places = nominatim_search(args.query, limit=args.limit)
    else:
        places = rapidapi_search(args.query, limit=args.limit, extra_params=extra)

    print(f"Found {len(places)} result(s).")
    for i, p in enumerate(places, 1):
        print(f"{i}. {p.label()} @ {p.lat:.5f},{p.lon:.5f} src={p.source}")

    if args.dump:
        with open(args.dump, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in places], f, indent=2, ensure_ascii=False)
        print(f"wrote {args.dump}")

if __name__ == "__main__":
    main()
