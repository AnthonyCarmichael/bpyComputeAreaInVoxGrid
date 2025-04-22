import bpy
from mathutils import Vector
import bmesh
import sys
import math
from datetime import datetime
import os
import argparse

class Grid:
    def __init__(self, voxel_size, objs):
        self.objs = objs
        self.voxels = {}
        self.voxel_size = voxel_size
        
        # Déterminer la grandeur minimale de la grille en fonction des objets de la scène
        all_corners = [obj.matrix_world @ Vector(corner) for obj in self.objs for corner in obj.bound_box]

        min_x = min(corner.x for corner in all_corners)
        min_y = min(corner.y for corner in all_corners)
        min_z = min(corner.z for corner in all_corners)
        
        max_x = max(corner.x for corner in all_corners)
        max_y = max(corner.y for corner in all_corners)
        max_z = max(corner.z for corner in all_corners)

        self.bbox_min = Vector((min_x, min_y, min_z))
        self.bbox_max = Vector((max_x, max_y, max_z))

        print("bbox_min:", self.bbox_min)
        print("bbox_max:", self.bbox_max)
        
        self.dimensions = self.bbox_max - self.bbox_min  
        
        self.dimx = int(max(1, math.ceil(self.dimensions.x / voxel_size)))
        self.dimy = int(max(1, math.ceil(self.dimensions.y / voxel_size)))
        self.dimz = int(max(1, math.ceil(self.dimensions.z / voxel_size)))
        print(f"{self.dimx},{self.dimy},{self.dimz}")
        
    def display(self):
        print("RÉSULTATS:")
        print(f"Dimensions bbox {self.dimensions.x:.2f} x {self.dimensions.y:.2f} x {self.dimensions.z:.2f}")
        print(f"Résolution: {self.dimx} x {self.dimy} x {self.dimz}")
        print(f"Grosseur d'un voxel: {self.voxel_size}")
        print(f"Dimension de la grille: dimx {self.dimx}, dimy {self.dimy}, dimz {self.dimz}")
        print(f"Aire totale: {sum(self.voxels.values())}\n")
        
        if not os.path.exists("output"):
            os.makedirs("output")
            
        # Exportation des données (optionnel)
        with open("output/info_grid.txt", "w") as f:
            f.write("RÉSULTATS:\n")
            f.write(f"Dimensions bbox {self.dimensions.x:.2f} x {self.dimensions.y:.2f} x {self.dimensions.z:.2f}\n")
            f.write(f"Résolution: {self.dimx} x {self.dimy} x {self.dimz}\n")
            f.write(f"Grosseur d'un voxel: {self.voxel_size}\n")
            f.write(f"Dimension de la grille: dimx {self.dimx}, dimy {self.dimy}, dimz {self.dimz}\n")
            f.write(f"Aire totale: {sum(self.voxels.values())}")
            
            f.close()
    
    def draw(self):
        cleanUp()
        # Créer un mesh pour la grille
        grid_mesh = bpy.data.meshes.new("GridMesh")
        grid_obj = bpy.data.objects.new("3DGrid", grid_mesh)
        bpy.context.collection.objects.link(grid_obj)
        
        # Créer le bmesh pour construire la grille
        bm = bmesh.new()
        
        # Calculer les pas
        step_x = self.voxel_size
        step_y = self.voxel_size
        step_z = self.voxel_size
        
        # Dictionnaire pour stocker les sommets avec leurs indices 3D
        vertices = {}

        # Créer les vertices de la grille
        for i in range(self.dimx + 1):
            x = self.bbox_min.x + i * step_x
            for j in range(self.dimy + 1):
                y = self.bbox_min.y + j * step_y
                for k in range(self.dimz + 1):
                    z = self.bbox_min.z + k * step_z
                    vertices[(i, j, k)] = bm.verts.new((x, y, z))

        bm.verts.ensure_lookup_table()

        # Créer les arêtes de la grille
        for i in range(self.dimx + 1):
            for j in range(self.dimy + 1):
                for k in range(self.dimz + 1):
                    if k < self.dimz:  # Arêtes Z
                        v1 = vertices.get((i, j, k))
                        v2 = vertices.get((i, j, k + 1))
                        if v1 and v2:
                            bm.edges.new((v1, v2))

                    if j < self.dimy:  # Arêtes Y
                        v1 = vertices.get((i, j, k))
                        v2 = vertices.get((i, j + 1, k))
                        if v1 and v2:
                            bm.edges.new((v1, v2))

                    if i < self.dimx:  # Arêtes X
                        v1 = vertices.get((i, j, k))
                        v2 = vertices.get((i + 1, j, k))
                        if v1 and v2:
                            bm.edges.new((v1, v2))

        # Finaliser le bmesh
        bm.to_mesh(grid_mesh)
        bm.free()

        # Mettre à jour l'affichage
        grid_obj.display_type = 'WIRE'
        grid_mesh.update()

    
    def cut_objects_into_voxels(self):
        progress = 0
        end_progress = len(self.objs) * (self.dimx+self.dimy+self.dimz)
        
        for obj in self.objs:
            #bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Accéder aux données du maillage
            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)
            
            world_matrix_inv = obj.matrix_world.inverted()            
            
            # Plans de coupe sur l'axe X
            for x in range( self.dimx):
                pos_x = self.bbox_min.x + x * self.voxel_size
                norm = Vector((1, 0, 0))
                point = Vector((pos_x, 0, 0))
                bisect_on_axis(point,norm,world_matrix_inv,bm)
                progress+=1
                update_progress("Coupe la grille en voxels", progress/end_progress)
                
            # Plans de coupe sur l'axe Y
            for y in range(self.dimy):
                pos_y = self.bbox_min.y + y * self.voxel_size
                norm = Vector((0, 1, 0))
                point = Vector((0, pos_y, 0))
                bisect_on_axis(point,norm,world_matrix_inv,bm)
                progress+=1
                update_progress("Coupe la grille en voxels", progress/end_progress)
                
            # Plans de coupe sur l'axe Z
            for z in range(self.dimz):
                pos_z = self.bbox_min.z + z * self.voxel_size
                norm = Vector((0, 0, 1))
                point = Vector((0, 0, pos_z))
                bisect_on_axis(point,norm,world_matrix_inv,bm)
                progress+=1
                update_progress("Coupe la grille en voxels", progress/end_progress)
                
            # Appliquer les modifications
            bpy.ops.object.mode_set(mode='OBJECT')
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            
        # Mettre à jour l'affichage
        bpy.context.view_layer.update()
        if progress < end_progress:
            update_progress("Coupe la grille en voxels", 1)

    def display_voxs(self):
        total = 0
        for x in range(self.dimx):
            for y in range(self.dimy): 
                for z in range(self.dimz):
                    # Calculer l'aire de surface dans ce voxel
                    print(f"vox ({x},{y},{z}): {self.voxels[x,y,z]}")                 
                    total += self.voxels[x,y,z]
        print(f"Aire total = {total}")
        
    def itFaces(self):  
        for obj in self.objs:      
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.transform(obj.matrix_world)
            
            min_x = self.bbox_min.x
            min_y = self.bbox_min.y
            min_z = self.bbox_min.z

            origin_offset = Vector((min_x, min_y, min_z))
        
            for face in bm.faces:
                
                # check goemetrical center
                face_center = face.calc_center_median()
                face_center -= origin_offset
                
                x = math.floor(face_center.x / self.voxel_size)
                y = math.floor(face_center.y / self.voxel_size)
                z = math.floor(face_center.z / self.voxel_size)
                
                if x> self.dimx -1:
                    x-=1
                if y> self.dimy -1:
                    y-=1
                if z> self.dimz -1:
                    z-=1
                    
                self.voxels[x,y,z] = self.voxels.get((x,y,z), 0) + face.calc_area()
                
            bm.free()   
    
    def export_vox_areas(self):
        if not os.path.exists("output"):
            os.makedirs("output")
            
        # Exportation des données (optionnel)
        with open("output/surface_areas.csv", "w") as f:
            f.write("Cell_X,Cell_Y,Cell_Z,Surface_Area\n")
            for (i, j, k), area in self.voxels.items():
                # if area > 0:
                f.write(f"{i},{j},{k},{area}\n") 
            
        f.close()    
                        
#########################################################################        
# Fonctions    
    
def get_obj(name):

    if name not in bpy.data.objects:
        print(f"L'objet '{name}' n'existe pas.")
        return None
    
    obj = bpy.data.objects.get(name)
    
    if obj.type != 'MESH':
        print(f"L'objet '{name}' n'est pas un mesh.")
        return None
    else:
        return obj
    
def get_all_objs(boolDelGround):
    
    if  bpy.data.objects is None:
        print(f"Il n'y a pas d'objet dans la scène")
        return None
    
    if boolDelGround == False:
        return bpy.context.scene.objects
    else:
        listObj = []
        for obj in bpy.context.scene.objects:
            
            if obj.name != "sol": 
                listObj.append(obj)
    

    return listObj
    
def cleanUp():
    # Créer une collection pour les voxels
    collection_name = "VoxelGrid"
    if collection_name in bpy.data.collections:
        voxel_collection = bpy.data.collections[collection_name]
        # Supprimer les objets existants dans la collection
        for obj in list(voxel_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        voxel_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(voxel_collection)
        
    # Active la collection VoxelGrid    
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["VoxelGrid"]
    
def update_progress(job_title, progress):
    length = 20 
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()
    
def bisect_on_axis(point,normal,world_matrix_inv,bm):
    local_co = world_matrix_inv @ point
    local_no = world_matrix_inv.to_3x3() @ normal
    
    bmesh.ops.bisect_plane(
        bm,
        geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=local_co,
        plane_no=local_no,
        clear_inner=False,
        clear_outer=False,
    )

def delGround():
    
    for obj in bpy.context.scene.objects:
        if obj.name == "sol": 
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['sol'].select_set(True) 
            bpy.ops.object.delete()   
            break
    else: 
        print("Il n'y à pas d'objet \"sol\" à retirer")
        
class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())

def main():
    # Setup
    start = datetime.now()
    # Parser d'arguments
    
    parser = ArgumentParserForBlender()
    parser.add_argument("vox_size", help="Choose a voxel size",
                        type=float, default=1)
    parser.add_argument("-d","--draw_grid", help="Visualization of the grid in blender",
                        action="store_true")
    parser.add_argument("-g","--delete_ground", help="Delete the ground from the scene",
                    action="store_true")
    args = parser.parse_args()
    
    if args.vox_size >0:
        print(f"Argument : Vox size = {args.vox_size}")
        voxel_size=args.vox_size
        # Création de la grille et affichage
        listObj = (get_all_objs(args.delete_ground))
            
        grid = Grid(voxel_size,listObj)
        # Lent lorsqu'il y a beaucoup de voxels plus utile pour debug avec des gros voxels
        if args.draw_grid:
            grid.draw()
        grid.cut_objects_into_voxels()
        grid.itFaces()
        grid.display() 
        grid.export_vox_areas()
        
    fin = datetime.now()
    
    print("TEMPS:")
    print(f"Début: {start}\nFin: {fin}\nDurée: {fin-start}\n")
                      
main()
