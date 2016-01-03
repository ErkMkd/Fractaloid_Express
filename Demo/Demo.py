# -*-coding:Utf-8 -*

"""
    Fractaloid Express - Mankind - 2016

    Données globales et template de la classe principale

"""

import gs
import gs.plus.render as render
import gs.plus.input as input

#======================================================================
#          The Classe principale, qui regroupe les variables globales
#       Les scènes sont des classes statiques.
#======================================================================

class Demo:
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
    pr_shader=None #Le shader de traitement post-rendu
    pr_indices=None
    pr_vertex_layout=None
    pr_vertex=None
    pr_texture_rendu=None
    pr_texture_rendu_depth=None
    pr_fbo_rendu=None

    pr_contraste=0.
    pr_seuil_contraste=0.5
    pr_Hue=1.9
    pr_Saturation=1.
    pr_Value=1.

    #------------ Affiche un message d'erreur à l'écran:
    @classmethod
    def affiche_message_erreur(cls):
        y=450
        for message in cls.message_erreur:
            render.text2d(400,y,message,16, gs.Color.Red)
            y-=20

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
        #Init les shaders:
        cls.pr_shader = cls.rendu.LoadShader("shaders/shader_2d_single_texture.isl")

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

        # create the texture we will render to
        window_size = cls.rendu.GetDefaultOutputWindow().GetSize()
        cls.pr_texture_rendu = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu, window_size.x, window_size.y,gs.GpuTexture.RGBA8,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)
        cls.pr_texture_rendu_depth = cls.rendu.NewTexture()
        cls.rendu.CreateTexture(cls.pr_texture_rendu_depth, window_size.x, window_size.y,gs.GpuTexture.Depth,gs.GpuTexture.NoAA,gs.GpuTexture.UsageDefault,False)

        # create and configure the frame buffer object to render to the texture
        cls.pr_fbo_rendu = cls.rendu.NewRenderTarget()
        cls.rendu.CreateRenderTarget(cls.pr_fbo_rendu)
        cls.rendu.SetRenderTargetColorTexture(cls.pr_fbo_rendu, cls.pr_texture_rendu)
        cls.rendu.SetRenderTargetDepthTexture(cls.pr_fbo_rendu, cls.pr_texture_rendu_depth)


    @classmethod
    def affiche_texture_rendu(cls):
        window_size = cls.rendu.GetDefaultOutputWindow().GetSize()
        cls.rendu.SetViewport(gs.fRect(0, 0, window_size.x, window_size.y))  # fit viewport to window dimensions
        cls.rendu.Clear(gs.Color.Black)  # red

        cls.rendu.SetShader(Demo.pr_shader)
        cls.rendu.SetShaderTexture("u_tex", Demo.pr_texture_rendu)
        #cls.rendu.SetShaderFloat("saturation", cls.pr_saturation_avec_seuil)
        cls.rendu.SetShaderFloat("contraste", cls.pr_contraste)
        cls.rendu.SetShaderFloat("seuil", cls.pr_seuil_contraste)
        cls.rendu.SetShaderFloat("H", cls.pr_Hue)
        cls.rendu.SetShaderFloat("S", cls.pr_Saturation)
        cls.rendu.SetShaderFloat("V", cls.pr_Value)
        gs.DrawBuffers(cls.rendu, 6, cls.pr_indices, cls.pr_vertex, cls.pr_vertex_layout)

    @classmethod
    def depart_demo(cls):
        cls.horloge = gs.Clock()