# -*-coding:Utf-8 -*

#==========================================================================================
"""

                        FRACTALOID EXPRESS - Mankind - 2016

                        Programme principal - Ze Main One

"""
#==========================================================================================

import gs
import gs.plus.render as render
import gs.plus.scene as scene
import gs.plus.input as input
import gs.plus.camera as camera
from Demo.Demo import Demo as Demo
from Demo.SceneBase import Scene_base as Scene_base
from Demo.Scene_01 import Scene_01 as Scene_01
from Demo.Scene_Terrain_Marching import Scene_Terrain_Marching as Scene_Terrain_Marching

# ============================================================================================================================
#                                                   Rendu arrière-plan
# ============================================================================================================================


def pre_scene():
    Demo.rendu.SetWorldMatrix(gs.Matrix4.Identity)
    projection_matrice_mem = Demo.rendu.GetProjectionMatrix()
    view_matrice_mem = Demo.rendu.GetViewMatrix()

    Demo.Scene_actuelle.pre_scene()


    Demo.rendu2d.Flush(Demo.systeme, Demo.rendu)
    Demo.rendu.SetProjectionMatrix(projection_matrice_mem)
    Demo.rendu.SetViewMatrix(view_matrice_mem)


# ============================================================================================================================
#                                        Rendu sprites intriqués, après le rendu de la scène
# ============================================================================================================================


def post_scene():
    Demo.rendu.SetWorldMatrix(gs.Matrix4.Identity)

    Demo.Scene_actuelle.post_scene()

    Demo.rendu2d.Flush(Demo.systeme, Demo.rendu)

# =============================================================================================================================
#               Gestion des scènes
# =============================================================================================================================

def active_scene_actuelle():

    # Connections de la chaîne de rendu:
    Demo.rendu_scene=Demo.Scene_actuelle.scene3d.GetSystem("Renderable")
    Demo.Scene_actuelle.scene3d.GetRenderSignals().frame_complete_signal.Connect(post_scene)
    Demo.Scene_actuelle.scene3d.GetRenderSignals().frame_cleared_signal.Connect(pre_scene)


def desactive_scene_actuelle():

    # Connections de la chaîne de rendu:
    Demo.Scene_actuelle.scene3d.GetRenderSignals().frame_complete_signal.Connect(None)
    Demo.Scene_actuelle.scene3d.GetRenderSignals().frame_cleared_signal.Connect(None)

# =============================================================================================================================
#               Gestion du déroulement de l'action
# =============================================================================================================================


def gestion_signal_scene(signal):
    #if signal==Scene_base.SIG_SCENE00_A_SCENE01:
    #    desactive_scene_actuelle()
    #    Demo.Scene_actuelle=Scene_01
    #    active_scene_actuelle()
    #    Demo.Scene_actuelle.restart(1)

    Demo.signal_scene=Scene_base.SIG_RIEN

# ================================================================
#               Départ programme
# ================================================================

# -----------Initialisation du système de fichiers:

gs.GetFilesystem().Mount(gs.StdFileDriver())  # Racine du projet
gs.GetFilesystem().Mount(gs.StdFileDriver("pkg.core"), "@core")  # Resources du runtime


# ------------Inits des moteurs de rendu:

render.init(1600, 900,"@core", 1)   #x,y, main path, antialiasing (1 à 8)

Demo.init()
Demo.signal_scene=Scene_base.SIG_RIEN

# -----------Init des scènes:
Scene_01.init()
Scene_Terrain_Marching.init()

Demo.Scene_actuelle=Scene_Terrain_Marching

# ----------- Positionnement initial:

active_scene_actuelle()
Demo.Scene_actuelle.restart()

scene.update_scene(Demo.Scene_actuelle.scene3d, 1 / 60)

# ============================================================================================================================
#                                                   BOUCLE PRINCIPALE
# ============================================================================================================================


Demo.depart_demo() #C'est bon, tout est prêt, Le Temps 0 de la demo commence ici...



while render.has_output_window() and not input.key_down(gs.InputDevice.KeyEscape):
    # ---- Mise à jour timing:
    Demo.horloge.Update()
    Demo.temps = Demo.horloge.Get().to_sec()
    Demo.delta_t = Demo.horloge.GetDelta().to_sec()
    Demo.numero_frame+=1

    #------ Premier rendu:
    #Demo.systeme.SetOutputRenderTarget(Demo.pr_fbo_rendu)
    Demo.rendu.SetRenderTarget(Demo.renvoie_fbo(Demo.FBO_RENDU_1))
    #Demo.rendu.Clear(gs.Color(0,0,1,0),1)
    window_size = Demo.rendu.GetDefaultOutputWindow().GetSize()
    Demo.rendu.SetViewport(gs.fRect(0, 0, window_size.x, window_size.y))# fit viewport to texture dimensions

    # ---- Gestion du signal du rendu précedent:
    # Placé ici car il faut laissé au rendu précédent le temps de se dérouler normalement.
    gestion_signal_scene(Demo.signal_scene)


    # ---- Rendu de la scène:

    Demo.Scene_actuelle.maj_cinetique()
    Demo.signal_scene=Demo.Scene_actuelle.maj_physique()  #Si il y a des réactions aux mouvements.

    # ---- Mise à jour Caméra:

    Demo.Scene_actuelle.maj_camera()


    # ----- Edition:

    if input.key_press(gs.InputDevice.KeyF12):
        Demo.Scene_actuelle.edit_id+=1
        if Demo.Scene_actuelle.edit_id>Scene_base.NUM_PAGES_EDIT: Demo.Scene_actuelle.edit_id=0

    if Demo.Scene_actuelle.edit_id!=Scene_base.EDIT_OFF: Demo.drapeau_camera_controle_utilisateur=False
    else: Demo.drapeau_camera_controle_utilisateur=True

    if Demo.Scene_actuelle.edit_id==Scene_base.EDIT_SCENE:
        Demo.Scene_actuelle.edition()
    elif Demo.Scene_actuelle.edit_id==Scene_base.EDIT_FILTRES:
        Demo.Scene_actuelle.edition_filtres()

    # --- Message système:
    if Demo.drapeau_erreur:
        Demo.affiche_message_erreur()
        Demo.drapeau_erreur=False

    # ----- Affichage des sprites de la scène:
    Demo.Scene_actuelle.affiche_sprites_scene()

    # ---- rendu 3d:
    scene.update_scene(Demo.Scene_actuelle.scene3d, Demo.delta_t)

    #----- rendu objets via shaders (raymarching)
    if Demo.Scene_actuelle.drapeau_rendu_shaders:
        Demo.rendu.SetRenderTarget(Demo.renvoie_fbo(Demo.FBO_RENDU_2))
        Demo.Scene_actuelle.affiche_rendu_shaders()

    #------ post-rendu:

    #Demo.systeme.SetOutputRenderTarget(None)
    #Demo.pr_Saturation=0
    Demo.affiche_texture_rendu_aura(Demo.Scene_actuelle.drapeau_rendu_shaders)

    #------ Flip flap flop:
    render.flip()


# -------------- Fin de programme:
