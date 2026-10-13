"""Coordonnées GPS des salles (pour le mode « Près de moi »).

Géocodage via le service d'adresses public de l'IGN (Géoplateforme), une seule fois par
salle : le résultat est gardé dans data/geo.json.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from .cinemas import Cinema

ENDPOINTS = ["https://data.geopf.fr/geocodage/search", "https://api-adresse.data.gouv.fr/search/"]


def clean_address(address: str) -> str:
    """« 128/162 avenue de France » → « 128 avenue de France » ; retire « , Niveau -3 »."""
    address = re.sub(r"^(\d+\s?(?:bis|ter)?)\s*[/-]\s*\d+", r"\1", address.strip())
    return address.split(",")[0].strip()


def parse_feature(data: dict, zipcode: str) -> tuple[float, float] | None:
    for f in data.get("features") or []:
        props = f.get("properties") or {}
        if props.get("postcode", zipcode)[:2] != "75" or (props.get("score") or 0) < 0.4:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        return round(lat, 5), round(lon, 5)
    return None


def geocode(cinema: Cinema, timeout: float = 10) -> tuple[float, float] | None:
    q = f"{clean_address(cinema.address)} {cinema.zipcode} Paris"
    for base in ENDPOINTS:
        url = f"{base}?{urllib.parse.urlencode({'q': q, 'limit': 1})}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                found = parse_feature(json.load(resp), cinema.zipcode)
        except Exception:  # service indisponible : on essaie le suivant
            continue
        if found:
            return found
    return None


def ensure_geo(cinemas: list[Cinema], cache_file: Path) -> dict[str, list[float]]:
    """Coordonnées {nom: [lat, lon]} ; ne géocode que les salles absentes du cache."""
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    missing = [c for c in cinemas if c.name not in cache]
    for c in missing:
        if found := geocode(c):
            cache[c.name] = list(found)
    if missing:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True))
    return cache
