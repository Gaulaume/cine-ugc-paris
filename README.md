# Ciné — Paris

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
- « Marquer déjà vu » sur la fiche d'un film : il disparaît de la liste (lien pour les réafficher),
  choix gardé sur le téléphone.
- Recherche : un film qui ne passe pas le jour choisi apparaît quand même, avec sa prochaine
  séance ; le toucher ouvre ce jour-là.
- Filtre « Fin avant 22 h / 23 h / minuit » (fin estimée, pubs comprises).

## Double séance, partage, calendrier
Vue « Par heure » d'un film : le bouton ⋯ d'une séance ouvre une feuille avec Réserver,
Partager, Ajouter au calendrier (fichier .ics avec rappel 45 min avant) et « Enchaîner un
2e film » : les films qui commencent après la fin estimée (jusqu'à 75 min d'attente), dans la
même salle puis le même arrondissement, en respectant les filtres et les films déjà vus.

## Découverte et envies
Bouton « 🎞 Découvrir » : les films à l'affiche défilent un par un (nouveautés d'abord) ;
glisser à droite ou ♥ = envie de voir, à gauche ou ✕ = pas pour moi, « ✓ vu » = déjà vu.
Filtre « ♥ Mes envies » et bouton « ♡ Envie de voir » sur la fiche du film.

## Rentabilité de la carte
Dans « Ma carte » : films marqués « Déjà vu » ce mois-ci × prix d'une place, comparé au prix
de la carte (21,90 € et 12 € par défaut, modifiables). Tout reste sur le téléphone.

## Apparence
Thème sombre « salle de cinéma » par défaut (bouton ◐ pour passer en clair), vue « Affiches »
(grille de 3 affiches avec note et badges) ou « Liste », fiche film avec l'affiche floutée en
fond. Choix mémorisés sur le téléphone.

## Ma carte
Bouton « 🎟 Ma carte » : on choisit une capture de sa carte UGC Illimité (et, si on veut, son
numéro). Elle est gardée **uniquement sur le téléphone** (IndexedDB du navigateur) : rien n'est
envoyé ni publié. Écran maintenu allumé pendant l'affichage. Raccourci : `…/#carte`.
