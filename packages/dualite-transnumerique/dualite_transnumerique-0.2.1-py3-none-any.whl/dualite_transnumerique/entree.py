import gzip
import re
import secrets
from typing import List, Tuple

from . import erreur


Entrees = Tuple[List[int], List[int], List[int]]

LIGNE_RE = re.compile(r'([01]).*([01]).*([01])')


def _aleatoire(nb: int) -> List[int]:
    return [secrets.randbelow(2) for _ in range(nb)]


def aleatoire(nb: int) -> Entrees:
    resultats: Entrees = ([], [], [])
    for _ in range(nb):
        rand = secrets.randbelow(8)
        resultats[0].append(1 if rand & 1 else 0)
        resultats[1].append(1 if rand & 2 else 0)
        resultats[2].append(1 if rand & 4 else 0)
    return resultats


def fichier(chemin: str) -> Entrees:
    resultats: Entrees = ([], [], [])
    open_ = gzip.open if chemin.endswith('.gz') else open
    with open_(chemin, 'rt') as lignes:  # type: ignore
        for ligne in lignes:
            ligne = ligne.strip()
            if ligne != '':
                colonnes = LIGNE_RE.match(ligne)
                if colonnes is None:
                    raise erreur.Erreur(
                        "Fichier invalide: une ligne n'a pas 3 chiffres séparé par des virgules")
                for i, colonne in enumerate(colonnes.groups()):
                    entier = int(colonne)
                    resultats[i].append(entier)
    return resultats
