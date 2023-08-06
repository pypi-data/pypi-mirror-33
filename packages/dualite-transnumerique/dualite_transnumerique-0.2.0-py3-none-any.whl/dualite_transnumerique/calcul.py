from typing import List, Tuple

from . import acces, algo, erreur


def calcul(base: List[int], secteur_debut: int, secteur_fin: int, comparo_debut: int, comparo_fin: int,
           formule_delta: List[int]) -> Tuple[int, int]:
    if secteur_debut < 1:
        raise erreur.Erreur("Le début du secteur de base doit être plus grand que 0")
    if secteur_fin <= secteur_debut:
        raise erreur.Erreur("La fin du secteur de base doit être plus grand que le début")
    if secteur_fin > len(base):
        raise erreur.Erreur("La fin du secteur de base doit être plus petit ou égale au nombre d'entrées")

    if comparo_fin < comparo_debut:
        raise erreur.Erreur("La fin des comparos doit être plus grand ou égale au début")

    if len(formule_delta) != 4:
        raise erreur.Erreur("Il faut 4 chiffres pour la formule delta")
    for i in range(3):
        if formule_delta[i] >= formule_delta[i + 1]:
            raise erreur.Erreur(
                f"L'entrée N°{i+2} de la formule delta doit être plus grande que les précédentes")

    secteur_base = acces.intervale(base, secteur_debut, secteur_fin)
    total_plus = 0
    total_moins = 0
    for comparo in acces.itere_comparos(base, secteur_debut, secteur_fin, comparo_debut, comparo_fin):
        valeurs = algo.compare(secteur_base, comparo)
        deltas = [algo.delta(*delta) for delta in acces.itere_delta(valeurs, formule_delta)]
        binomes = algo.binomes(deltas)
        plus, moins = algo.decompte(binomes)
        total_plus += plus
        total_moins += moins
    return total_plus, total_moins
