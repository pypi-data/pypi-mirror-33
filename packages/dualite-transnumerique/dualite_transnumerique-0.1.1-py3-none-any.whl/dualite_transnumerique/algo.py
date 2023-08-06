from typing import List, Tuple


def compare(secteur_base: List[int], comparo: List[int]) -> List[int]:
    return [a ^ b for a, b in zip(secteur_base, comparo)]


def delta(a: int, b: int, c: int, d: int) -> bool:
    return (a + b + c >= 2) == bool(d)


def binomes(deltas: List[bool]) -> List[bool]:
    return [a == b for a, b in zip(deltas[0:-1], deltas[1:])]


def decompte(binomes: List[bool]) -> Tuple[int, int]:
    plus = binomes.count(True)
    return plus, len(binomes) - plus
