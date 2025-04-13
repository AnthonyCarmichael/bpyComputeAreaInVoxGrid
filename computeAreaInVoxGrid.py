import bpy
import bmesh
from mathutils import Vector
import math
from datetime import datetime
import os

class Grid:
    def __init__(self, voxel_size):
        self.objs = get_all_objs()
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

        # Délimitation englobante de tout les objets. 
        # Nous devons ajuster la grandeur de grille pour respecter la dimension des voxels
        print("bbox_min:", self.bbox_min)
        print("bbox_max:", self.bbox_max)
        
        self.dimensions = self.bbox_max - self.bbox_min
               
        # Calculer la résolution pour chaque axe
        self.resolution = (
            max(1, math.ceil(self.dimensions.x / voxel_size)),
            max(1, math.ceil(self.dimensions.y / voxel_size)),
            max(1, math.ceil(self.dimensions.z / voxel_size)),
        )
        
        self.dimx = self.resolution[0] * voxel_size
        self.dimy = self.resolution[1] * voxel_size
        self.dimz = self.resolution[2] * voxel_size
        
        for x in range(self.resolution[0]):
            for y in range(self.resolution[1]):
                for z in range(self.resolution[2]):
                    self.add_voxel(x, y, z, 0)   

    def add_voxel(self, x, y, z, value):
        self.voxels[(x, y, z)] = value

    def remove_voxel(self, x, y, z):
        if (x, y, z) in self.voxels:
            del self.voxels[(x, y, z)]

    def get_voxel(self, x, y, z):
        return self.voxels.get((x, y, z))

    def display(self):
        print("RÉSULTATS:")
        print(f"Dimensions obj {self.dimensions.x:.2f} x {self.dimensions.y:.2f} x {self.dimensions.z:.2f} avec {len(self.voxels)} voxels.")
        print(f"Résolution: {self.resolution[0]} x {self.resolution[1]} x {self.resolution[2]}")
        print(f"Grosseur d'un voxel: {self.voxel_size}")
        print(f"Dimension de la grille: dimx {self.dimx}, dimy {self.dimy}, dimz {self.dimz}")
        print(f"Aire totale: {sum(self.voxels.values())}\n")
    
    def draw(self):
        
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
        for i in range(self.resolution[0] + 1):
            x = self.bbox_min.x + i * step_x
            for j in range(self.resolution[1] + 1):
                y = self.bbox_min.y + j * step_y
                for k in range(self.resolution[2] + 1):
                    z = self.bbox_min.z + k * step_z
                    vertices[(i, j, k)] = bm.verts.new((x, y, z))

        bm.verts.ensure_lookup_table()

        # Créer les arêtes de la grille
        for i in range(self.resolution[0] + 1):
            for j in range(self.resolution[1] + 1):
                for k in range(self.resolution[2] + 1):
                    if k < self.resolution[2]:  # Arêtes Z
                        v1 = vertices.get((i, j, k))
                        v2 = vertices.get((i, j, k + 1))
                        if v1 and v2:
                            bm.edges.new((v1, v2))

                    if j < self.resolution[1]:  # Arêtes Y
                        v1 = vertices.get((i, j, k))
                        v2 = vertices.get((i, j + 1, k))
                        if v1 and v2:
                            bm.edges.new((v1, v2))

                    if i < self.resolution[0]:  # Arêtes X
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

        
    def cut_cube_into_voxels(self):
        # Passer en mode objet
        print(f"\n#######################################\nDébut de la coupe de la scène en voxel")
        obj = self.obj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Accéder aux données du maillage
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        progress =0
        end_progress = self.resolution[0]+self.resolution[1]+self.resolution[2]
        
        # Récupérer la matrice monde inverse
        world_matrix_inv = obj.matrix_world.inverted()
        
        # Plans de coupe sur l'axe X
        for i in range(1, self.resolution[0]):
            print(f"Progression de la coupe: {round(progress/end_progress*100,2)} %")
            pos_x = self.bbox_min.x + i * self.voxel_size
            local_co = world_matrix_inv @ Vector((pos_x, 0, 0))
            plane_no = world_matrix_inv.to_3x3() @ Vector((1, 0, 0))
            
            bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=local_co,
                plane_no=plane_no,
                clear_inner=False,
                clear_outer=False,
            )
            progress +=1
        
        # Plans de coupe sur l'axe Y
        for j in range(1, self.resolution[1]):
            print(f"Progression de la coupe: {round(progress/end_progress*100,2)} %")
            pos_y = self.bbox_min.y + j * self.voxel_size
            local_co = world_matrix_inv @ Vector((0, pos_y, 0))
            plane_no = world_matrix_inv.to_3x3() @ Vector((0, 1, 0))
            
            bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=local_co,
                plane_no=plane_no,
                clear_inner=False,
                clear_outer=False,
            )
            progress +=1
        
        # Plans de coupe sur l'axe Z
        for k in range(1, self.resolution[2]):
            print(f"Progression de la coupe: {round(progress/end_progress*100,2)} %")
            pos_z = self.bbox_min.z + k * self.voxel_size
            local_co = world_matrix_inv @ Vector((0, 0, pos_z))
            plane_no = world_matrix_inv.to_3x3() @ Vector((0, 0, 1))
            
            bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=local_co,
                plane_no=plane_no,
                clear_inner=False,
                clear_outer=False,
            )
            progress +=1
        
        print(f"Progression de la coupe: {round(progress/end_progress*100,2)} %")
        # Appliquer les modifications
        bpy.ops.object.mode_set(mode='OBJECT')
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        
        # Mettre à jour l'affichage
        bpy.context.view_layer.update()
        print(f"\nFin de la coupe de la scène en voxel\n#######################################\n")
        
    def cut_objects_into_voxels(self):
        # Passer en mode objet
        print(f"\n#######################################\nDébut de la coupe de la scène en voxel")
        
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
            
            # Récupérer la matrice monde inverse
            world_matrix_inv = obj.matrix_world.inverted()
            
            # Plans de coupe sur l'axe X
            for i in range(1, self.resolution[0]):
                pos_x = self.bbox_min.x + i * self.voxel_size
                local_co = world_matrix_inv @ Vector((pos_x, 0, 0))
                plane_no = world_matrix_inv.to_3x3() @ Vector((1, 0, 0))
                
                bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=local_co,
                    plane_no=plane_no,
                    clear_inner=False,
                    clear_outer=False,
                )
            
            # Plans de coupe sur l'axe Y
            for j in range(1, self.resolution[1]):
                pos_y = self.bbox_min.y + j * self.voxel_size
                local_co = world_matrix_inv @ Vector((0, pos_y, 0))
                plane_no = world_matrix_inv.to_3x3() @ Vector((0, 1, 0))
                
                bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=local_co,
                    plane_no=plane_no,
                    clear_inner=False,
                    clear_outer=False,
                )
            
            # Plans de coupe sur l'axe Z
            for k in range(1, self.resolution[2]):
                pos_z = self.bbox_min.z + k * self.voxel_size
                local_co = world_matrix_inv @ Vector((0, 0, pos_z))
                plane_no = world_matrix_inv.to_3x3() @ Vector((0, 0, 1))
                
                bmesh.ops.bisect_plane(
                    bm,
                    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                    plane_co=local_co,
                    plane_no=plane_no,
                    clear_inner=False,
                    clear_outer=False,
                )
            
            # Appliquer les modifications
            bpy.ops.object.mode_set(mode='OBJECT')
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            
        # Mettre à jour l'affichage
        bpy.context.view_layer.update()
        print(f"\nFin de la coupe de la scène en voxel\n#######################################\n")

    def display_voxs(self):
        total = 0
        for x in range(self.resolution[0]):
            for y in range(self.resolution[1]): 
                for z in range(self.resolution[2]):
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
                
                face_center = face.calc_center_median()
                face_center -= origin_offset
                
                x = math.floor(face_center.x / self.voxel_size)
                y = math.floor(face_center.y / self.voxel_size)
                z = math.floor(face_center.z / self.voxel_size)
                
                if x> self.resolution[0] -1:
                    x-=1
                if y> self.resolution[1] -1:
                    y-=1
                if z> self.resolution[2] -1:
                    z-=1
                    
                self.voxels[x,y,z] += face.calc_area()
                
            bm.free()   
    
    def export_vox_areas(self):
        if not os.path.exists("output"):
            os.makedirs("output")
            
        # Exportation des données (optionnel)
        with open("output/surface_areas.csv", "w") as f:
            f.write("Cell_X,Cell_Y,Cell_Z,Surface_Area\n")
            for (i, j, k), area in self.voxels.items():
                f.write(f"{i},{j},{k},{area:.6f}\n") 
            
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
    
def get_all_objs():
    if  bpy.data.objects is None:
        print(f"Il n'y a pas d'objet dans la scène")
        return None
    return bpy.data.objects
    
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
    

def main():
    # Setup
    start = datetime.now()
    cleanUp()
    voxel_size=1
    
    # Création de la grille et affichage
    grid = Grid(voxel_size)
    
    # Lent lorsqu'il y a beaucoup de voxels
    grid.draw()
    
    grid.cut_objects_into_voxels()
    grid.itFaces()
    grid.display() 
    grid.export_vox_areas()
    
    fin = datetime.now()
    
    print("TEMPS:")
    print(f"Début: {start}\nFin: {fin}\nDurée: {fin-start}\n")
    
                    
main()

# commande terminal pour lancer blender en mode background 
# (ajouter blender dans le PATH C:\Program Files\Blender Foundation\Blender 4.3)
# blender --background C:/Users/antho/Documents/blender/scriptVox/scriptLVoxArea.blend --python C:/Users/antho/Documents/blender/scriptVox/script/computeAreaInVoxGrid.py
# blender --background C:/Users/antho/Documents/blender/scriptVox/allScene.blend --python C:/Users/antho/Documents/blender/scriptVox/script/computeAreaInVoxGrid.py