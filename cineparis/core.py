"""Association des salles UGC Illimité aux codes AlloCiné, et mise en forme des séances."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from .cinemas import Cinema

# Mots qui n'aident pas à distinguer deux salles.
_STOP = {"le", "la", "les", "l", "de", "des", "du", "d", "cinema", "cinemas",
         "the", "et", "salle", "paris", "club", "espace", "panorama", "palais"}

_SYNONYMS = {"st": "saint", "ste": "sainte", "fg": "faubourg", "fbg": "faubourg",
             "ugc": "ugc", "mk2": "mk2", "cine": "cine", "cite": "cite"}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    words = re.sub(r"[^a-z0-9]+", " ", text).split()
    return " ".join(_SYNONYMS.get(w, w) for w in words)


def _tokens(text: str) -> set[str]:
    return {w for w in normalize(text).split() if w not in _STOP}


def similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    jaccard = len(ta & tb) / len(ta | tb)
    contain = len(ta & tb) / min(len(ta), len(tb))
    seq = SequenceMatcher(None, normalize(a), normalize(b)).ratio()
    return 0.45 * contain + 0.35 * jaccard + 0.20 * seq


def match_cinemas(cinemas: list[Cinema], allocine: list[dict], min_score: float = 0.55):
    """Retourne ({nom_ugc: theater_allocine}, [noms non trouvés]).

    Chaque salle AlloCiné n'est attribuée qu'une fois, au meilleur score, et
    on exige le même code postal quand AlloCiné le fournit (évite de confondre
    « MK2 Odéon » et « UGC Odéon »).
    """
    candidates = []
    for c in cinemas:
        if c.allocine:
            continue
        for t in allocine:
            if t.get("zipcode") and t["zipcode"] != c.zipcode:
                continue
            # Une salle UGC ne peut correspondre qu'à une salle « UGC », idem MK2.
            tnorm = normalize(t["name"])
            if c.group in ("UGC", "MK2") and c.group.lower() not in tnorm.split():
                continue
            if c.group == "Indépendant" and ({"ugc", "mk2"} & set(tnorm.split())):
                continue
            score = similarity(c.name, t["name"])
            # Bonus si le numéro de rue apparaît dans l'adresse AlloCiné.
            num = re.match(r"\d+", c.address)
            if num and t.get("address") and re.search(rf"\b{num.group()}\b", t["address"]):
                score += 0.15
            if score >= min_score:
                candidates.append((score, c.name, t))

    matched: dict[str, dict] = {}
    used: set[str] = set()
    for c in cinemas:
        if c.allocine:
            matched[c.name] = {"id": c.allocine, "name": c.name, "forced": True}
            used.add(c.allocine)
    for score, name, t in sorted(candidates, key=lambda x: -x[0]):
        if name in matched or t["id"] in used:
            continue
        matched[name] = {**t, "score": round(score, 3)}
        used.add(t["id"])
    missing = [c.name for c in cinemas if c.name not in matched]
    return matched, missing


# --- Séances ---------------------------------------------------------------

def _version(raw: dict, movie: dict) -> str:
    """« VO » (film étranger en version originale), « VF » (doublé) ou « FR » (film français).

    AlloCiné : diffusionVersion vaut ORIGINAL, DUBBED (doublé) ou LOCAL (film français).
    """
    # La langue du film d'abord : AlloCiné marque parfois « DUBBED » des films français.
    langs = movie.get("languages") or []
    dv = raw.get("diffusionVersion")
    if langs[:1] == ["FRENCH"] or (not langs and dv == "LOCAL"):
        return "FR"
    if dv in ("DUBBED", "LOCAL") or "Localization.Language.French" in (raw.get("tags") or []):
        return "VF"
    return "VO"


def _formats(raw: dict) -> list[str]:
    labels = {"IMAX": "IMAX", "F_3D": "3D", "E_4DX": "4DX", "SCREENX": "ScreenX",
              "DOLBY_CINEMA": "Dolby Cinema", "PLF": "Grand écran", "INFINITE": "Infinite",
              "E_SCREENX": "ScreenX", "SCREEN_X": "ScreenX", "4DX": "4DX", "F_70MM": "70mm",
              "F_35MM": "35mm", "DOLBY_ATMOS": "Atmos"}
    out = []
    for key in ("experience", "projection", "sound", "picture"):
        for v in raw.get(key) or []:
            if v in labels and labels[v] not in out:
                out.append(labels[v])
    return out


def _poster(movie: dict) -> str | None:
    return (movie.get("poster") or {}).get("url")


def parse_results(results: list[dict], theater_key: str, movies: dict, showtimes: list):
    """Ajoute les films et séances d'une réponse AlloCiné aux structures communes."""
    for item in results:
        movie = item.get("movie")
        if not movie or not movie.get("internalId"):
            continue
        mid = str(movie["internalId"])
        if mid not in movies:
            directors = [
                " ".join(filter(None, [(c.get("person") or {}).get("firstName"),
                                       (c.get("person") or {}).get("lastName")]))
                for c in movie.get("credits") or []
                if ((c.get("position") or {}).get("name") == "DIRECTOR")
            ]
            rating = ((movie.get("stats") or {}).get("userRating") or {}).get("score")
            movies[mid] = {
                "title": movie.get("title") or "",
                "original": movie.get("originalTitle") or "",
                "poster": _poster(movie),
                "runtime": movie.get("runtime") or "",
                "genres": [g.get("translate") for g in movie.get("genres") or [] if g.get("translate")],
                "directors": [d for d in directors if d][:2],
                "rating": round(float(rating), 1) if isinstance(rating, (int, float)) else None,
            }
        for group in (item.get("showtimes") or {}).values():
            for raw in group or []:
                starts = raw.get("startsAt")
                if not starts:
                    continue
                showtimes.append([mid, theater_key, starts[:16], _version(raw, movie), _formats(raw)])
