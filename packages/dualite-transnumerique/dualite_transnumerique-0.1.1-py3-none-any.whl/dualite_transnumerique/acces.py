from typing import List, Generator


def intervale(base: List[int], debut: int, fin: int) -> List[int]:
    while debut <= 0:
        debut += len(base)
        fin += len(base)
    while debut > len(base):
        debut -= len(base)
        fin -= len(base)
    if fin > len(base):
        return base[(debut - 1):] + base[0:(fin - len(base))]
    else:
        return base[(debut - 1):fin]


def itere_comparos(base: List[int], secteur_debut: int, secteur_fin: int, comparo_debut: int,
                   comparo_fin: int) -> Generator[List[int], None, None]:
    for comparo in range(comparo_debut, comparo_fin + 1):
        debut = secteur_debut - comparo
        fin = secteur_fin - comparo
        yield intervale(base, debut, fin)



def itere_delta(comparo: List[int], formule_delta: List[int]) -> Generator[List[int], None, None]:
    for i in range(-1, len(comparo) - formule_delta[3]):
        yield [comparo[i + d] for d in formule_delta]
