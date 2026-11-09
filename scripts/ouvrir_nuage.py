#!/usr/bin/env python3
"""Ouvre un nuage de points PLY ASCII et affiche un résumé.

La visualisation, la segmentation et l'ICP viendront plus tard.
Ce script ne fait que lire le fichier et décrire les points.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def nuage_par_defaut() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "data"
        / "bunny"
        / "bun_zipper_res2.ply"
    )


def _lire_entete(fichier):
    premiere = fichier.readline()
    if premiere.strip() != "ply":
        raise ValueError("ce fichier n'est pas un PLY")

    format_ply = None
    elements = []
    courant = None

    while True:
        ligne = fichier.readline()
        if not ligne:
            raise ValueError("en-tête PLY incomplet")
        morceaux = ligne.split()
        if not morceaux or morceaux[0] in {"comment", "obj_info"}:
            continue
        if morceaux[0] == "format":
            format_ply = morceaux[1]
            continue
        if morceaux[0] == "element":
            courant = {
                "nom": morceaux[1],
                "nombre": int(morceaux[2]),
                "proprietes": [],
            }
            elements.append(courant)
            continue
        if morceaux[0] == "property":
            if courant is None:
                raise ValueError("propriété PLY hors d'un élément")
            courant["proprietes"].append(morceaux[1:])
            continue
        if morceaux[0] == "end_header":
            break
        raise ValueError(f"ligne d'en-tête inattendue : {ligne.rstrip()}")

    if format_ply != "ascii":
        raise ValueError(
            f"format PLY non géré : {format_ply} (seul le PLY ASCII est lu)"
        )
    return elements


def lire_ply_ascii(chemin: Path) -> dict:
    with chemin.open("r", encoding="ascii") as fichier:
        elements = _lire_entete(fichier)
        points = None
        noms = None

        for element in elements:
            if element["nom"] != "vertex":
                for _ in range(element["nombre"]):
                    if not fichier.readline():
                        raise ValueError(
                            f"fichier tronqué dans l'élément {element['nom']}"
                        )
                continue

            noms = []
            for propriete in element["proprietes"]:
                if propriete[0] == "list":
                    raise ValueError("liste de valeurs sur un sommet non gérée")
                noms.append(propriete[-1])
            if not {"x", "y", "z"} <= set(noms):
                raise ValueError("les sommets n'ont pas de coordonnées x y z")

            points = []
            for _ in range(element["nombre"]):
                valeurs = fichier.readline().split()
                if len(valeurs) < len(noms):
                    raise ValueError("ligne de sommet incomplète")
                points.append(
                    {nom: float(brut) for nom, brut in zip(noms, valeurs)}
                )

        if points is None:
            raise ValueError("aucun sommet dans ce PLY")

    return {"elements": elements, "noms": noms, "points": points}


def afficher(chemin: Path, nuage: dict) -> None:
    points = nuage["points"]
    nombre = len(points)
    print(f"fichier    : {chemin}")
    print("format     : PLY ascii")
    print(f"points     : {nombre}")
    print(f"propriétés : {', '.join(nuage['noms'])}")

    for element in nuage["elements"]:
        if element["nom"] != "vertex":
            print(f"{element['nom']:<11}: {element['nombre']}")

    for axe in ("x", "y", "z"):
        valeurs = [point[axe] for point in points]
        print(
            f"{axe}          : "
            f"min {min(valeurs): .6f}   "
            f"max {max(valeurs): .6f}   "
            f"moyenne {sum(valeurs) / nombre: .6f}"
        )


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Ouvre un nuage PLY ASCII et affiche un résumé."
    )
    analyseur.add_argument(
        "chemin",
        nargs="?",
        type=Path,
        default=nuage_par_defaut(),
        help="fichier .ply (défaut : Stanford Bunny, version res2)",
    )
    args = analyseur.parse_args(argv)
    chemin = args.chemin
    if not chemin.is_file():
        print(f"fichier introuvable : {chemin}", file=sys.stderr)
        return 1
    try:
        nuage = lire_ply_ascii(chemin)
    except (OSError, UnicodeError, ValueError) as erreur:
        print(f"lecture impossible : {erreur}", file=sys.stderr)
        return 1
    afficher(chemin, nuage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
