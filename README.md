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

## Mise en ligne (une seule fois)
Dans le dépôt GitHub : **Settings → Pages → Build and deployment → Source : « GitHub Actions »**.
Ensuite, chaque exécution du workflow « Mise à jour des séances » publie le site sur
`https://<compte>.github.io/cine-ugc-paris/`.

## Versions des séances
`VO` = film étranger en version originale (sous-titrée), `VF` = film doublé en français,
`FR` = film français. Le filtre « VO » garde tout sauf les films doublés ; « VF » garde
tout ce qui est en français.

## Réservation
Chaque séance porte son lien de réservation sur le site du cinéma (ugc.fr, mk2.com,
billetteries des indépendants), fourni par AlloCiné : toucher un horaire ouvre directement
la réservation de ce film à cette heure.

## Nouveautés
Le filtre « ✦ Nouveautés » garde les films sortis depuis 7 jours et ceux pas encore sortis
(avant-premières), du plus récent au plus ancien. Badge « Nouveau » / « Sortie mer. 21 oct. »
dans la liste ; les séances en avant-première portent la mention « Avant-première ».

## Confort
- Tri « les plus diffusés » ou « mieux notés » (note des spectateurs AlloCiné ; les films
  avec moins de 20 avis passent après), choix mémorisé. En « mieux notés », les sorties des
  3 derniers mois passent d'abord, puis les films plus anciens et les reprises.
- VO par défaut (cache seulement les films doublés), choix mémorisé ; séances passées masquées
  (lien pour les revoir) ; heure de fin estimée (film + 15 min de pubs).
- Lien « Itinéraire » Google Maps sur chaque salle.

## Ma carte
Bouton « 🎟 Ma carte » : on choisit une capture de sa carte UGC Illimité (et, si on veut, son
numéro). Elle est gardée **uniquement sur le téléphone** (IndexedDB du navigateur) : rien n'est
envoyé ni publié. Écran maintenu allumé pendant l'affichage. Raccourci : `…/#carte`.
