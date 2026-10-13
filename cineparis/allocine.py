"""Petit client pour les endpoints publics d'AlloCiné.

On imite un vrai navigateur (curl_cffi) : AlloCiné filtre les clients HTTP
« nus ». On reste poli : une requête à la fois, avec une petite pause.
"""

from __future__ import annotations

import html
import json
import re
import time
from datetime import date

from curl_cffi import requests

BASE = "https://www.allocine.fr"
PARIS_GEOCODE = 115755  # « ville-115755 » = Paris sur AlloCiné


class AllocineClient:
    def __init__(self, delay: float = 0.4, retries: int = 4):
        self.session = requests.Session(impersonate="chrome")
        self.delay = delay
        self.retries = retries

    def _get(self, url: str, params: dict | None = None) -> requests.Response:
        for attempt in range(self.retries):
            time.sleep(self.delay)
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            return resp
        resp.raise_for_status()
        return resp

    # --- Salles -----------------------------------------------------------
    def paris_theaters(self) -> list[dict]:
        """Toutes les salles listées par AlloCiné pour Paris (toutes pages)."""
        theaters: dict[str, dict] = {}
        page = 1
        while True:
            params = {"page": page} if page > 1 else None
            resp = self._get(f"{BASE}/salle/cinema/ville-{PARIS_GEOCODE}/", params)
            resp.raise_for_status()
            found = parse_theater_cards(resp.text)
            new = [t for t in found if t["id"] not in theaters]
            for t in found:
                theaters[t["id"]] = t
            if not new or page >= 30:
                break
            page += 1
        return list(theaters.values())

    # --- Séances ----------------------------------------------------------
    def showtimes(self, theater_id: str, day: date) -> list[dict]:
        """Résultats bruts (films + séances) d'une salle pour un jour donné."""
        results: list[dict] = []
        page = 1
        while True:
            url = f"{BASE}/_/showtimes/theater-{theater_id}/d-{day.isoformat()}/"
            if page > 1:
                url += f"p-{page}/"
            resp = self._get(url)
            if resp.status_code == 404:
                return results
            resp.raise_for_status()
            data = resp.json()
            if data.get("error"):
                return results  # "no.showtime.error" / "next.showtime.on"
            results.extend(data.get("results") or [])
            total = (data.get("pagination") or {}).get("totalPages") or 1
            if page >= total:
                return results
            page += 1


_CARD_RE = re.compile(r'data-theater="([^"]+)"')
_ADDR_RE = re.compile(r'<address[^>]*>(.*?)</address>', re.S)


def parse_theater_cards(page_html: str) -> list[dict]:
    """Extrait {id, name, address, zipcode} des cartes « theater-card »."""
    out = []
    chunks = page_html.split('theater-card')
    for chunk in chunks[1:]:
        m = _CARD_RE.search(chunk)
        if not m:
            continue
        try:
            data = json.loads(html.unescape(m.group(1)))
        except json.JSONDecodeError:
            continue
        tid = data.get("id") or data.get("internalId")
        if not tid or not data.get("name"):
            continue
        address = ""
        if a := _ADDR_RE.search(chunk):
            address = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(a.group(1))).split())
        z = re.search(r"\b75\d{3}\b", address)
        out.append({
            "id": str(tid),
            "name": html.unescape(data["name"]),
            "address": address,
            "zipcode": z.group() if z else "",
        })
    return out
