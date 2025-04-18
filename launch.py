import subprocess
import shutil

# Chemin vers Blender
blender_bin = shutil.which("blender")

if blender_bin is None:
   print("Blender n'a pas été trouvé dans le PATH.")
else:
   print(f"Blender trouvé : {blender_bin}")

   #blend_file = "C:/Users/antho/Documents/blender/scriptVox/allScene.blend"
   blend_file = "C:/Users/antho/Documents/blender/scriptVox/m1.blend"
   
   script_file = "C:/Users/antho/Documents/blender/scriptVox/script/computeAreaInVoxGrid.py"
   
   # Permier argument correspond à la grosseur de voxel
   # Flag -g correspond à ground. Si le flag est présent, on vérifie s'il y a un objet sol et on le supprime (recommandé).
   # Falg -d correspond à draw. Si le flag est présent, on déssine la grille (non recommandé lorsqu'il y a beaucoup de voxels).
   arguments = ["0.1", "-g"]
   
   # Mettre "--background" en commentaire si l'on veut l'interface graphique de blender
   command = [
      blender_bin,
      #"--background",
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
