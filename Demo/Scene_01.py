# -*-coding:Utf-8 -*

"""
    Fractaloid Express - Mankind - 2016

    Scène 1 - La gare

"""

#Voici la commande qui permet de transcrire la scène au format FBX vers le format utilisé par GameStart:
#fbx_converter_bin.exe "d:/programmation/Fractaloid_Express/Modelisation/scene_01/Gare_test.fbx" -o "d:/programmation/Fractaloid_Express/scene_01" -base-resource-path "d:/programmation/Fractaloid_Express"

import gs
import gs.plus.render as render
import gs.plus.scene as scene
import gs.plus.input as input
import gs.plus.camera as camera
from math import pi, cos, sin, asin, sqrt
from editeur_niveau import *
from Demo.Demo import Demo as Demo
from Demo.SceneBase import Scene_base as Scene_base


class Scene_01(Scene_base):

    lumiere_clair_obscur=None
    lumiere_soleil=None


    # Données éditeur:
    cube_l_clair_obscur=None
    cube_l_soleil=None

    noeud_actuel=0
    sprite_actuel=0

    drapeau_edition=False
    drapeau_lumieres_actives=True

    camera_start_pos_mem=None   #La position de départ de la caméra

    #-------- La liste d'affichage des sprites, contient des objets SpriteTransform
    liste_sprites_scene=[]          #Les sprites intégrés à la scène
    liste_sprites_hors_scene=[]     #Les sprites hors scène (habillage visuel)

    #--------------------------------------------------------------------------------------------------------------------------------------

    @classmethod
    def init(cls):

        #-------- Environnement:
        cls.couleur_horizon=gs.Color(1.,.699,.586)
        cls.couleur_zenith=gs.Color(1.,0.978,0.407)
        cls.couleur_ambiante=gs.Color(0.019,0.042,0.034)

        #-------- Création de la scène:
        cls.scene3d=scene.new_scene()

        cls.contexte=gs.SceneLoadContext(render.get_render_system())
        cls.scene3d.Load("scene_01/Gare_test.scn",cls.contexte)
        #----------- Attend que la scène soit accessible:
        scene.update_scene(cls.scene3d,1/60)

        #----------- Prise en main de la scène:
        cls.noeuds=cls.contexte.GetNodes()
        cls.components=cls.scene3d.GetComponents()

        for comp in cls.components:
            if comp.GetName()=="Environment":
                cls.environnement=comp
                break

        #----------- Init billboards et shaders:

        cls.init_billboards(cls.noeuds,cls.liste_sprites_scene)
        cls.init_shaders(cls.noeuds)

        #----------- Init environnement:

        cls.environnement.SetBackgroundColor(cls.couleur_horizon)
        cls.environnement.SetFogColor(cls.couleur_horizon)
        cls.environnement.SetFogNear(1)
        cls.environnement.SetFogFar(100)
        cls.environnement.SetAmbientIntensity(2.)
        cls.environnement.SetAmbientColor(cls.couleur_ambiante)

        cls.camera=cls.scene3d.GetNode("Camera")
        cls.camera.camera.SetZNear(.1)
        cls.camera.camera.SetZFar(1000.)
        cls.camera_start_pos_mem=cls.camera.transform.GetPosition()
        #cls.camera.AddComponent(gs.Target())   #Si la caméra suit une cible

        cls.lumiere_clair_obscur=cls.scene3d.GetNode("clair obscur")
        cls.lumiere_soleil=cls.scene3d.GetNode("soleil")

        cls.lumiere_soleil.light.SetShadow(gs.Light.Shadow_Map)    #Active les ombres portées
        cls.lumiere_soleil.light.SetShadowRange(100)

        cls.lumiere_soleil.light.SetDiffuseIntensity(2.)
        cls.lumiere_soleil.light.SetSpecularIntensity(2.)

        orientation=gs.Vector3(54/180*pi,135/180*pi,0)
        cls.lumiere_clair_obscur.transform.SetRotation(orientation)

        orientation=gs.Vector3(54/180*pi,-45/180*pi,0)
        cls.lumiere_soleil.transform.SetRotation(orientation)

        #cls.lumiere_clair_obscur.light.SetDiffuseIntensity(2.)
        #cls.lumiere_clair_obscur.light.SetSpecularIntensity(2.)



        #-------- Mémorise les intensités lumineuses pour le switch des éclairages:
        noeuds=cls.scene3d.GetNodes()
        for noeud in noeuds:
            if not noeud.light==None:
                cls.lumieres_intens_mem.append(noeud.light.GetDiffuseIntensity())
                cls.lumieres_intens_mem.append(noeud.light.GetSpecularIntensity())

        #--------Init les variables de shaders:

        #Couleur d'ambiance:
        """
        for noeud in cls.noeuds:
            if not noeud.object==None:
                obj=noeud.object
                geo=obj.GetGeometry()
                n=geo.GetMaterialCount()
                i=0
                while i<n:
                    materiau=geo.GetMaterial(i)
                    materiau.SetFloat3("ambient_color",cls.couleur_ambiante.r*0.,cls.couleur_ambiante.g*0.,cls.couleur_ambiante.b*0.)
                    i+=1
        """
        #--------- Init listes des sprites:
        #cls.liste_sprites_scene.append(...)


        #--------- Inits de l'éditeur embarqué
        cls.cube_l_soleil=scene.add_cube(cls.scene3d,gs.Matrix4.Identity,0.5,0.5,2.)
        cls.cube_l_clair_obscur=scene.add_cube(cls.scene3d,gs.Matrix4.Identity,0.5,0.5,2.)

        cls.scene3d.SetCurrentCamera(cls.camera)

        scene.update_scene(cls.scene3d,1/60)

    #-------------------------------------------------------------------------------------------------------------------------------------------


    @classmethod
    def raz_camera(cls):
        #cls.camera.transform.SetPosition(cls.camera_start_pos_mem)
        cls.fps=camera.fps_controller(cls.camera_start_pos_mem.x,cls.camera_start_pos_mem.y,cls.camera_start_pos_mem.z)

    @classmethod
    def raz_demo(cls):
        pass

    @classmethod
    def raz_temps(cls):
        pass

    @classmethod
    def restart(cls,id_point_depart=1):
        cls.signal=Scene_base.SIG_RIEN
        cls.raz_temps()
        if id_point_depart==1:
            cls.raz_camera()

        elif id_point_depart==2:
            pass


        scene.update_scene(cls.scene3d,1./60.)

    #----------------------------------------------------------------------------------------------------------------------------------------------

    @classmethod
    def pre_scene(cls):

        #---Projection ortho:
        projection_matrice_ortho = gs.ComputeOrthographicProjectionMatrix(1., 500., 2, gs.Vector2(1, 1))
        Demo.rendu.SetProjectionMatrix(projection_matrice_ortho)
        Demo.rendu.SetViewMatrix(gs.Matrix4.Identity)

        #Affiche le ciel:
        Demo.rendu2d.Quad(-1, 0, 400., \
                              -1, 1, 400., \
                              1., 1, 400., \
                              1., 0, 400., \
                              -1, -1, 1, 1, None, cls.couleur_horizon, cls.couleur_zenith,
                              cls.couleur_zenith, cls.couleur_horizon)

    @classmethod
    def post_scene(cls):
        cls.affiche_sprites_hors_scene()
        #On pose ici les affichages des reperes visuels (croix,cercles, lignes...) pour le débugage:
        #Les routines d'affichage sont dans editeur_niveau.py
        if cls.drapeau_edition:
            pass

    #----------------------------------------------------------------------------------------------------------------------------------------------
    #                       Affichage des listes de sprites:
    #----------------------------------------------------------------------------------------------------------------------------------------------
    @classmethod
    def affiche_sprites_scene(cls):
        #cls.liste_sprites_scene=cls.tri_sprites(cls.liste_sprites_scene,cls.camera)
        Scene_base.affiche_sprites_scene(cls.liste_sprites_scene)

    @classmethod
    def affiche_sprites_hors_scene(cls):
        #cls.liste_sprites_hors_scene=cls.tri_sprites(cls.liste_sprites_hors_scene,cls.camera)
        Scene_base.affiche_sprites_hors_scene(cls.liste_sprites_hors_scene)

    #----------------------------------------------------------------------------------------------------------------------------------------------
    #                       Fonctions principales
    #----------------------------------------------------------------------------------------------------------------------------------------------


    #--------------------------- Mise à jour de la cinétique de la scène :

    @classmethod
    def maj_cinetique(cls):
        pass

    #--------------------------- Mise à jour de la physique de la scène :
    @classmethod
    def maj_physique(cls):
        return cls.signal


    #------------- Mise à jour caméra:

    @classmethod
    def maj_camera(cls):
        #pass
        if Demo.drapeau_camera_controle_utilisateur:
            cls.fps.update_and_apply_to_node(cls.camera,Demo.delta_t)


    #----------------------------------------------------------------------------------------------------------------------------------------------



    @classmethod
    def edition(cls):
        noeuds=cls.scene3d.GetNodes()
        if input.key_press(gs.InputDevice.KeySpace):
            if input.key_down(gs.InputDevice.KeyLShift):
                cls.noeud_actuel-=1
                if cls.noeud_actuel<0:
                    cls.noeud_actuel=len(noeuds)-1
            else:
                cls.noeud_actuel+=1
                if cls.noeud_actuel>=len(noeuds):
                    cls.noeud_actuel=0

        if input.key_press(gs.InputDevice.KeyBackspace):
            cls.drapeau_lumieres_actives=not cls.drapeau_lumieres_actives
            if not cls.drapeau_lumieres_actives:
                for noeud in noeuds:
                    if not noeud.light==None:
                        noeud.light.SetDiffuseIntensity(0.)
                        noeud.light.SetSpecularIntensity(0.)
            else:
                i=0
                for noeud in noeuds:
                    if not noeud.light==None:
                        noeud.light.SetDiffuseIntensity(cls.lumieres_intens_mem[2*i])
                        noeud.light.SetSpecularIntensity(cls.lumieres_intens_mem[2*i+1])
                        i+=1

        listing_sprites(cls.liste_sprites_scene,cls.sprite_actuel,gs.Color.Red,gs.Color.Green)
        listing_noeuds(noeuds,cls.noeud_actuel,gs.Color.Red,gs.Color.Green)
        listing_components(cls.components,0)
        affiche_donnees_environnement(cls.environnement,300,450)
        affiche_donnees_camera(cls.camera,300)
        affiche_donnees_lumiere(cls.lumiere_soleil,600)
        affiche_donnees_noeud(noeuds[cls.noeud_actuel],  gs.Color.Yellow)
        maj_zoom(cls.camera)
        edit_noeud(noeuds[cls.noeud_actuel])


        cls.cube_l_clair_obscur.transform.SetPosition(cls.lumiere_clair_obscur.transform.GetPosition())
        cls.cube_l_clair_obscur.transform.SetRotation(cls.lumiere_clair_obscur.transform.GetRotation())
        cls.cube_l_soleil.transform.SetPosition(cls.lumiere_soleil.transform.GetPosition())
        cls.cube_l_soleil.transform.SetRotation(cls.lumiere_soleil.transform.GetRotation())
