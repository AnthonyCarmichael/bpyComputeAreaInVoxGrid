import subprocess
import shutil

# Chemin vers Blender
blender_bin = shutil.which("blender")

if blender_bin is None:
   print("Blender n'a pas été trouvé dans le PATH.")
else:
   print(f"Blender trouvé : {blender_bin}")

   blend_file = "C:/Users/antho/Documents/blender/scriptVox/allScene.blend"
   script_file = "C:/Users/antho/Documents/blender/scriptVox/script/computeAreaInVoxGrid.py"
   arguments = ["1", "-g", "-d"]


   command = [
      blender_bin,
      #"--background",
      blend_file,
      "--python", script_file,
      "--",  
      *arguments
   ]
   
   print(command)

   try:
      subprocess.run(command, check=True)
      print("Script exécuté avec succès.")
   except subprocess.CalledProcessError as e:
      print("Erreur lors de l'exécution du script Blender :", e)
