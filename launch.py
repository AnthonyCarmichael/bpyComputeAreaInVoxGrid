import subprocess
import shutil
import os

# Chemin vers Blender
blender_bin = shutil.which("blender")

if blender_bin is None:
   print("Blender n'a pas été trouvé dans le PATH.")
else:
   print(f"Blender trouvé : {blender_bin}")
   
   parent_dir = os.path.dirname(__file__)

   # Modifier le path pour votre fichier blender
   blend_file = "C:/path/to/m.blend"
   
   script_file = parent_dir+"/computeAreaInVoxGrid.py"
   
   # Permier argument correspond à la grosseur de voxel
   # Flag -g correspond à ground. Si le flag est présent, on vérifie s'il y a un objet nommé sol et ne calcule pas son aire (recommandé).
   # Falg -d correspond à draw. Si le flag est présent, on dessine la grille (non recommandé lorsqu'il y a beaucoup de voxels).
   arguments = ["5", "-g"]
   
   # Mettre "--background" en commentaire si l'on veut l'interface graphique de blender
   command = [
      blender_bin,
      "--background",
      blend_file,
      "--python", script_file,
      "--",  
      *arguments
   ]

   try:
      subprocess.run(command, check=True)
      print("Script exécuté avec succès.")
   except subprocess.CalledProcessError as e:
      print("Erreur lors de l'exécution du script Blender :", e)
