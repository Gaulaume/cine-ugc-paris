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

## Jours incomplets
La semaine des cinémas commence le mercredi : avant, le programme du mercredi suivant n'est
publié que par quelques salles. Ces jours portent un point dans la barre des jours et un avis
dans la ligne d'état.

## Réservation
Chaque séance porte son lien de réservation sur le site du cinéma (ugc.fr, mk2.com,
billetteries des indépendants), fourni par AlloCiné : toucher un horaire ouvre directement
la réservation de ce film à cette heure.

## Nouveautés
Le filtre « ✦ Nouveautés » garde les films sortis depuis 7 jours et ceux pas encore sortis
(avant-premières), du plus récent au plus ancien. Badge « Nouveau » / « Sortie mer. 21 oct. »
dans la liste ; les séances en avant-première portent la mention « Avant-première ».

## Par cinéma
La recherche trouve aussi les salles (« danton », « mk2 », « champo »…). Chaque salle a sa
page (`#/salle/<code>`) : tous ses films du jour avec leurs horaires (filtres respectés, envies
d'abord), ★ pour l'ajouter à « Mes salles », liens Itinéraire et AlloCiné. Sur la fiche d'un
film, le nom d'une salle ouvre sa page.

## Filtres
Barre compacte : « 🎞 Découvrir », « Filtres » (pastille = nombre de filtres actifs), tri.
« Filtres » ouvre un panneau avec tout visible : version (VO/VF), sélection (Nouveautés,
Mes envies, Mes salles), fin de séance, enseigne, arrondissement ; « Voir N films » donne le
résultat en direct, « Réinitialiser » enlève tout. Les filtres actifs s'affichent en
étiquettes sous la barre, retirables d'un ✕.

## Confort
- Tri « les plus diffusés » ou « mieux notés » (note des spectateurs AlloCiné ; les films
  avec moins de 20 avis passent après), choix mémorisé. En « mieux notés », les sorties des
  3 derniers mois passent d'abord, puis les films plus anciens et les reprises.
- VO par défaut (cache seulement les films doublés), choix mémorisé ; séances passées masquées
  (lien pour les revoir) ; une séance reste réservable 20 min après l'heure affichée (pubs),
  avec la mention « a commencé » ; heure de fin estimée (film + 15 min de pubs).
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

Raccourcis sur chaque affiche de la liste : ♡ (envie de voir) et ✓ (déjà vu, avec un bandeau
« Annuler » pendant 5 s).

## Appli Android
Dossier `android/` : petite appli Android (WebView plein écran sur le site, donc toujours à jour).
Les réservations (ugc.fr, mk2.com, billetteries des indés) et AlloCiné s'ouvrent **dans Ciné**,
sous une barre aux couleurs de l'appli (film, salle, heure, site) : plus de passage par l'appli
UGC ni par le navigateur, et la connexion aux sites reste gardée. Sur la page de confirmation,
« 🎟 Garder le billet » enregistre l'écran (QR code) dans « Mes billets » (🎟 en haut de l'appli),
affiché en grand, écran à fond, pour l'entrée en salle. Letterboxd, Maps et l'agenda s'ouvrent
dans leur appli ; « Partager » utilise le menu d'Android. Le workflow « Appli Android » construit l'APK à chaque
changement de `android/` et le publie : https://github.com/Gaulaume/cine-ugc-paris/releases/latest/download/cine.apk
(clé de signature `android/cine.keystore`, fixe pour pouvoir installer les mises à jour par-dessus).

## Logo
Ticket de cinéma au style impression riso / comic (points de trame, couleurs légèrement
décalées), sur fond papier. Source : `scripts/logo-source.png` ; les icônes de `docs/icons/`
se régénèrent avec `python scripts/make_icons.py docs/icons` (nécessite Pillow).

## Ouverture instantanée
Le service worker (`docs/sw.js`) sert l'appli et les séances depuis la copie du téléphone,
puis les rafraîchit en arrière-plan ; quand de nouvelles séances arrivent, la page se met à
jour seule (« Séances mises à jour »). Hors ligne, la dernière copie reste utilisable. Les
polices ne bloquent plus l'affichage et les affiches se chargent au fil du défilement.

## Apparence
Thème sombre « salle de cinéma » par défaut (bouton ◐ pour passer en clair), vue « Affiches »
(grille de 3 affiches avec note et badges) ou « Liste », fiche film avec l'affiche floutée en
fond. Choix mémorisés sur le téléphone.

