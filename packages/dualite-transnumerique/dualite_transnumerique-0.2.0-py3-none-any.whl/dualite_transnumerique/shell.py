# coding=utf-8
"""
La dualité transnumérique
"""

import argparse
from typing import List

from dualite_transnumerique import entree, calcul


def intervale(texte: str) -> List[int]:
    return [int(x) for x in texte.split(':')]


def _arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)

    input = parser.add_mutually_exclusive_group(required=True)
    input.add_argument('--fichier', type=str, help='Fichier aléatoire')
    input.add_argument('--aleatoire', type=int, help='Prend une série de nombres aléatoires')


    parser.add_argument('--secteur', type=intervale, help='Secteur de base (deux chiffres, séparés par ":")')
    parser.add_argument('--comparos', type=intervale, help='Comparos (deux chiffres, séparés par ":")')
    parser.add_argument('--formule-delta', type=intervale,
                        help='Les 4 chiffres de la formule delta, séparés par ":"')

    return parser


def main() -> None:
    args = _arg_parser().parse_args()
    if args.aleatoire:
        colonnes = entree.aleatoire(args.aleatoire)
    else:
        colonnes = entree.fichier(args.fichier)
    for i, valeurs in enumerate(colonnes):
        plus, moins = calcul.calcul(valeurs, args.secteur[0], args.secteur[1], args.comparos[0],
                                    args.comparos[1], args.formule_delta)
        print(f"{chr(ord('A') + i)}: +={plus} -={moins}")


if __name__ == "__main__":
    main()
