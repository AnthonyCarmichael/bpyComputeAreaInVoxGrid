# Instruction pour l'usage du script de python pour Blender

## Introduction
Le script *computeAreaInVoxGrid.py* est un script python (bpy) qui permet de calculer l'aire de surface des objets dans une scène blender.

Ce script segmente la scène en coupant les faces des objets dans des voxels. La grosseur des voxels est paramétrable. Les faces contenues dans chacun des voxels sont coupées. Ceci permet de calculer facilement les faces à l'intérieur des limitations des voxels. Le cumule d'aire des faces internes dans les voxels sont comptabilisées et si l'aire est supérieure à 0, le voxel sera inscrit en sortie dans un fichier csv contenant le x, y, z du voxel et l'aire cumulée pour ce voxel spécifique.

Ce script à été testé avec Blender 4.3.
## Prérequis
- Blender installé
- Ajouter blender.exe dans la variable d'environnement PATH
- Scène blender contenant des objets
- Vérifier les unités de mesure pour correspondre a l'unité de mesure correspondant aux besoins
## Utilisation
Pour utiliser ce script, il faut avoir une scène blender (.blend) contenant des objets. Ensuite, on peut lancer le script via un terminal:

`blender --background C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py -- 1`

On peut ajouter des flags pour blender comme:

`blender --background`

Ce flag lance le script avec blender sans l'interface graphique. C'est plus rapide et ça ne sauvegarde pas la scène donc les objets restent non altérés après l'exécution du script. Il est préférable de le garder sauf pour debug.

On doit ajouter des arguments pour le script python. Il faut ajouter **--** après le chemin du script python. Ensuite, on met la **grosseur des voxels** en unité blender.

`blender C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py -- 1 -d`

Le flag **-d** est pour afficher la grille dans l'interface graphique. Afficher la grille ralentit énormément le script lorsqu'il y a beaucoup de voxels et est plus utile comme outil pour debug.

## Pour utiliser blender avec Helios++

Ce script a été conçu dans l'optique de comparer des données collectées d'une maquette par blender et les comparer avec l'algorithme LVox utilisant des nuages de points. C'est pourquoi, il y a cette section pour guider l'utilisateur de se script à transformer la maquette 3D en nuage de point à l'aide de Helios++

### Étapes

1. Télécharger Helios++ : https://github.com/3dgeo-heidelberg/helios

2. Télécharger Blender2Helios : https://github.com/AnthonyCarmichael/Blender2Helios.git

3. Suivre la procédure d'installation du addon Blender2Helios : https://github.com/neumicha/Blender2Helios/wiki/Installation

4. Une fois que le addon est ajouté dans blender via l'installation par le disque, ouvrir la scène que l'on veut exporter et cliquer sur **Render** (à côté de *edit* sur la barre d'outil supérieur) et ensuite sur **Run Blender2Helios Export**.

   Il faut que les obj soit dans une collection. Ils seront placé dans un dossié portant le nom de cette collection. Dans ce cas ci "test".

5. Installer conda (recommandé mamba, micromamba ou miniconda)

6. Installer Helios++ dans un environnement python

   `conda install -c conda-forge helios`

7. Dans le terminal, se positionner dans le dossier de helios

   `cd path/to/helios`

8. Lancer la commande suivate pour obtenir un fichier las:

   `helios data\surveys\blender2heliosScene.xml --lasOutput`

   Si ça ne marche pas à cause du chemin pour le scanner ou la plateforme, modifier le chemin du scanner et de la plateforme du fichier *helios/data/surveys/blender2heliosScene.xml* pour ceci :

   `platform="data/platforms.xml#tripod" scanner="data/scanners_tls.xml#riegl_vz400"`

9. Vous devriez avoir dans *helios/output/blender2heliosScene* un nouveau dossier contenant un fichier las.



*Auteurs :*
*Anthony Carmichael sous la supervision de Félix Chabot*
