"""Usage :
    python -m cineparis resolve        # retrouve les codes AlloCiné des salles
    python -m cineparis scrape --days 7  # récupère les séances -> docs/data/
    python -m cineparis serve          # site en local sur http://localhost:8000
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .cinemas import CINEMAS
from .core import match_cinemas, parse_results

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = DOCS / "data"
THEATERS_FILE = ROOT / "data" / "theaters.json"
PARIS = ZoneInfo("Europe/Paris")


def cmd_resolve(args) -> int:
    from .allocine import AllocineClient

    client = AllocineClient()
    theaters = client.paris_theaters()
    print(f"{len(theaters)} salles trouvées sur AlloCiné pour Paris")
    matched, missing = match_cinemas(CINEMAS, theaters)
    THEATERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    THEATERS_FILE.write_text(json.dumps(
        {"resolvedAt": datetime.now(PARIS).isoformat(timespec="seconds"),
         "matched": matched, "missing": missing, "allocine": theaters},
        ensure_ascii=False, indent=1))
    for name, t in sorted(matched.items()):
        print(f"  ✓ {name:38} → {t['id']:7} {t['name']}")
    for name in missing:
        print(f"  ✗ {name} (non trouvé — ajoute allocine='CODE' dans cinemas.py)")
    print(f"{len(matched)}/{len(CINEMAS)} salles associées → {THEATERS_FILE.relative_to(ROOT)}")
    return 0 if len(matched) >= len(CINEMAS) * 0.8 else 1


def cmd_scrape(args) -> int:
    from .allocine import AllocineClient

    if not THEATERS_FILE.exists() or args.resolve:
        cmd_resolve(args)
    resolved = json.loads(THEATERS_FILE.read_text())["matched"]
    # Les codes forcés dans cinemas.py priment sur la détection enregistrée.
    resolved.update({c.name: {"id": c.allocine, "name": c.name, "forced": True}
                     for c in CINEMAS if c.allocine})

    today = datetime.now(PARIS).date()
    days = [today + timedelta(days=i) for i in range(args.days)]
    theaters_out, movies, showtimes, errors = {}, {}, [], []

    def work(cinema):
        info = resolved.get(cinema.name)
        if not info:
            return cinema, None, [], "code AlloCiné inconnu"
        client = AllocineClient()
        per_day = []
        try:
            for d in days:
                per_day.append(client.showtimes(info["id"], d))
        except Exception as exc:  # une salle en erreur ne bloque pas les autres
            return cinema, info, per_day, str(exc)
        return cinema, info, per_day, None

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for cinema, info, per_day, err in pool.map(work, CINEMAS):
            key = info["id"] if info else cinema.name
            theaters_out[key] = {
                "name": cinema.name, "address": cinema.address, "zip": cinema.zipcode,
                "arr": cinema.arrondissement, "group": cinema.group,
                "allocine": f"https://www.allocine.fr/seance/salle_gen_csalle={info['id']}.html" if info else None,
            }
            for results in per_day:
                parse_results(results, key, movies, showtimes)
            status = "✗ " + err if err else f"✓ {sum(len(r) for r in per_day)} films·jour"
            print(f"  {cinema.name:38} {status}", flush=True)
            if err:
                errors.append({"cinema": cinema.name, "error": err})

    # Dédoublonnage + tri chronologique.
    showtimes = sorted({json.dumps(s): s for s in showtimes}.values(), key=lambda s: (s[2], s[1]))
    used = {s[0] for s in showtimes}
    movies = {k: v for k, v in movies.items() if k in used}

    if not showtimes:
        print("Aucune séance récupérée : je garde les données précédentes.", file=sys.stderr)
        return 1

    DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(PARIS).isoformat(timespec="seconds"),
        "days": [d.isoformat() for d in days],
        "theaters": theaters_out, "movies": movies, "showtimes": showtimes, "errors": errors,
    }
    (DATA / "showtimes.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    print(f"\n{len(showtimes)} séances · {len(movies)} films · {len(theaters_out)} salles "
          f"({len(errors)} en erreur) → docs/data/showtimes.json")
    return 0


def cmd_serve(args) -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS))
    print(f"→ http://localhost:{args.port}")
    http.server.ThreadingHTTPServer(("", args.port), handler).serve_forever()
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cineparis")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("resolve").set_defaults(func=cmd_resolve)
    s = sub.add_parser("scrape")
    s.add_argument("--days", type=int, default=7)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--resolve", action="store_true", help="refaire la détection des salles")
    s.set_defaults(func=cmd_scrape)
    v = sub.add_parser("serve")
    v.add_argument("--port", type=int, default=8000)
    v.set_defaults(func=cmd_serve)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
