"""Cinémas de Paris intra-muros acceptant la carte UGC Illimité.

Source : https://www.ugc.fr/cinemas-acceptant-ui.html (relevé du 13/10/2026).
La liste évolue : mets-la à jour ici si UGC ajoute ou retire une salle.

`allocine` permet de forcer le code AlloCiné d'une salle si la détection
automatique se trompe (voir `python -m cineparis resolve`).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Cinema:
    name: str
    address: str
    zipcode: str
    group: str  # "UGC", "MK2" ou "Indépendant"
    allocine: str | None = None

    @property
    def arrondissement(self) -> int:
        return int(self.zipcode[-2:])


def _c(name, address, zipcode, group, allocine=None):
    return Cinema(name, address, zipcode, group, allocine)


CINEMAS: list[Cinema] = [
    # --- UGC ---
    _c("UGC Ciné Cité Les Halles", "Forum des Halles, Niveau -3", "75001", "UGC"),
    _c("UGC Ciné Cité Bercy", "2 cour Saint-Émilion", "75012", "UGC"),
    _c("UGC Ciné Cité Maillot", "2 place de la Porte Maillot", "75017", "UGC"),
    _c("UGC Montparnasse", "83 boulevard du Montparnasse", "75006", "UGC"),
    _c("UGC Rotonde", "103 boulevard du Montparnasse", "75006", "UGC"),
    _c("UGC Odéon", "124 boulevard Saint-Germain", "75006", "UGC"),
    _c("UGC Danton", "99 boulevard Saint-Germain", "75006", "UGC"),
    _c("UGC Lyon Bastille", "12 rue de Lyon", "75012", "UGC"),
    _c("UGC Gobelins", "66 bis avenue des Gobelins", "75013", "UGC"),
    _c("UGC Opéra", "32 boulevard des Italiens", "75009", "UGC"),
    _c("UGC Ciné Cité Paris 19", "166 boulevard Macdonald", "75019", "UGC"),
    # --- MK2 ---
    _c("MK2 Beaubourg", "50 rue Rambuteau", "75003", "MK2"),
    _c("MK2 Odéon (côté St Germain)", "113 boulevard Saint-Germain", "75006", "MK2"),
    _c("MK2 Odéon (côté St Michel)", "7 rue Hautefeuille", "75006", "MK2"),
    _c("MK2 Parnasse", "11 rue Jules Chaplain", "75006", "MK2"),
    _c("MK2 Bastille (côté Beaumarchais)", "4 boulevard Beaumarchais", "75011", "MK2"),
    _c("MK2 Bastille (côté Fg St Antoine)", "5 rue du Faubourg Saint-Antoine", "75011", "MK2"),
    _c("MK2 Nation", "133 boulevard Diderot", "75012", "MK2"),
    _c("MK2 Bibliothèque", "128/162 avenue de France", "75013", "MK2"),
    _c("MK2 Quai de Loire", "7 quai de la Loire", "75019", "MK2"),
    _c("MK2 Quai de Seine", "14 quai de la Seine", "75019", "MK2"),
    _c("MK2 Gambetta", "6 rue Belgrand", "75020", "MK2"),
    # --- Indépendants ---
    _c("Le Grand Rex", "1 boulevard Poissonnière", "75002", "Indépendant"),
    _c("Luminor Hôtel de Ville", "20 rue du Temple", "75004", "Indépendant"),
    _c("Cinéma du Panthéon", "13 rue Victor Cousin", "75005", "Indépendant"),
    _c("Écoles Cinéma Club", "25 rue des Écoles", "75005", "Indépendant"),
    _c("L'Épée de Bois", "100 rue Mouffetard", "75005", "Indépendant"),
    _c("Espace Saint-Michel", "7 place Saint-Michel", "75005", "Indépendant"),
    _c("La Filmothèque du Quartier Latin", "9 rue Champollion", "75005", "Indépendant"),
    _c("Le Champo", "51 rue des Écoles", "75005", "Indépendant"),
    _c("Le Grand Action", "5 rue des Écoles", "75005", "Indépendant"),
    _c("Le Reflet Médicis", "3/7 rue Champollion", "75005", "Indépendant"),
    _c("Studio Galande", "42 rue Galande", "75005", "Indépendant"),
    _c("Studio des Ursulines", "10 rue des Ursulines", "75005", "Indépendant"),
    _c("Christine Cinéma Club", "4 rue Christine", "75006", "Indépendant"),
    _c("L'Arlequin", "76 rue de Rennes", "75006", "Indépendant"),
    _c("Le Lucernaire", "53 rue Notre-Dame-des-Champs", "75006", "Indépendant"),
    _c("Le Nouvel Odéon", "6 rue de l'École de Médecine", "75006", "Indépendant"),
    _c("Le Saint-André des Arts", "30 rue Saint-André-des-Arts", "75006", "Indépendant"),
    _c("Les 3 Luxembourg", "67 rue Monsieur-le-Prince", "75006", "Indépendant"),
    _c("Le Saint-Germain-des-Prés", "22 rue Guillaume Apollinaire", "75006", "Indépendant"),
    _c("Jeu de Paume", "1 place de la Concorde", "75008", "Indépendant"),
    _c("Le Balzac", "1 rue Balzac", "75008", "Indépendant"),
    _c("Le Lincoln", "14 rue Lincoln", "75008", "Indépendant"),
    _c("Publicis Cinémas", "133 avenue des Champs-Élysées", "75008", "Indépendant"),
    _c("5 Caumartin", "101 rue Saint-Lazare", "75009", "Indépendant"),
    _c("Max Linder Panorama", "24 boulevard Poissonnière", "75009", "Indépendant"),
    _c("L'Archipel", "17 boulevard de Strasbourg", "75010", "Indépendant"),
    _c("Le Brady", "39 boulevard de Strasbourg", "75010", "Indépendant"),
    _c("Le Louxor", "170 boulevard de Magenta", "75010", "Indépendant"),
    _c("Majestic Bastille", "4 boulevard Richard-Lenoir", "75011", "Indépendant"),
    _c("L'Escurial", "11 boulevard de Port-Royal", "75013", "Indépendant"),
    _c("L'Entrepôt", "7 rue Francis de Pressensé", "75014", "Indépendant"),
    _c("Les 7 Parnassiens", "98 boulevard du Montparnasse", "75014", "Indépendant"),
    _c("Chaplin Denfert", "24 place Denfert-Rochereau", "75014", "Indépendant"),
    _c("Chaplin Saint-Lambert", "6 rue Péclet", "75015", "Indépendant"),
    _c("Majestic Passy", "18 rue de Passy", "75016", "Indépendant"),
    _c("Cinéma des Cinéastes", "7 avenue de Clichy", "75017", "Indépendant"),
    _c("Mac-Mahon", "5 avenue Mac-Mahon", "75017", "Indépendant"),
]
