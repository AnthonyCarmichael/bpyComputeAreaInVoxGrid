# Instruction pour l'usage du script python pour Blender Compute Area In Vox Grid

## Introduction
Le script *computeAreaInVoxGrid.py* est un script en python qui permet de calculer l'aire de surface des objets dans une scène blender.

Ce script segmente la scène en coupant les faces des objets dans des voxels. La grosseur des voxels est paramétrable. Les faces contenues dans chacun des voxels sont coupées. Ceci permet de calculer facilement les faces à l'intérieur des limitations des voxels. Le cumule d'aire des faces internes dans les voxels sont comptabilisées et si l'aire est supérieure à 0, le voxel sera inscrit en sortie dans un fichier csv contenant le x, y, z du voxel et l'aire cumulée pour ce voxel spécifique.

Ce script à été testé avec Blender 4.3.
## Prérequis
- Blender installé
- Ajouter blender.exe dans la variable d'environnement PATH
- Scène blender contenant des objets
- Vérifier les unités de mesure pour correspondre a l'unité de mesure correspondant aux besoins
## Utilisation
Pour utiliser ce script, il faut avoir une scène blender (.blend) contenant des objets. Ensuite, on peut lancer le script via un terminal ou par le fichier **launch.py** après configuration :

```
blender --background C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py -- 1 
```

Paramètre à considérer (dans le fichier launch):

1. Chemin du fichier blend
2. Arguments du script python
3. Arguments blender

On peut ajouter des flags pour blender comme:

```
blender --background
```

Ce flag lance le script avec blender sans l'interface graphique. C'est plus rapide et ça ne sauvegarde pas la scène donc les objets restent non altérés après l'exécution du script. Il est préférable de le garder sauf pour debug.

On doit ajouter des arguments pour le script python. Il faut ajouter **--** après le chemin du script python. Ensuite, on met la **grosseur des voxels** en unité blender.

```
blender C:/path/to/sceneBlender.blend --python C:/path/to/computeAreaInVoxGrid.py -- 1 -d -g
```

Le flag **-d** est pour afficher la grille dans l'interface graphique. Afficher la grille ralentit énormément le script lorsqu'il y a beaucoup de voxels et est plus utile comme outil pour debug.

Le flag **-g**  permet de retirer tout objet nommé 'sol' du calcul de l'aire pour accélérer le temps de traitement.

## Pour utiliser blender avec Helios++

Ce script a été conçu dans l'optique de comparer des données collectées d'une maquette dans blender avec la sortie de l'algorithme L-Vox utilisant des nuages de points. C'est pourquoi cette section a pour but de guider l'utilisateur de ce script à transformer la maquette 3D en nuage de point à l'aide de Helios++

### Étapes

1. Télécharger Helios++ : https://github.com/3dgeo-heidelberg/helios

   Pour reproduire exactement la même installation:

   1. Cloner le dépôt github de Helios++

   2. Créer un environnement conda avec [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html), [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) ou [miniconda](https://www.anaconda.com/docs/main) (testé avec miniconda)

   3. Ligne pour installer helios dans l'environnement conda activé:
      
``` 
conda install -c conda-forge helios
```

2. Cloner le dépôt de Blender2Helios : https://github.com/neumicha/Blender2Helios.git

3. Installer le addon Blender2Helios dans blender
   (documentation https://github.com/neumicha/Blender2Helios/wiki/Installation)

   1. Cliquer sur edit et préférences
   
      ![screenshot](img/screenshot4.png)

   2. Dans le menu preferences, cliquer sur **Get Extensions** et à droite de la fenêtre, sur la **flèche** pour ouvrir les options d'installation du addon. Ensuite cliquer sur **Install from Disk** et sélectionner blender2helios.py du dépôt cloné précédament.
      ![screenshot](img/screenshot5.png)
   
   3. Ensuite, cliquer sur **Add-ons** et trouver Helios2Blender pour l'activer et le paramètrer. Il faut indiquer le chemin vers le dossier de Helios++ cloné préalablement.
      ![screenshot](img/screenshot6.png)
   
      
   
4. Une fois que le addon est ajouté dans blender via l'installation par le disque, ouvrir la scène que l'on veut exporter et cliquer sur **Render** (à côté de *edit* sur la barre d'outil supérieur) et ensuite sur **Run Blender2Helios Export**.

   Ceci exportera la scène blend en fichier xml dans le dossier **data** du dossier de helios++

   ![screenshot](img/screenshot1.png)

   Il faut que les obj soient dans une collection. Ils seront placés dans un dossier portant le nom de cette collection. Dans ce cas-ci, la collection "test" sera exportée dans helios.

   ![screenshot](img/screenshot2.png)

5. Dans un terminal avec l'environnement conda activé se positionner dans le dossier de helios++

6. Lancer la commande suivante pour obtenir un fichier las:

```
helios data/surveys/blender2heliosScene.xml --lasOutput
```

7. Vous devriez avoir dans *helios/output/blender2heliosScene* un nouveau dossier contenant un fichier las.

   ![screenshot](img/screenshot3.png)
