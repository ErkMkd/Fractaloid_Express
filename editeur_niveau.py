# -*-coding:Utf-8 -*

"""

    Fractaloid Express - Mankind - 2016

    Méthodes pour l'édition des scènes

"""
import gs
import gs.plus.render as render
import gs.plus.scene as scene
import gs.plus.input as input
import gs.plus.camera as camera
from math import pi, cos, sin, asin, sqrt,tan
from Demo.Demo import Demo as Demo


def affiche_vecteur(position,direction,c1=gs.Color.Yellow,c2=gs.Color.Red):
    position_b=position+direction
    Demo.rendu2d.Line(position.x,position.y,position.z, position_b.x,position_b.y,position_b.z, c1,c2)

def affiche_trajectoire(points,c=gs.Color.Yellow):
    if len(points)==0:
        return
    p0=points[0]
    for point in points:
        Demo.rendu2d.Line(p0.x,p0.y,p0.z, point.x,point.y,point.z, c,c)
        p0=point

def affiche_croix(x,y,z,e,c):
    r=10*e
    rCentre=3*e
    dwrt=Demo.rendu2d.GetDepthWrite()
    dtst=Demo.rendu2d.GetDepthTest()
    Demo.rendu2d.SetDepthWrite(False)
    Demo.rendu2d.SetDepthTest(False)
    Demo.rendu2d.Line(x,y-rCentre,z, x,y-r, z, c,c)
    Demo.rendu2d.Line(x+rCentre-e,y,z, x+r-e,y,z, c,c)
    Demo.rendu2d.Line(x,y+rCentre-e,z, x,y+r-e,z, c,c)
    Demo.rendu2d.Line(x-rCentre,y,z, x-r,y,z, c,c)
    Demo.rendu2d.Line(x,y,z, x+e,y, z, c,c)
    Demo.rendu2d.Line(x+e,y,z, x+e,y+e,z, c,c)
    Demo.rendu2d.Line(x+e,y+e,z, x,y+e,z, c,c)
    Demo.rendu2d.Line(x,y+e,z, x,y,z, c,c)
    Demo.rendu2d.SetDepthWrite(dwrt)
    Demo.rendu2d.SetDepthTest(dtst)

def affiche_cercle(x,y,z,r,c):
    dwrt=Demo.rendu2d.GetDepthWrite()
    dtst=Demo.rendu2d.GetDepthTest()
    numSegments=32
    pas=2*pi/numSegments
    x0=x+r
    y0=y
    i=1
    while i<=numSegments:
        x1=r*cos(i*pas)+x
        y1=r*sin(i*pas)+y
        Demo.rendu2d.Line(x0,y0,z, x1,y1, z, c,c)
        x0=x1
        y0=y1
        i+=1
    Demo.rendu2d.SetDepthWrite(dwrt)
    Demo.rendu2d.SetDepthTest(dtst)

def listing_noeuds(noeuds,noeud_actuel,c_inactive=gs.Color.White,c_active=gs.Color.Yellow):
    yStart=850
    yPos=yStart
    i=0
    render.text2d(25,yPos,"Noeuds:",18, gs.Color.Green)
    yPos-=20
    for noeud in noeuds:
        if i==noeud_actuel:
            c=c_active
        else:
            c=c_inactive
        render.text2d(50,yPos,noeud.GetName(),16, c)
        yPos-=16
        i+=1

def listing_components(components,component_actuel):
    yStart=450
    yPos=yStart
    i=0
    c=gs.Color.Grey
    for comp in components:
        if i==component_actuel:
            c=gs.Color.Yellow
        else:
            c=gs.Color.White
        render.text2d(50,yPos,comp.GetAspect(),16, c)
        yPos-=16
        i+=1

def listing_sprites(liste,sprite_actuel,c_inactive=gs.Color.White,c_active=gs.Color.Yellow):
    yStart=850
    yPos=yStart
    i=0
    render.text2d(25+300,yPos,"Sprites:",18, gs.Color.Green)
    yPos-=20
    for sprite in liste:
        if i==sprite_actuel:
            c=c_active
        else:
            c=c_inactive
        render.text2d(50+300,yPos,sprite.nom,16, c)
        yPos-=16
        i+=1

def affiche_matrice(mat,x,y,c=gs.Color.White):
    e=16
    position=mat.GetPosition()
    orientation=mat.GetRotation()

    render.text2d(x,y,"X: "+str(round(position.x,3)),16, c)
    render.text2d(x,y-e,"Y: "+str(round(position.y,3)),16, c)
    render.text2d(x,y-2*e,"Z: "+str(round(position.z,3)),16, c)
    render.text2d(x,y-4*e,"T: "+str(round(orientation.x/pi*180.,3))+"°    "+str(round(orientation.x,3))+" rad",16, c)
    render.text2d(x,y-5*e,"L: "+str(round(orientation.y/pi*180.,3))+"°    "+str(round(orientation.y,3))+" rad",16, c)
    render.text2d(x,y-6*e,"R: "+str(round(orientation.z/pi*180.,3))+"°    "+str(round(orientation.z,3))+" rad",16, c)

def affiche_donnees_camera(la_camera,xPos,c=gs.Color.White):
    yPos=850
    e=16
    cam=la_camera.GetCamera()
    render.text2d(xPos,yPos,"Caméra: "+la_camera.GetName(),16, c)
    render.text2d(xPos,yPos-2*e,"Zoom: "+str(round(cam.GetZoomFactor(),3)),16, c)
    Fov=gs.ZoomFactorToFov(cam.GetZoomFactor())
    render.text2d(xPos,yPos-3*e,"Fov: "+str(round(Fov/pi*180,3)),16, c)

    distanceFocale=Demo.calcul_distance_focale(la_camera)
    render.text2d(xPos,yPos-4*e,"Distance focale: "+str(round(distanceFocale,3)),16, c)
    render.text2d(xPos,yPos-5*e,"Z near: "+str(round(cam.GetZNear(),3)),16,c)
    render.text2d(xPos,yPos-6*e,"Z far: "+str(round(cam.GetZFar(),3)),16, c)
    affiche_matrice(la_camera.GetTransform(),xPos,yPos-8*e,c)


def affiche_donnees_lumiere(la_lumiere,xPos,c=gs.Color.White):
    yPos=850
    e=16
    l=la_lumiere.GetLight()
    modeles=['','','']
    modeles[gs.Light.Model_Point]="Point"
    modeles[gs.Light.Model_Linear]="Linear"
    modeles[gs.Light.Model_Spot]="Spot"

    shadows=['','','']
    shadows[gs.Light.Shadow_None]="None"
    shadows[gs.Light.Shadow_Map]="Map"
    shadows[gs.Light.Shadow_ProjectionMap]="ProjectionMap"

    render.text2d(xPos,yPos,"Lumière: "+la_lumiere.GetName(),16, c)
    render.text2d(xPos,yPos-e*2,"Model: "+modeles[l.GetModel()],16, c)
    #render.text2d(xPos,yPos-e*2,"Diff intensité: "+str(l.Get()],16, gs.Color.Yellow)

    render.text2d(xPos,yPos-e*3,"Shadow: "+shadows[l.GetShadow()],16, c)
    render.text2d(xPos,yPos-e*4,"Shadow range: "+str(l.GetShadowRange()),16, c)
    render.text2d(xPos,yPos-e*5,"Shadow bias: "+str(round(l.GetShadowBias(),6)),16,c)
    #render.text2d(xPos,yPos-e*6,"Shadow distribution: "+str(round(l.GetShadowDistribution(),6)),16, c)

    render.text2d(xPos,yPos-e*8,"Intensité Diff.: "+str(round(l.GetDiffuseIntensity(),3)),16, c)
    render.text2d(xPos,yPos-e*9,"Portée: "+str(round(l.GetRange(),3)),16, c)

    affiche_matrice(la_lumiere.GetTransform(),xPos,yPos-10*e,c  )

def affiche_donnees_object(lobject,xPos,c=gs.Color.White):
    yPos=850
    e=16
    obj=lobject.GetObject()
    render.text2d(xPos,yPos,"Objet: "+lobject.GetName(),16, c)

    geo=obj.GetGeometry()
    i=geo.GetMaterialCount()
    render.text2d(xPos,yPos-2*e,"Num matériaux: "+str(i),16, c)
    n=0
    while n<i:
        materiau=geo.GetMaterial(n)
        render.text2d(xPos,yPos-(n+4)*e,"Materiau "+str(n)+" : "+materiau.GetName(),16, c)
        #tex=materiau.GetTexture()
        #if is not None materiau.GetTexture()
        n+=1

    affiche_matrice(lobject.GetTransform(),xPos,yPos-(n+6)*e,c  )

def affiche_donnees_noeud(noeud,c=gs.Color.Yellow):
    xPos=1200
    yPos=850
    e=16

    if not noeud.GetLight()==None:
        affiche_donnees_lumiere(noeud,xPos,c)
    elif not noeud.GetCamera()==None:
        affiche_donnees_camera(noeud,xPos,c)
    elif not noeud.GetObject()==None:
        affiche_donnees_object(noeud,xPos,c)
    else:
        render.text2d(xPos,yPos,"Noeud: "+noeud.GetName(),16, c)
        affiche_matrice(noeud.GetTransform(),xPos,yPos-2*e,c)

def maj_zoom(la_camera):
    zoom=la_camera.GetCamera().GetZoomFactor()
    pas_zoom=0.1
    if input.key_down(gs.InputDevice.KeyAdd):
        zoom+=pas_zoom
    elif  input.key_down(gs.InputDevice.KeySub):
        zoom-=pas_zoom
        if zoom<1.:
            zoom=1.
    la_camera.GetCamera().SetZoomFactor(zoom)

def edit_noeud(le_noeud):
    maj_orientation(le_noeud)
    maj_position(le_noeud)
    if not le_noeud.GetLight()==None:
        edit_lumiere(le_noeud)

def edit_lumiere(le_noeud):
    sr=le_noeud.GetLight().GetShadowRange()
    sb=le_noeud.GetLight().GetShadowBias()
    #sd=le_noeud.GetLight().GetShadowDistribution()
    di=le_noeud.GetLight().GetDiffuseIntensity()
    lr=le_noeud.GetLight().GetRange()
    f=1
    if input.key_down(gs.InputDevice.KeyLShift):
        f=10

    if input.key_down(gs.InputDevice.KeyU):
       sr-=1*f
       if sr<1:
           sr=1
    elif  input.key_down(gs.InputDevice.KeyI):
        sr+=1*f

    if input.key_down(gs.InputDevice.KeyO):
       sb-=0.0001*f
       if sb<0.0001:
           sb=0.0001
    elif  input.key_down(gs.InputDevice.KeyP):
        sb+=0.0001*f

    """
    if input.key_down(gs.InputDevice.KeyK):
       sd-=0.001*f
       if sd<0.001:
           sd=0.001
    elif  input.key_down(gs.InputDevice.KeyL):
        sd+=0.001*f
    """
    if input.key_down(gs.InputDevice.KeyB):
       di-=0.01*f
       #if di<0:
       #    di=0
    elif  input.key_down(gs.InputDevice.KeyN):
        di+=0.01*f

    if input.key_down(gs.InputDevice.KeyH):
       lr-=0.01*f
       if lr<0.01:
           lr=0.01
    elif  input.key_down(gs.InputDevice.KeyJ):
        lr+=0.01*f

    le_noeud.GetLight().SetShadowBias(sb)
    le_noeud.GetLight().SetShadowRange(sr)
    #le_noeud.GetLight().SetShadowDistribution(sd)
    le_noeud.GetLight().SetDiffuseIntensity(di)
    le_noeud.GetLight().SetRange(lr)

def maj_orientation(le_noeud):
    mat=le_noeud.GetTransform()
    pas_rot=1/180*pi
    orientation=mat.GetRotation()
    if input.key_down(gs.InputDevice.KeyA):
        orientation.y-=pas_rot
    elif  input.key_down(gs.InputDevice.KeyZ):
        orientation.y+=pas_rot
    elif  input.key_down(gs.InputDevice.KeyE):
        orientation.x-=pas_rot
    elif  input.key_down(gs.InputDevice.KeyR):
        orientation.x+=pas_rot
    elif  input.key_down(gs.InputDevice.KeyT):
        orientation.z-=pas_rot
    elif  input.key_down(gs.InputDevice.KeyY):
        orientation.z+=pas_rot
    le_noeud.GetTransform().SetRotation(orientation)

def maj_position(le_noeud):
    mat=le_noeud.GetTransform()
    pas_dep=1/180*pi
    position=mat.GetPosition()

    """
    for key in range(0, gs.InputDevice.KeyLast):
        if input.key_press(key):
            print("Keyboard key pressed: %d" % key)
    """
    # Switch contrôle Danel / élément scène:

    if not Demo.drapeau_camera_controle_utilisateur:
        if input.key_down(gs.InputDevice.KeyLeft):
            position.x-=pas_dep
        elif  input.key_down(gs.InputDevice.KeyRight):
            position.x+=pas_dep
        elif  input.key_down(gs.InputDevice.KeyPageDown):
            position.y-=pas_dep
        elif  input.key_down(gs.InputDevice.KeyPageUp):
            position.y+=pas_dep
        elif  input.key_down(gs.InputDevice.KeyDown):
            position.z-=pas_dep
        elif  input.key_down(gs.InputDevice.KeyUp):
            position.z+=pas_dep
        le_noeud.GetTransform().SetPosition(position)


def giration_lumiere(la_lumiere):
    orientation=la_lumiere.GetTransform().GetRotation()
    orientation.y+=5/180.*pi
    la_lumiere.GetTransform().SetRotation(orientation)


def affiche_donnees_environnement(ze_environnement,xPos,yPos,c=gs.Color.White):
    e=16
    bgc=ze_environnement.GetBackgroundColor()
    render.text2d(xPos,yPos,"Environnement: "+ze_environnement.GetAspect(),16, c)
    render.text2d(xPos,yPos-2*e,"Couleur fond: R="+str(round(bgc.r,3))+" V="+str(round(bgc.g,3))+" B="+str(round(bgc.b,3)),16, c)



#---------Renvoie un RenderMaterial d'après son nom:

def renvoie_materiau_nom(objet,nom):
    geo=objet.GetGeometry()
    i=geo.GetMaterialCount()
    n=0
    while n<i:
        materiau=geo.GetMaterial(n)
        if materiau.GetName()==nom:
            return materiau
        n+=1
    return None

#---------- Paramétrage des filtres:

def affiche_parametres_filtres():
    window_size = Demo.rendu.GetDefaultOutputWindow().GetSize()
    xPos=10
    yPos=window_size.y-30

    c=gs.Color.White
    render.text2d(xPos,yPos,"A/Q pr_taille_aura: "+str(Demo.pr_taille_aura),16, c)
    render.text2d(xPos,yPos-15,"Z/S pr_intensite_aura: "+str(Demo.pr_intensite_aura),16, c)
    render.text2d(xPos,yPos-15*2,"E/D pr_aura_contraste: "+str(Demo.pr_aura_contraste),16, c)
    render.text2d(xPos,yPos-15*3,"R/F pr_aura_seuil_contraste: "+str(Demo.pr_aura_seuil_contraste),16, c)
    render.text2d(xPos,yPos-15*4,"T/G pr_aura_hue: "+str(Demo.pr_aura_hue),16, c)
    render.text2d(xPos,yPos-15*5,"Y/H pr_aura_saturation: "+str(Demo.pr_aura_saturation),16, c)
    render.text2d(xPos,yPos-15*6,"U/J pr_aura_value: "+str(Demo.pr_aura_value),16, c)
    render.text2d(xPos,yPos-15*7,"I/K pr_alpha_aura: "+str(Demo.pr_alpha_aura),16, c)
    render.text2d(xPos,yPos-15*8,"O/L pr_alpha_rendu: "+str(Demo.pr_alpha_rendu),16, c)
    render.text2d(xPos,yPos-15*9,"1/2 pr_Contraste: "+str(Demo.pr_Contraste),16, c)
    render.text2d(xPos,yPos-15*10,"3/4 pr_Seuil_contraste: "+str(Demo.pr_Seuil_contraste),16, c)
    render.text2d(xPos,yPos-15*11,"5/6 pr_Hue: "+str(Demo.pr_Hue),16, c)
    render.text2d(xPos,yPos-15*12,"7/8 pr_Saturation: "+str(Demo.pr_Saturation),16, c)
    render.text2d(xPos,yPos-15*13,"9/0 pr_Value: "+str(Demo.pr_Value),16, c)

def maj_filtres():

    if not Demo.drapeau_camera_controle_utilisateur:

        if input.key_down(gs.InputDevice.KeyA):
            Demo.pr_taille_aura+=1
        elif input.key_down(gs.InputDevice.KeyQ):
            Demo.pr_taille_aura-=1
            if Demo.pr_taille_aura<1:
                Demo.pr_taille_aura=1

        elif input.key_down(gs.InputDevice.KeyZ):
            Demo.pr_intensite_aura+=0.1
        elif input.key_down(gs.InputDevice.KeyS):
            Demo.pr_intensite_aura-=0.1
            if Demo.pr_intensite_aura<0.1:
                Demo.pr_intensite_aura=0.1

        elif input.key_down(gs.InputDevice.KeyE):
            Demo.pr_aura_contraste+=0.1
        elif input.key_down(gs.InputDevice.KeyD):
            Demo.pr_aura_contraste-=0.1
            if Demo.pr_aura_contraste<0.1:
                Demo.pr_aura_contraste=0.1

        elif input.key_down(gs.InputDevice.KeyR):
                Demo.pr_aura_seuil_contraste+=0.01
        elif input.key_down(gs.InputDevice.KeyF):
            Demo.pr_aura_seuil_contraste-=0.01
            if Demo.pr_aura_seuil_contraste<0.01:
                Demo.pr_aura_seuil_contraste=0.01

        elif input.key_down(gs.InputDevice.KeyT):
            Demo.pr_aura_hue+=1
        elif input.key_down(gs.InputDevice.KeyG):
            Demo.pr_aura_hue-=1

        elif input.key_down(gs.InputDevice.KeyY):
                Demo.pr_aura_saturation+=0.1
        elif input.key_down(gs.InputDevice.KeyH):
            Demo.pr_aura_saturation-=0.1
            if Demo.pr_aura_saturation<0:
                Demo.pr_aura_saturation=0

        elif input.key_down(gs.InputDevice.KeyU):
                Demo.pr_aura_value+=0.1
        elif input.key_down(gs.InputDevice.KeyJ):
            Demo.pr_aura_value-=0.1
            if Demo.pr_aura_value<0:
                Demo.pr_aura_value=0

        elif input.key_down(gs.InputDevice.KeyI):
                Demo.pr_alpha_aura+=0.1
        elif input.key_down(gs.InputDevice.KeyK):
            Demo.pr_alpha_aura-=0.1
            if Demo.pr_alpha_aura<0:
                Demo.pr_alpha_aura=0

        elif input.key_down(gs.InputDevice.KeyO):
                Demo.pr_alpha_rendu+=0.1
        elif input.key_down(gs.InputDevice.KeyL):
            Demo.pr_alpha_rendu-=0.1
            if Demo.pr_alpha_rendu<0:
                Demo.pr_alpha_rendu=0

        elif input.key_down(gs.InputDevice.KeyNumpad2):
                Demo.pr_Contraste+=0.1
        elif input.key_down(gs.InputDevice.KeyNumpad1):
            Demo.pr_Contraste-=0.1
            if Demo.pr_Contraste<0:
                Demo.pr_Contraste=0

        elif input.key_down(gs.InputDevice.KeyNumpad4):
                Demo.pr_Seuil_contraste+=0.01
        elif input.key_down(gs.InputDevice.KeyNumpad3):
            Demo.pr_Seuil_contraste-=0.01
            if Demo.pr_Seuil_contraste<0.01:
                Demo.pr_Seuil_contraste=0.01

        elif input.key_down(gs.InputDevice.KeyNumpad6):
                Demo.pr_Hue+=1
        elif input.key_down(gs.InputDevice.KeyNumpad5):
            Demo.pr_Hue-=1

        elif input.key_down(gs.InputDevice.KeyNumpad8):
                Demo.pr_Saturation+=0.1
        elif input.key_down(gs.InputDevice.KeyNumpad7):
            Demo.pr_Saturation-=0.1
            if Demo.pr_Saturation<0:
                Demo.pr_Saturation=0

        elif input.key_down(gs.InputDevice.KeyNumpad0):
                Demo.pr_Value+=0.1
        elif input.key_down(gs.InputDevice.KeyNumpad9):
            Demo.pr_Value-=0.1
            if Demo.pr_Value<0:
                Demo.pr_Value=0
