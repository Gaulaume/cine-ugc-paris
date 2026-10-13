from cineparis.cinemas import Cinema
from cineparis.geo import clean_address, ensure_geo, parse_feature


def test_nettoyage_adresse():
    assert clean_address("128/162 avenue de France") == "128 avenue de France"
    assert clean_address("3/7 rue Champollion") == "3 rue Champollion"
    assert clean_address("Forum des Halles, Niveau -3") == "Forum des Halles"
    assert clean_address("66 bis avenue des Gobelins") == "66 bis avenue des Gobelins"


def test_lecture_reponse():
    data = {"features": [{"geometry": {"coordinates": [2.38612, 48.83321]},
                          "properties": {"postcode": "75012", "score": 0.93}}]}
    assert parse_feature(data, "75012") == (48.83321, 2.38612)
    assert parse_feature({"features": []}, "75012") is None


def test_cache_sans_reseau(tmp_path, monkeypatch):
    cache = tmp_path / "geo.json"
    cache.write_text('{"UGC Bercy": [48.8, 2.38]}')
    monkeypatch.setattr("cineparis.geo.geocode", lambda c: (48.9, 2.3))
    out = ensure_geo([Cinema("UGC Bercy", "x", "75012", "UGC"), Cinema("Neuf", "y", "75001", "UGC")], cache)
    assert out == {"UGC Bercy": [48.8, 2.38], "Neuf": [48.9, 2.3]}
