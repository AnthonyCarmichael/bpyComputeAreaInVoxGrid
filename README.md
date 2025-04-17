# Instruction pour l'usage du script de python pour Blender

## Introduction
Le script *computeAreaInVoxGrid.py* est un script python (bpy) qui permet de calculer l'aire de surface des objets dans une scène blender.

Ce script segmente la scène en coupant les faces des objets dans des voxels. La grosseur des voxels est paramétrable. Les faces contenues dans chacun des voxels sont coupées. Ceci permet de calculer facilement les faces à l'intérieur des limitations des voxels. Le cumule d'aire des faces internes dans les voxels sont comptabilisées et si l'aire est supérieure à 0, le voxel sera inscrit en sortie dans un fichier csv contenant le x, y, z du voxel et l'aire cumulée pour ce voxel spécifique.

Ce script à été testé avec Blender 4.3.
## Prérequis
- Blender installé
- Ajouter blender.exe dans la variable d'environnement PATH
- Scène blender contenant des objets
- Vérifier les unités de mesure pour correspondre aux unités correspondant aux besoins
## Utilisation
Pour utiliser ce script, il faut avoir une scène blender (.blend) contenant des objets. Ensuite, on peut lancer le script via un terminal:

>blender C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py

On peut ajouter des flags pour blender comme:

>blender --background

Ce flag lance le script avec blender sans l'interface graphique. C'est plus rapide et ça ne sauvegarde pas la scène donc les objets restent non altérés après l'exécution du script

Si on veut ajouter des arguments pour le script python il faut ajouter -- après le path du script.

>blender C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py -- 1 True

Le premier argument (1) est la grosseur du voxel en unité blender et le deuxième est pour afficher la grille dans l'interface graphique. Afficher la grille ralentit énormément le script et est plus utile comme outil pour debug.

*Auteurs :*
*Anthony Carmichael sous la supervision de Félix Chabot*
