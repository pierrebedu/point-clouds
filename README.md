# Nuages de points

Dépôt pour apprendre les nuages de points sur un CPU, sans jeu de données lourd.

Le parcours prévu :

1. **Ouvrir** un nuage et lire ce qu'il contient. C'est le script actuel.
2. **Regarder** le nuage (visualisation).
3. **Segmenter** un objet dans une scène.
4. **ICP** : recaler un scan partiel sur un modèle 3D connu.

Seul le premier pas est en place.

## Jeu de données

[Stanford Bunny](https://graphics.stanford.edu/data/3Dscanrep/), du Stanford 3D Scanning Repository (Stanford University Computer Graphics Laboratory, 1996). C'est le lapin de référence en géométrie 3D : petit, public, et déjà utilisé pour la reconstruction et le recalage.

Le fichier versionné est `data/bunny/bun_zipper_res2.ply` :

- reconstruction du lapin, version décimée `res2` ;
- 8 171 points, environ 650 Ko ;
- la reconstruction pleine (`bun_zipper.ply`) en a 35 947. `res2` suffit pour apprendre sans charger la machine.

Les sommets portent `x y z`, plus `confidence` et `intensity` issus du scanner. Le fichier contient aussi des faces : c'est un maillage. Le script s'en sert comme d'un nuage et se contente de signaler le nombre de faces.

Ce maillage est le modèle 3D connu de l'étape ICP. Les scans partiels d'origine (`bun000`, `bun045`, etc.) restent sur le site de Stanford ; ils seront ajoutés au moment du recalage. Le lapin est un seul objet : la segmentation d'une scène (table, plusieurs objets) viendra ensuite, sur un autre nuage du même ordre de taille.

## Ouvrir le nuage

Python 3, bibliothèque standard uniquement. Pas de fenêtre : la visualisation est l'étape suivante.

```bash
python3 scripts/ouvrir_nuage.py
```

Autre fichier PLY ASCII :

```bash
python3 scripts/ouvrir_nuage.py chemin/vers/nuage.ply
```

La sortie donne le nombre de points, les propriétés, les autres éléments du fichier, puis min, max et moyenne de `x`, `y` et `z`.
