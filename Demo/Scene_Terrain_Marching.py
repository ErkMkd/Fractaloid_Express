# -*-coding:Utf-8 -*

"""
    Fractaloid Express - Mankind - 2016

    Scène Terrain Marching - Où la loco file dans les montagnes.

"""

#Voici la commande qui permet de transcrire la scène au format FBX vers le format utilisé par GameStart:
#fbx_converter_bin.exe "d:/programmation/Fractaloid_Express/Modelisation/scene_terrain_marching/Terrain_marching.fbx" -o "d:/programmation/Fractaloid_Express/scene_terrain_marching" -base-resource-path "d:/programmation/Fractaloid_Express"

import gs
import gs.plus.render as render
import gs.plus.scene as scene
import gs.plus.input as input
import gs.plus.camera as camera
from math import pi, cos, sin, asin, sqrt
from editeur_niveau import *
from Demo.Demo import Demo as Demo
from Demo.SceneBase import Scene_base as Scene_base


class Scene_Terrain_Marching(Scene_base):

    lumiere_ciel=None
    lumiere_soleil=None


    # Données éditeur:
    cube_l_ciel=None
    cube_l_soleil=None

    noeud_actuel=0
    sprite_actuel=0

    edit_id=Scene_base.EDIT_OFF
    drapeau_lumieres_actives=True

    camera_start_pos_mem=None   #La position de départ de la caméra

    #-------- La liste d'affichage des sprites, contient des objets SpriteTransform
    liste_sprites_scene=[]          #Les sprites intégrés à la scène
    liste_sprites_hors_scene=[]     #Les sprites hors scène (habillage visuel)

    #-------- Paramètres rendu shaders:
    drapeau_rendu_shaders=True  #True si la scène comporte des objets rendu via des shaders (raymarching)

    shader_terrain = None

    texture_terrain1 = None
    texture_terrain2 = None
    texture_terrain3 = None

    facteur_echelle_terrain_l1 = None
    facteur_echelle_terrain_l2 = None
    facteur_echelle_terrain_l3 = None
    amplitude_l1=6000
    amplitude_l2=90
    amplitude_l3=1.5

    facteur_precision_distance=1.01

    couleur_neige=None
    couleur_eau=None
    altitude_eau=150

    #--------------------------------------------------------------------------------------------------------------------------------------

    @classmethod
    def init(cls):

        #-------- Environnement:
        cls.couleur_horizon=gs.Color(10./255.,1./255.,5./255.,1.)
        cls.couleur_zenith=gs.Color(70./255.,150./255.,255./255.,1.)
        cls.couleur_ambiante=gs.Color(70./255.,150./255.,255./255.,1.)
        #cls.couleur_ambiante=gs.Color(1,0,0,1)

        #-------- Création de la scène:
        cls.scene3d=scene.new_scene()

        cls.contexte=gs.SceneLoadContext(render.get_render_system())
        #cls.scene3d.Load("scene_terrain_marching/Terrain_Marching.scn",cls.contexte)
        cls.scene3d.Load("scene_01/Gare_test.scn",cls.contexte)
        #----------- Attend que la scène soit accessible:
        scene.update_scene(cls.scene3d,1/60)

        #----------- Prise en main de la scène:
        cls.noeuds=cls.contexte.GetNodes()
        cls.components=cls.scene3d.GetComponents()

        for comp in cls.components:
            if comp.GetAspect()=="Environment":
                cls.environnement=comp
                break

        #----------- Init billboards et shaders:

        cls.init_billboards(cls.noeuds,cls.liste_sprites_scene)
        cls.init_shaders(cls.noeuds)

        #----------- Init environnement:

        cls.environnement.SetBackgroundColor(gs.Color(0.,0.,0.,0))
        cls.environnement.SetFogColor(cls.couleur_zenith)
        cls.environnement.SetFogNear(10)
        cls.environnement.SetFogFar(50)
        cls.environnement.SetAmbientIntensity(.1)
        cls.environnement.SetAmbientColor(cls.couleur_ambiante)

        cls.camera=cls.scene3d.GetNode("Camera")
        cls.camera.GetCamera().SetZNear(.1)
        cls.camera.GetCamera().SetZFar(10000.)
        cls.camera_start_pos_mem=cls.camera.GetTransform().GetPosition()
        #cls.camera.AddComponent(gs.Target())   #Si la caméra suit une cible

        cls.lumiere_ciel=cls.scene3d.GetNode("clair obscur")
        cls.lumiere_soleil=cls.scene3d.GetNode("soleil")
        cls.lumiere_ciel.GetLight().SetDiffuseColor(gs.Color(77./255.,158./255.,255./255.,1.))
        cls.lumiere_soleil.GetLight().SetDiffuseColor(gs.Color(255./255.,250./255.,223./255.,1.))

        cls.lumiere_soleil.GetLight().SetShadow(gs.Light.Shadow_Map)    #Active les ombres portées
        cls.lumiere_soleil.GetLight().SetShadowRange(100)

        cls.lumiere_soleil.GetLight().SetDiffuseIntensity(1.)
        cls.lumiere_soleil.GetLight().SetSpecularIntensity(1.)

        orientation=gs.Vector3(54/180*pi,135/180*pi,0)
        cls.lumiere_ciel.GetTransform().SetRotation(orientation)

        orientation=gs.Vector3(54/180*pi,-45/180*pi,0)
        cls.lumiere_soleil.GetTransform().SetRotation(orientation)

        #cls.lumiere_ciel.GetLight().SetDiffuseIntensity(2.)
        #cls.lumiere_ciel.GetLight().SetSpecularIntensity(2.)



        #-------- Mémorise les intensités lumineuses pour le switch des éclairages:
        noeuds=cls.scene3d.GetNodes()
        for noeud in noeuds:
            if not noeud.GetLight()==None:
                cls.lumieres_intens_mem.append(noeud.GetLight().GetDiffuseIntensity())
                cls.lumieres_intens_mem.append(noeud.GetLight().GetSpecularIntensity())

        #--------Init les variables de shaders:

        #Couleur d'ambiance:
        """
        for noeud in cls.noeuds:
            if not noeud.GetObject()==None:
                obj=noeud.GetObject()
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
        cls.cube_l_ciel=scene.add_cube(cls.scene3d,gs.Matrix4.Identity,0.5,0.5,2.)

        cls.scene3d.SetCurrentCamera(cls.camera)

        scene.update_scene(cls.scene3d,1/60)

        #------------- Filtres:
        Demo.pr_alpha_rendu=0.75
        Demo.pr_alpha_aura=0.5
        Demo.pr_taille_aura=50
        Demo.pr_aura_contraste=2
        Demo.pr_aura_seuil_contraste=0.6

        #-------------- Init le shader de rendu de terrain:
        cls.shader_terrain=Demo.rendu.LoadShader("shaders_marching/terrain_marching_montagnes.isl")
        cls.texture_terrain1=Demo.rendu.LoadTexture("textures/bruit_1024.png")
        cls.texture_terrain2=Demo.rendu.LoadTexture("textures/bruit_512.png")
        cls.texture_terrain3=Demo.rendu.LoadTexture("textures/bruit_512.png")

        cls.facteur_echelle_terrain_l1 = gs.Vector2(20000,20000)
        cls.facteur_echelle_terrain_l2 = gs.Vector2(1000,1000)
        cls.facteur_echelle_terrain_l3 = gs.Vector2(90,90)

        cls.amplitude_l1=6000
        cls.amplitude_l2=90
        cls.amplitude_l3=1.5

        cls.facteur_precision_distance=1.01
        cls.couleur_neige=gs.Color(0.91,0.91,1)
        cls.couleur_eau=gs.Color(117./255.,219./255.,211./255.)
        cls.altitude_eau=15

    #-------------------------------------------------------------------------------------------------------------------------------------------


    @classmethod
    def raz_camera(cls):
        #cls.camera.GetTransform().SetPosition(cls.camera_start_pos_mem)
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
        """
        Demo.rendu2d.Quad(-1, 0, 4000., \
                              -1, 1, 4000., \
                              1., 1, 4000., \
                              1., 0, 4000., \
                              -1, -1, 1, 1, None, cls.couleur_horizon, cls.couleur_zenith,
                              cls.couleur_zenith, cls.couleur_horizon)
        """

    @classmethod
    def post_scene(cls):
        cls.affiche_sprites_hors_scene()
        #On pose ici les affichages des reperes visuels (croix,cercles, lignes...) pour le débugage:
        #Les routines d'affichage sont dans editeur_niveau.py
        if cls.edit_id==Scene_base.EDIT_SCENE:
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
    #                       Affichage via les shaders:
    #----------------------------------------------------------------------------------------------------------------------------------------------
    @classmethod
    def affiche_rendu_shaders(cls):
        window_size=Demo.rendu.GetDefaultOutputWindow().GetSize()
        Demo.rendu.SetViewport(gs.fRect(0, 0, window_size.x, window_size.y))  # fit viewport to window dimensions
        Demo.rendu.Clear(gs.Color(0.,0.,0.,0.))
        Demo.rendu.EnableBlending(False)
        Demo.rendu.SetShader(cls.shader_terrain)
        Demo.rendu.SetShaderTexture("texture_terrain", cls.texture_terrain1)
        Demo.rendu.SetShaderTexture("texture_terrain2", cls.texture_terrain2)
        Demo.rendu.SetShaderTexture("texture_terrain3", cls.texture_terrain3)
        Demo.rendu.SetShaderFloat("ratio_ecran",window_size.y/window_size.x)
        Demo.rendu.SetShaderFloat("distanceFocale",cls.camera.GetCamera().GetZoomFactor()/2.)
        cam=cls.camera.GetTransform()
        camPos=cam.GetPosition()
        Demo.rendu.SetShaderFloat3("obs_pos",camPos.x,camPos.y,camPos.z)
        #matr=cam.GetWorld().GetRotationMatrix()
        #matr.Inverse()
        Demo.rendu.SetShaderMatrix3("obs_mat_normale",cam.GetWorld().GetRotationMatrix())
        Demo.rendu.SetShaderFloat2("facteur_echelle_terrain",cls.facteur_echelle_terrain_l1.x,cls.facteur_echelle_terrain_l1.y)
        Demo.rendu.SetShaderFloat2("facteur_echelle_terrain2",cls.facteur_echelle_terrain_l2.x,cls.facteur_echelle_terrain_l2.y)
        Demo.rendu.SetShaderFloat2("facteur_echelle_terrain3",cls.facteur_echelle_terrain_l3.x,cls.facteur_echelle_terrain_l3.y)
        Demo.rendu.SetShaderFloat("amplitude_terrain",cls.amplitude_l1)
        Demo.rendu.SetShaderFloat("amplitude_terrain2",cls.amplitude_l2)
        Demo.rendu.SetShaderFloat("amplitude_terrain3",cls.amplitude_l3)
        Demo.rendu.SetShaderFloat("facteur_precision_distance",cls.facteur_precision_distance)
        Demo.rendu.SetShaderFloat("altitude_eau",cls.altitude_eau)
        Demo.rendu.SetShaderFloat3("couleur_zenith",cls.couleur_zenith.r,cls.couleur_zenith.g,cls.couleur_zenith.b)
        Demo.rendu.SetShaderFloat3("couleur_horizon",cls.couleur_horizon.r,cls.couleur_horizon.g,cls.couleur_horizon.b)
        Demo.rendu.SetShaderFloat3("couleur_neige",cls.couleur_neige.r,cls.couleur_neige.g,cls.couleur_neige.b)
        Demo.rendu.SetShaderFloat3("couleur_eau",cls.couleur_eau.r,cls.couleur_eau.g,cls.couleur_eau.b)

        l_dir=cls.lumiere_soleil.GetTransform().GetWorld().GetRotationMatrix().GetZ()
        Demo.rendu.SetShaderFloat3("l1_direction",l_dir.x,l_dir.y,l_dir.z)
        l_couleur=cls.lumiere_soleil.GetLight().GetDiffuseColor()
        Demo.rendu.SetShaderFloat3("l1_couleur",l_couleur.r,l_couleur.g,l_couleur.b)

        l_dir=cls.lumiere_ciel.GetTransform().GetWorld().GetRotationMatrix().GetZ()
        Demo.rendu.SetShaderFloat3("l2_direction",l_dir.x,l_dir.y,l_dir.z)
        l_couleur=cls.lumiere_ciel.GetLight().GetDiffuseColor()
        Demo.rendu.SetShaderFloat3("l2_couleur",l_couleur.r,l_couleur.g,l_couleur.b)

        Demo.rendu.SetShaderFloat2("zFrustum",cls.camera.GetCamera().GetZNear(),cls.camera.GetCamera().GetZFar())

        Demo.affiche_texture_rendu()
        pass

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
    def edition_filtres(cls):
        maj_filtres()
        affiche_parametres_filtres()


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
                    if not noeud.GetLight()==None:
                        noeud.GetLight().SetDiffuseIntensity(0.)
                        noeud.GetLight().SetSpecularIntensity(0.)
            else:
                i=0
                for noeud in noeuds:
                    if not noeud.GetLight()==None:
                        noeud.GetLight().SetDiffuseIntensity(cls.lumieres_intens_mem[2*i])
                        noeud.GetLight().SetSpecularIntensity(cls.lumieres_intens_mem[2*i+1])
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


        cls.cube_l_ciel.GetTransform().SetPosition(cls.lumiere_ciel.GetTransform().GetPosition())
        cls.cube_l_ciel.GetTransform().SetRotation(cls.lumiere_ciel.GetTransform().GetRotation())
        cls.cube_l_soleil.GetTransform().SetPosition(cls.lumiere_soleil.GetTransform().GetPosition())
        cls.cube_l_soleil.GetTransform().SetRotation(cls.lumiere_soleil.GetTransform().GetRotation())
