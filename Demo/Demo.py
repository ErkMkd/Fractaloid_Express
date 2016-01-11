# -*-coding:Utf-8 -*

"""
    Fractaloid Express - Mankind - 2016

    Données globales et template de la classe principale

"""

import gs
import gs.plus.render as render
import gs.plus.input as input
from math import tan

#======================================================================
#          The Classe principale, qui regroupe les variables globales
#       Les scènes sont des classes statiques.
#======================================================================

class Demo:

    #--------- Constantes de gestion des framebuffer objects:
    TAILLE_FBO_LO=256 #Résolution des textures de rendu basse résolution (utilisées pour les filtres glow par exemple)
    FBO_RENDU_1=0
    FBO_RENDU_2=1
    FBO_RENDU_3=2
    FBO_LOW_1=3
    FBO_LOW_2=4

    NUM_FBOS=5


    #------------ Variables:
    temps=0
    delta_t=0
    numero_frame=0

    systeme=None
    rendu=None
    rendu2d=None
    rendu_scene=None #Pour afficher un objet complètement intégré à la scène
    clavier=None
    horloge=None

    police=None
    police2=None

    Scene_actuelle=None
    signal_scene=0

    texture_ombre_sol=None
    texture_bruit_01=None #Bruit de Perlin

    drapeau_camera_controle_utilisateur=True #True si on peut controler la caméra
    message_erreur={""}
    drapeau_erreur=False

    audio=None

     #--------- Shaders:
    shader_billboards=None
    shader_constant_map=None
    shader_constant=None
    shader_ocean_01=None
    shader_ocean_02=None
    shader_transparent=None

    #--------- Post-rendu:
    pr_shader_filtres_basiques=None #Le shader de base du traitement post-rendu sans aura
    pr_shader_affiche_texture_2d=None #Simple affichage de texture, avec réglage de l'alpha.
    pr_shader_affiche_2_textures_2d=None #Simple affichage de deux textures, avec réglage des alphas.
    pr_shader_2_textures_filtres=None #Fusionne 2 textures et applique des filtres.
    pr_shader_3_textures_filtres=None #Fusionne 2 textures de scènes et une pour l'aura et applique des filtres.
    pr_shader_fusion_2_textures_depth=None #Fusionne 2 textures de scènes, grace à leurs depth buffer

    pr_shader_contraste=None    #Shaders pour le rendu des auras
    pr_shader_flou_x=None
    pr_shader_flou_y=None
    pr_shader_filtre_HSV=None   #Shader final pour un réglage des couleurs.

    pr_indices=None
    pr_vertex_layout=None
    pr_vertex=None

    pr_fbo_rendu_1=None #FBO hi res pour rendu scènes.
    pr_fbo_rendu_2=None
    pr_fbo_rendu_3=None

    pr_texture_rendu_1=None
    pr_texture_rendu_2=None
    pr_texture_rendu_3=None

    pr_texture_rendu_1_depth=None
    pr_texture_rendu_2_depth=None
    pr_texture_rendu_3_depth=None

    pr_fbo_low_1=None   #FBO basse résolution pour certains effets (glow)
    pr_fbo_low_2=None

    pr_texture_low_1=None
    pr_texture_low_2=None

    pr_fbos=[] #Table des FBO, c'est plus simple à gérer via les id définis plus haut.
    pr_textures=[]
    pr_textures_depth=[]

    #----------- Paramètres filtres:

    pr_taille_aura=20
    pr_intensite_aura=1

    pr_aura_contraste=3
    pr_aura_seuil_contraste=0.75
    pr_aura_hue=5
    pr_aura_saturation=1
    pr_aura_value=1.

    pr_alpha_aura=0.5
    pr_alpha_rendu=0.5

    pr_Contraste=0
    pr_Seuil_contraste=0.5
    pr_Hue=0
    pr_Saturation=1
    pr_Value=1.

    #------------ Affiche un message d'erreur à l'écran:
    @classmethod
    def affiche_message_erreur(cls):
        y=450
        for message in cls.message_erreur:
            render.text2d(400,y,message,16, gs.Color.Red)
            y-=20

    @classmethod
    def calcul_distance_focale(cls,camera):
        cam=camera.GetCamera()
        Fov=gs.ZoomFactorToFov(cam.GetZoomFactor())
        return 1./(2.*tan(Fov/2.))

    #------------------------------------------------------
    #   Initialisation des paramètres globaux du jeu
    #------------------------------------------------------
    @classmethod
    def init(cls):
        cls.rendu = render.get_renderer()
        cls.clavier = input.get_keyboard()

        cls.systeme = render.get_render_system()

        cls.rendu2d = gs.SimpleGraphicEngine()
        cls.rendu2d.SetDepthWrite(False)
        cls.rendu2d.SetDepthTest(True)
        cls.rendu2d.SetBlendMode(gs.BlendAlpha)
        cls.rendu_scene=None    #Initialisé à chaque activation de scène

        cls.texture_ombre_sol=Demo.rendu.LoadTexture("textures/ombre_sol.png")
        cls.texture_bruit_01=Demo.rendu.LoadTexture("textures/bruit_01.png")

        if cls.texture_ombre_sol is None or cls.texture_bruit_01 is None:
            cls.message_erreur="Impossible de charger les textures de base"
            cls.drapeau_erreur=True

        #Shaders par défaut:
        cls.shader_billboards=cls.systeme.LoadSurfaceShader("shaders/sprite_alpha.isl",False)
        cls.shader_constant_map=cls.systeme.LoadSurfaceShader("shaders/constant_map.isl",False)
        cls.shader_constant=cls.systeme.LoadSurfaceShader("shaders/diffuse_constante.isl",False)
        cls.shader_ocean_01=cls.systeme.LoadSurfaceShader("shaders/ocean.isl",False)
        cls.shader_ocean_02=cls.systeme.LoadSurfaceShader("shaders/ocean_proche.isl",False)
        cls.shader_transparent=cls.systeme.LoadSurfaceShader("shaders/diffuse_alpha.isl",False)

        #Init le post-rendu:
        cls.init_post_rendu()

        #Init le gestionnaire sonore:
        cls.audio = gs.ALMixer()
        cls.audio.Open()

    #------------------------------------------------------
    #   Initialisation du sytème de post-rendu
    #------------------------------------------------------
    @classmethod
    def init_post_rendu(cls):
        #Init les shaders de post rendu:
        cls.pr_shader_filtres_basiques = cls.rendu.LoadShader("shaders/filtre_basique.isl")
        cls.pr_shader_affiche_texture_2d = cls.rendu.LoadShader("shaders/affiche_texture_2d.isl")
        cls.pr_shader_affiche_2_textures_2d = cls.rendu.LoadShader("shaders/affiche_2_textures_2d.isl")
        cls.pr_shader_2_textures_filtres = cls.rendu.LoadShader("shaders/2_textures_filtres.isl")
        cls.pr_shader_3_textures_filtres = cls.rendu.LoadShader("shaders/3_textures_filtres.isl")
        cls.pr_shader_fusion_2_textures_depth = cls.rendu.LoadShader("shaders/fusion_2_textures_depth.isl")

        cls.pr_shader_contraste = cls.rendu.LoadShader("shaders/filtre_contraste.isl")
        cls.pr_shader_flou_x = cls.rendu.LoadShader("shaders/flou_x.isl")
        cls.pr_shader_flou_y = cls.rendu.LoadShader("shaders/flou_y.isl")
        cls.pr_shader_filtre_HSV = cls.rendu.LoadShader("shaders/filtre_HSV.isl")


        # create primitive index buffer
        data = gs.BinaryBlob()
        data.WriteShorts([0, 1, 2, 0,2,3])

        cls.pr_indices = cls.rendu.NewBuffer()
        cls.rendu.CreateBuffer(cls.pr_indices, data, gs.GpuBuffer.Index)

        # create primitive vertex buffer
        cls.pr_vertex_layout = gs.VertexLayout()
        cls.pr_vertex_layout.AddAttribute(gs.VertexAttribute.Position, 3, gs.ValueFloat)
        cls.pr_vertex_layout.AddAttribute(gs.VertexAttribute.UV0, 2, gs.ValueUByte, True)  # UVs are sent as normalized 8 bit unsigned integer (range [0;255])

        data = gs.BinaryBlob()
        x, y = 1, 1
        data.WriteFloats([-x, -y, 0.5])
        data.WriteUnsignedBytes([0, 0])

        data.WriteFloats([-x, y, 0.5])
        data.WriteUnsignedBytes([0, 255])

        data.WriteFloats([x, y, 0.5])
        data.WriteUnsignedBytes([255, 255])

        data.WriteFloats([x, -y, 0.5])
        data.WriteUnsignedBytes([255, 0])

        cls.pr_vertex = cls.rendu.NewBuffer()
        cls.rendu.CreateBuffer(cls.pr_vertex, data, gs.GpuBuffer.Vertex)

        # Création des textures de rendu:
        window_size = cls.rendu.GetDefaultOutputWindow().GetSize()
        cls.pr_texture_rendu_1 = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_1, window_size.x, window_size.y,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)
        cls.pr_texture_rendu_1_depth = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_1_depth, window_size.x, window_size.y,gs.GpuTexture.Depth,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)

        cls.pr_texture_rendu_2 = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_2, window_size.x, window_size.y,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)
        cls.pr_texture_rendu_2_depth = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_2_depth, window_size.x, window_size.y,gs.GpuTexture.Depth,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)

        cls.pr_texture_rendu_3 = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_3, window_size.x, window_size.y,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)
        cls.pr_texture_rendu_3_depth = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_3_depth, window_size.x, window_size.y,gs.GpuTexture.Depth,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)

        cls.pr_texture_low_1 = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_low_1, cls.TAILLE_FBO_LO, cls.TAILLE_FBO_LO,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)
        cls.pr_texture_low_2 = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_low_2, cls.TAILLE_FBO_LO, cls.TAILLE_FBO_LO,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)


        # Création des frameBuffer objects:
        cls.pr_fbo_rendu_1 = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_rendu_1)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_rendu_1, cls.pr_texture_rendu_1)
        cls.rendu.SetRenderTargetDepthTexture(cls.pr_fbo_rendu_1, cls.pr_texture_rendu_1_depth)

        cls.pr_fbo_rendu_2 = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_rendu_2)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_rendu_2, cls.pr_texture_rendu_2)
        cls.rendu.SetRenderTargetDepthTexture(cls.pr_fbo_rendu_2, cls.pr_texture_rendu_2_depth)

        cls.pr_fbo_rendu_3 = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_rendu_3)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_rendu_3, cls.pr_texture_rendu_3)
        cls.rendu.SetRenderTargetDepthTexture(cls.pr_fbo_rendu_3, cls.pr_texture_rendu_3_depth)

        cls.pr_fbo_low_1 = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_low_1)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_low_1, cls.pr_texture_low_1)

        cls.pr_fbo_low_2 = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_low_2)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_low_2, cls.pr_texture_low_2)

        #Init les tables des fbo:
        cls.pr_fbos=[cls.pr_fbo_rendu_1,cls.pr_fbo_rendu_2,cls.pr_fbo_rendu_3,cls.pr_fbo_low_1,cls.pr_fbo_low_2]
        cls.pr_textures=[cls.pr_texture_rendu_1,cls.pr_texture_rendu_2,cls.pr_texture_rendu_3,cls.pr_texture_low_1,cls.pr_texture_low_2]
        cls.pr_textures_depth=[cls.pr_texture_rendu_1_depth,cls.pr_texture_rendu_2_depth,cls.pr_texture_rendu_3_depth,None,None]

    #================ Affichage du polygone qui occupe l'écran:
    @classmethod
    def affiche_texture_rendu(cls):
        gs.DrawBuffers(cls.rendu, 6, cls.pr_indices, cls.pr_vertex, cls.pr_vertex_layout)

    @classmethod
    def affiche_texture_rendu_basique(cls,id_fbo=FBO_RENDU_1):
        cls.rendu.SetRenderTarget(None)
        window_size = cls.rendu.GetDefaultOutputWindow().GetSize()
        cls.rendu.SetViewport(gs.fRect(0, 0, window_size.x, window_size.y))  # fit viewport to window dimensions
        cls.rendu.Clear(gs.Color.Black)  # red

        cls.rendu.SetShader(Demo.pr_shader_filtres_basiques)
        cls.rendu.SetShaderTexture("u_tex", cls.pr_textures[id_fbo])
        #cls.rendu.SetShaderFloat("saturation", cls.pr_saturation_avec_seuil)
        cls.rendu.SetShaderFloat("contraste", cls.pr_contraste)
        cls.rendu.SetShaderFloat("seuil", cls.pr_seuil_contraste)
        cls.rendu.SetShaderFloat("H", cls.pr_Hue)
        cls.rendu.SetShaderFloat("S", cls.pr_Saturation)
        cls.rendu.SetShaderFloat("V", cls.pr_Value)
        cls.affiche_texture_rendu()

    #===================================================================
    #======= Filtres Glow, et fusion éventuelle avec les objets rendus via les shaders (raymarching surtout):
    #===================================================================

    @classmethod
    def affiche_texture_rendu_aura(cls,drapeau_rendu_shader=False):

        window_size = cls.rendu.GetDefaultOutputWindow().GetSize()
        cls.rendu.EnableBlending(False)
        texture_scene_id=cls.FBO_RENDU_1
        #------ Fusion de deux scènes si besoin:
        if drapeau_rendu_shader:
            cls.rendu.SetRenderTarget(cls.pr_fbos[cls.FBO_RENDU_3])
            cls.rendu.SetViewport(gs.fRect(0, 0, window_size.x,window_size.y))
            cls.rendu.Clear(gs.Color.Black)  # red
            cls.rendu.SetShader(Demo.pr_shader_fusion_2_textures_depth)
            cls.rendu.SetShaderTexture("u_tex_scene1", cls.pr_textures[cls.FBO_RENDU_1])
            cls.rendu.SetShaderTexture("u_tex_scene2", cls.pr_textures[cls.FBO_RENDU_2])
            cls.rendu.SetShaderTexture("u_tex_scene1_depth", cls.pr_textures_depth[cls.FBO_RENDU_1])
            cls.rendu.SetShaderTexture("u_tex_scene2_depth", cls.pr_textures_depth[cls.FBO_RENDU_2])
            cls.affiche_texture_rendu()
            texture_scene_id=cls.FBO_RENDU_3


        #------ Contraste pour isoler les surfaces claires:
        cls.rendu.SetRenderTarget(cls.pr_fbos[cls.FBO_LOW_1])
        cls.rendu.SetViewport(gs.fRect(0, 0, cls.TAILLE_FBO_LO, cls.TAILLE_FBO_LO))
        cls.rendu.Clear(gs.Color.Black)  # red


        cls.rendu.SetShader(Demo.pr_shader_filtres_basiques)
        cls.rendu.SetShaderTexture("u_tex", cls.pr_textures[texture_scene_id])
        cls.rendu.SetShaderFloat("contraste", cls.pr_aura_contraste)
        cls.rendu.SetShaderFloat("seuil", cls.pr_aura_seuil_contraste)
        cls.rendu.SetShaderFloat("H", cls.pr_aura_hue)
        cls.rendu.SetShaderFloat("S", cls.pr_aura_saturation)
        cls.rendu.SetShaderFloat("V", cls.pr_aura_value)
        cls.affiche_texture_rendu()


        #--------- Floutage X:
        cls.rendu.SetRenderTarget(cls.pr_fbos[cls.FBO_LOW_2])
        cls.rendu.SetShader(Demo.pr_shader_flou_x)
        cls.rendu.SetShaderTexture("u_tex", cls.pr_textures[cls.FBO_LOW_1])
        #cls.rendu.SetShaderFloat("saturation", cls.pr_saturation_avec_seuil)
        cls.rendu.SetShaderInt("taille_flou", cls.pr_taille_aura)
        cls.rendu.SetShaderFloat("saturation_flou", cls.pr_intensite_aura)
        cls.rendu.SetShaderFloat("taille_texture", window_size.x)
        cls.affiche_texture_rendu()

        #--------- Floutage Y:
        cls.rendu.SetRenderTarget(cls.pr_fbos[cls.FBO_LOW_1])
        cls.rendu.SetShader(Demo.pr_shader_flou_y)
        cls.rendu.SetShaderTexture("u_tex", cls.pr_textures[cls.FBO_LOW_2])
        #cls.rendu.SetShaderFloat("saturation", cls.pr_saturation_avec_seuil)
        cls.rendu.SetShaderInt("taille_flou", cls.pr_taille_aura)
        cls.rendu.SetShaderFloat("saturation_flou", cls.pr_intensite_aura)
        cls.rendu.SetShaderFloat("taille_texture", window_size.y)
        cls.affiche_texture_rendu()

        #--------- Superposition des textures et filtre final:

        cls.rendu.SetRenderTarget(None)
        cls.rendu.SetViewport(gs.fRect(0, 0, window_size.x, window_size.y))  # fit viewport to window dimensions
        cls.rendu.Clear(gs.Color.Black)
        cls.rendu.SetShader(Demo.pr_shader_2_textures_filtres)
        cls.rendu.SetShaderTexture("u_tex1", cls.pr_textures[texture_scene_id])
        cls.rendu.SetShaderTexture("u_tex2", cls.pr_textures[cls.FBO_LOW_1])
        cls.rendu.SetShaderFloat("alpha_1", cls.pr_alpha_rendu)
        cls.rendu.SetShaderFloat("alpha_2", cls.pr_alpha_aura)
        cls.rendu.SetShaderFloat("contraste", cls.pr_Contraste)
        cls.rendu.SetShaderFloat("seuil", cls.pr_Seuil_contraste)
        cls.rendu.SetShaderFloat("H", cls.pr_Hue)
        cls.rendu.SetShaderFloat("S", cls.pr_Saturation)
        cls.rendu.SetShaderFloat("V", cls.pr_Value)
        cls.rendu.EnableBlending(True)
        cls.affiche_texture_rendu()

    #===============================
    #       Renvois des fbo:
    #===============================

    @classmethod
    def renvoie_fbo(cls,id):
        return cls.pr_fbos[id]
    @classmethod
    def renvoie_texture_rendu(cls,id):
        return cls.pr_textures[id]
    @classmethod
    def renvoie_texture_rendu_depth(cls,id):
        return cls.pr_textures_depth[id]

    #============================
    #   GAAAAAZ !
    #============================

    @classmethod
    def depart_demo(cls):
        cls.horloge = gs.Clock()