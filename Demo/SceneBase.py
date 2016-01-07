# -*-coding:Utf-8 -*

"""
    Fractaloid Express - Mankind - 2016

    Classe de base des scènes

    Chunk d'identification des objets, à partir du nom des "object":

        bb. :   BillBoard, ces objets sont convertis en billboards.
                Les noeuds sont supprimés et les billboards sont transférés dans la liste d'affichage des sprites de scène.

    Chunks d'identification des shaders, à partir du nom des matériaux:

        bk00 : constant_map.isl - Texture entièrement bakée
        oc01 : ocean.isl - Surface de l'océan n°1
        oc02:  ocean_proche.isl - Surface de l'océan au premier plan
        em01:  diffuse_constant.isl - Surface émettrice de lumière, sans texture (ampoules)
        tr01:  diffuse_alpha.isl - Surface transparente, sans texture (vitres propres)

"""

import gs
import gs.plus.scene as scene
import gs.plus.camera as camera

from Demo.Sprites import BillBoard as BillBoard
from Demo.Demo import Demo as Demo
from operator import attrgetter

#==========================================================
#           Scène de base, classe virtuelle
#       Les scènes sont des classes statiques.
#==========================================================


class Scene_base:

    #==== Les signaux globals de scène, qui servent à l'enchaînement des tableaux:
    SIG_RIEN=0

    scene3d=None
    contexte=None
    components=None
    environnement=None
    couleur_horizon=gs.Color(170/255,237/255,255/255)
    couleur_zenith=gs.Color(130/255,197/255,255/255)
    couleur_ambiante=gs.Color(19/255,42/255,63/255)
    camera=None
    signal=SIG_RIEN

    #-------- La liste d'affichage des sprites, contient des objets SpriteTransform
    #liste_sprites_scene=[]          #Les sprites intégrés à la scène
    #liste_sprites_hors_scene=[]     #Les sprites hors scène (habillage visuel)

    #-------- Données pour le mini-éditeur embarqué, à supprimer après le dev:
    EDIT_OFF=0
    EDIT_SCENE=1
    EDIT_FILTRES=2
    NUM_PAGES_EDIT=2

    edit_id=EDIT_SCENE

    #---------

    fps=None    #Controle manuel de la caméra
    lumieres_intens_mem=[]

    @classmethod
    def init(cls):
        raise NotImplementedError

    @classmethod
    def init_billboards(cls,noeuds,liste):
        for noeud in noeuds:
            nom=noeud.GetName()
            bb_chunk=nom[0]+nom[1]+nom[2]
            if bb_chunk=="bb.":
                materiau=noeud.GetObject().GetGeometry().GetMaterial(0)
                texture=materiau.GetTexture("diffuse_map")
                #shader=Demo.systeme.LoadSurfaceShader("shaders/sprite_alpha.isl",False)
                materiau.SetSurfaceShader(Demo.shader_billboards)
                materiau.SetTexture("diffuse_map",texture)
                cls.scene3d.RemoveNode(noeud)
                bill=BillBoard()
                bill.convertion_node(noeud)
                liste.append(bill)

    @classmethod
    def init_shaders(cls,noeuds):
        for noeud in noeuds:
            if noeud.GetObject() is not None:
                geo=noeud.GetObject().GetGeometry()
                i=geo.GetMaterialCount()
                n=0
                while n<i:
                    materiau=geo.GetMaterial(n)
                    nom=materiau.GetName()
                    #Cherche le départ du chunk, grace au caractère '#'
                    of7=0
                    shader_ok=False
                    for htag in nom:
                        if htag=='#':
                            shader_ok=True
                            break
                        of7+=1
                    if shader_ok:
                        chunk=nom[of7+1]+nom[of7+2]+nom[of7+3]+nom[of7+4]
                        if chunk=="bk00":
                            texture=materiau.GetTexture("diffuse_map")
                            materiau.SetSurfaceShader(Demo.shader_constant_map)
                            materiau.SetTexture("diffuse_map",texture)
                        elif chunk=="oc01":
                            texture=materiau.GetTexture("diffuse_map")
                            materiau.SetSurfaceShader(Demo.shader_ocean_01)
                            materiau.SetTexture("texture_couleur",texture)
                            materiau.SetTexture("texture_bruit",Demo.texture_bruit_01)
                        elif chunk=="oc02":
                            texture=materiau.GetTexture("diffuse_map")
                            materiau.SetSurfaceShader(Demo.shader_ocean_02)
                            materiau.SetTexture("texture_couleur",texture)
                            materiau.SetTexture("texture_bruit",Demo.texture_bruit_01)
                        elif chunk=="em01":
                            couleur=gs.Color()
                            couleur.r,couleur.g,couleur.b,couleur.a=materiau.GetFloat4("diffuse_color")
                            print(materiau.GetName()+" R:"+str(couleur.r)+" G:"+str(couleur.g)+" B:"+str(couleur.b))
                            materiau.SetSurfaceShader(Demo.shader_constant)
                            materiau.SetFloat4("diffuse_color",couleur.r,couleur.g,couleur.b,couleur.a)
                        elif chunk=="tr01":
                            couleur=gs.Color()
                            couleur.r,couleur.g,couleur.b,couleur.a=materiau.GetFloat4("diffuse_color")
                            materiau.SetSurfaceShader(Demo.shader_transparent)
                            materiau.SetFloat4("diffuse_color",couleur.r,couleur.g,couleur.b,couleur.a/2)

                    n+=1

    @classmethod
    def raz_camera(cls):
        raise NotImplementedError

    @classmethod
    def raz_jeu(cls):
        raise NotImplementedError
    @classmethod
    def raz_temps(cls):
        raise NotImplementedError

    @classmethod
    def restart(cls,id_point_depart=1):
        raise NotImplementedError

    @classmethod
    def tri_sprites(cls,liste,camera):
        if len(liste)>0:
            camPos = camera.GetTransform().GetWorld().GetTranslation()
            for sprite in liste:
                sprPos=camPos-gs.Vector3(sprite.x,sprite.y,sprite.z)
                sprite.distance_camera=sprPos.Len()
            return sorted(liste,key=attrgetter("distance_camera"),reverse=True)
        else: return liste

    @classmethod
    def affiche_sprites_hors_scene(cls,liste):
        for sprite in liste:
            sprite.affiche()

    @classmethod
    def affiche_sprites_scene(cls,liste):
        #print ("----------------------")
        for sprite in liste:
            sprite.affiche_geometrie()
            #print (str(sprite.distance_camera))

    #Méthode où sont rendu les objets en raymarching, pour une fusion avec la scène 3d classique:
    @classmethod
    def affiche_rendu_shaders(cls):
        raise NotImplementedError

    @classmethod
    def pre_scene(cls):
        raise NotImplementedError

    @classmethod
    def post_scene(cls):
        raise NotImplementedError

    @classmethod
    def maj_cinetique(cls):
        raise NotImplementedError

    #Avant la mise à jour de Danel
    @classmethod
    def maj_physique(cls):
        raise NotImplementedError

    @classmethod
    def maj_cinetique_personnages(cls):
        raise NotImplementedError

    @classmethod
    def maj_physique_personnages(cls):
        raise NotImplementedError

    @classmethod
    def interaction_Danel(cls):
        raise NotImplementedError

    @classmethod
    def maj_camera(cls):
        raise NotImplementedError

    @classmethod

    def renvoie_position_ecran(cls,point):
        """
        Renvoie les limites du champ de vision à la profondeur en entrée.
        La caméra doit être orienté vers l'axe des Z
        :param point: gs.Vector3(x,y,z)
        :return: gs.Vector3(x_ecran,y_ecran,z=0)
        """
        #drapeau,position=gs.Project(cls.camera.GetCamera(),cls.camera.GetTransform(),gs.Vector2(16/9,1),point)
        drapeau,position=gs.Project(cls.camera.GetTransform().GetWorld(),cls.camera.GetCamera().GetZoomFactor(),Demo.rendu.GetAspectRatio(),point)
        return position

    @classmethod
    def edition(cls):
        raise NotImplementedError

    @classmethod
    def edition_filtres(cls):
        raise NotImplementedError

