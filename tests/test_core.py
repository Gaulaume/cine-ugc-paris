import json
from pathlib import Path

from cineparis.allocine import parse_theater_cards
from cineparis.cinemas import CINEMAS
from cineparis.core import match_cinemas, parse_results

FIX = Path(__file__).parent / "fixtures"

# Noms tels qu'AlloCiné a l'habitude de les écrire (différents de la liste UGC).
ALLOCINE_LIKE = [
    {"id": "C0159", "name": "UGC Ciné Cité Les Halles", "zipcode": "75001", "address": "7 place de la Rotonde 75001 Paris"},
    {"id": "C0097", "name": "UGC Odéon", "zipcode": "75006", "address": "124 bd Saint-Germain 75006 Paris"},
    {"id": "C0089", "name": "Max Linder Panorama", "zipcode": "75009", "address": "24 bd Poissonnière 75009 Paris"},
    {"id": "C0093", "name": "Le Champo - Espace Jacques Tati", "zipcode": "75005", "address": "51 rue des Ecoles 75005 Paris"},
    {"id": "C0071", "name": "Écoles Cinéma Club", "zipcode": "75005", "address": "23 rue des Ecoles 75005 Paris"},
    {"id": "C0095", "name": "Le Grand Action", "zipcode": "75005", "address": "5 rue des Ecoles 75005 Paris"},
    {"id": "C1621", "name": "mk2 Odéon (côté St Michel)", "zipcode": "75006", "address": "7 rue Hautefeuille 75006 Paris"},
    {"id": "C0116", "name": "mk2 Odéon (côté St Germain)", "zipcode": "75006", "address": "113 bd St-Germain 75006 Paris"},
    {"id": "C0140", "name": "Gaumont Opéra", "zipcode": "75009", "address": "2 bd des Capucines 75009 Paris"},
    {"id": "C0179", "name": "Pathé Wepler", "zipcode": "75018", "address": "140 bd de Clichy 75018 Paris"},
]


def test_liste_complete():
    assert len(CINEMAS) == 59
    assert len({c.name for c in CINEMAS}) == 59


def test_association_des_salles():
    matched, _ = match_cinemas(CINEMAS, ALLOCINE_LIKE)
    assert matched["UGC Ciné Cité Les Halles"]["id"] == "C0159"
    assert matched["UGC Odéon"]["id"] == "C0097"
    assert matched["Max Linder Panorama"]["id"] == "C0089"
    assert matched["Le Champo"]["id"] == "C0093"
    assert matched["Écoles Cinéma Club"]["id"] == "C0071"
    assert matched["Le Grand Action"]["id"] == "C0095"
    assert matched["MK2 Odéon (côté St Michel)"]["id"] == "C1621"
    assert matched["MK2 Odéon (côté St Germain)"]["id"] == "C0116"
    # Les salles hors carte UGC (Gaumont, Pathé) ne sont jamais associées.
    assert {"C0140", "C0179"}.isdisjoint(t["id"] for t in matched.values())


def test_parse_seances():
    data = json.loads((FIX / "showtimes_sample.json").read_text())
    movies, shows = {}, []
    parse_results(data["results"], "C0159", movies, shows)
    assert movies["1001"]["title"] == "Film Test"
    assert movies["1001"]["directors"] == ["Jane Doe"]
    assert movies["1001"]["rating"] == 4.1
    assert shows[0][:4] == ["1001", "C0159", "2026-10-13T14:00", "VO"]
    assert shows[1][3] == "VF"
    assert set(shows[1][4]) == {"IMAX", "3D"}
    assert len(shows) == 2
    assert shows[0][5] == "https://example.test/ticket/1"


def test_parse_cartes_salles():
    page = '''<div class="card theater-card"><span class="add-theater-anchor"
      data-theater="{&quot;id&quot;:&quot;C0159&quot;,&quot;name&quot;:&quot;UGC Ciné Cité Les Halles&quot;}"></span>
      <address class="address">7 place de la Rotonde <span>75001 Paris</span></address></div>'''
    cards = parse_theater_cards(page)
    assert cards == [{"id": "C0159", "name": "UGC Ciné Cité Les Halles",
                      "address": "7 place de la Rotonde 75001 Paris", "zipcode": "75001"}]


def test_version_film_francais():
    film = {"internalId": 7, "title": "Garance", "languages": ["FRENCH"]}
    results = [{"movie": film, "showtimes": {
        "original": [{"startsAt": "2026-10-13T10:00:00", "diffusionVersion": "ORIGINAL"}],
        "multiple": [{"startsAt": "2026-10-13T12:00:00", "diffusionVersion": "LOCAL",
                      "experience": ["INFINITE"]},
                     {"startsAt": "2026-10-13T14:00:00", "diffusionVersion": "DUBBED"}]}}]
    movies, shows = {}, []
    parse_results(results, "C0102", movies, shows)
    assert [s[3] for s in shows] == ["FR", "FR", "FR"]
    assert shows[1][4] == ["Infinite"]


def test_lien_reservation_sans_pistage():
    raw = {"startsAt": "2026-10-14T09:00:00", "data": {"ticketing": [
        {"provider": "relay", "urls": ["https://relay.mvtx.us/ticketing/x"]},
        {"provider": "default", "urls": ["https://www.ugc.fr/reservationSeances.html?id=33&part=all&mtm_source=allocine&mtm_medium=affiliate"]}]}}
    movies, shows = {}, []
    parse_results([{"movie": {"internalId": 1, "title": "X"}, "showtimes": {"original": [raw]}}], "C0159", movies, shows)
    assert shows[0][5] == "https://www.ugc.fr/reservationSeances.html?id=33&part=all"
