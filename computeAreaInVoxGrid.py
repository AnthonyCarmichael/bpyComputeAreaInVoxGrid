import bpy
import bmesh
from mathutils import Vector
import math
from datetime import datetime

class Grid:
    def __init__(self, voxel_size ,margin,obj):
        self.obj = obj

        self.voxel_size = voxel_size
        self.voxels = {}
        self.margin = margin
        
        # Récupérer les dimensions et la position de l'objet
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        # Trouver les points min et max
        self.bbox_min = Vector((
            min(corner.x for corner in bbox_corners),
            min(corner.y for corner in bbox_corners),
            min(corner.z for corner in bbox_corners)
        ))
        
        self.bbox_max = Vector((
            max(corner.x for corner in bbox_corners),
            max(corner.y for corner in bbox_corners),
            max(corner.z for corner in bbox_corners)
        ))
        
            
        if(margin>0):
            self.bbox_min -= Vector((margin, margin, margin))
            self.bbox_max += Vector((margin, margin, margin))
            self.voxel_size += margin
            
    
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
        print(f"Dimensions obj {self.dimensions.x:.2f} x {self.dimensions.y:.2f} x {self.dimensions.z:.2f} avec {len(self.voxels)} voxels.")
        print(f"Résolution: {self.resolution[0]} x {self.resolution[1]} x {self.resolution[2]}")
        print(f"Grosseur d'un voxel: {self.voxel_size}")
        print(f"Dimension de la grille: dimx {self.dimx}, dimy {self.dimy}, dimz {self.dimz}")
    
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
        print(f"#######################################\nDébut de la coupe de la scène en voxel")
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
    
    def compute_areas_in_grid(self):
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        bm.transform(self.obj.matrix_world)
        for x in range(self.resolution[0]):
            for y in range(self.resolution[1]): 
                for z in range(self.resolution[2]):
                    # Calculer l'aire de surface dans ce voxel
                    voxel_surface_area = self.calculate_surface_area_in_voxel(bm,x,y,z)
                    self.voxels[x, y, z] = voxel_surface_area
        bm.free()

    def calculate_surface_area_in_voxel(self,bm, x, y, z):

        voxel_min = Vector((
            self.bbox_min.x + x * self.voxel_size,
            self.bbox_min.y + y * self.voxel_size,
            self.bbox_min.z + z * self.voxel_size
        ))
        
        voxel_max = Vector((
            self.bbox_min.x + (x + 1) * self.voxel_size,
            self.bbox_min.y + (y + 1) * self.voxel_size,
            self.bbox_min.z + (z + 1) * self.voxel_size
        ))
        
        surface_area = 0.0
        
        for face in bm.faces:
            face_center = face.calc_center_median()
            if (voxel_min.x  <= face_center.x <= voxel_max.x and
                voxel_min.y <= face_center.y <= voxel_max.y  and
                voxel_min.z  <= face_center.z <= voxel_max.z):
                
                # Ajouter l'aire de cette face (petite imprécision)
                surface_area += face.calc_area()
        
        return surface_area

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
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        bm.transform(self.obj.matrix_world)
        
        min_x = self.bbox_min.x
        min_y = self.bbox_min.y
        min_z = self.bbox_min.z
        
        total = 0
        
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
            total += face.calc_area()
            
        bm.free()   
        
        # Pour tester :
        print(f"Aire totale: {total}")                   
                        

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
    start = datetime.now()
    cleanUp()
    obj = get_obj("Cube")
    if(obj == None):
        print("ERROR: L'objet n'a pas été trouvé")
        exit()
        
    grid= Grid(0.1,0,obj)

    #grid.draw()
    
    # Un peu long lorsqu'il y a beaucoup de voxels
    grid.cut_cube_into_voxels()
    
    #grid.compute_areas_in_grid()
    grid.itFaces()
    grid.display()
    #grid.display_voxs()
    fin = datetime.now()
    print(f"Début: {start}\nFin: {fin}\nDurée: {fin-start}")
    

#########################################################################  
                    
main()

# commande terminal pour lancer blender en mode background 
# (ajouter blender dans le PATH C:\Program Files\Blender Foundation\Blender 4.3)
# blender --background C:/Users/antho/Documents/blender/scriptVox/scriptLVoxArea.blend --python C:/Users/antho/Documents/blender/scriptVox/script/computeAreaInVoxGrid.py