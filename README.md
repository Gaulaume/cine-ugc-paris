# Séances Illimité — Paris

Appli mobile (PWA) pour trouver **toutes les séances d'un film** dans les 59 cinémas
de Paris qui acceptent la carte **UGC Illimité** (UGC, MK2 et indépendants).

- Données : endpoints publics d'AlloCiné, rafraîchis 3×/jour par GitHub Actions.
- Site : GitHub Pages (`docs/`), installable sur l'écran d'accueil du téléphone.

## En local
```bash
pip install -r requirements.txt
python -m cineparis resolve      # associe les 59 salles à leurs codes AlloCiné
python -m cineparis scrape       # séances des 7 prochains jours -> docs/data/showtimes.json
python -m cineparis serve        # http://localhost:8000
python -m pytest -q
```

Liste des salles : `cineparis/cinemas.py` (source : ugc.fr/cinemas-acceptant-ui.html).
Si une salle est mal associée, force son code avec `allocine="C0XXX"`.
