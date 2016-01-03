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
from math import pi, cos, sin, asin, sqrt
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
        render.text2d(50,yPos,comp.GetName(),16, c)
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
    cam=la_camera.camera
    render.text2d(xPos,yPos,"Caméra: "+la_camera.GetName(),16, c)
    render.text2d(xPos,yPos-2*e,"Zoom: "+str(round(cam.GetZoomFactor(),3)),16, c)
    render.text2d(xPos,yPos-3*e,"Fov: "+str(round(gs.ZoomFactorToFov(cam.GetZoomFactor())/pi*180,3)),16, c)
    render.text2d(xPos,yPos-4*e,"Z near: "+str(round(cam.GetZNear(),3)),16,c)
    render.text2d(xPos,yPos-5*e,"Z far: "+str(round(cam.GetZFar(),3)),16, c)
    affiche_matrice(la_camera.transform,xPos,yPos-6*e,c)


def affiche_donnees_lumiere(la_lumiere,xPos,c=gs.Color.White):
    yPos=850
    e=16
    l=la_lumiere.light
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

    affiche_matrice(la_lumiere.transform,xPos,yPos-10*e,c  )

def affiche_donnees_object(lobject,xPos,c=gs.Color.White):
    yPos=850
    e=16
    obj=lobject.object
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

    affiche_matrice(lobject.transform,xPos,yPos-(n+6)*e,c  )

def affiche_donnees_noeud(noeud,c=gs.Color.Yellow):
    xPos=1200
    yPos=850
    e=16

    if not noeud.light==None:
        affiche_donnees_lumiere(noeud,xPos,c)
    elif not noeud.camera==None:
        affiche_donnees_camera(noeud,xPos,c)
    elif not noeud.object==None:
        affiche_donnees_object(noeud,xPos,c)
    else:
        render.text2d(xPos,yPos,"Noeud: "+noeud.GetName(),16, c)
        affiche_matrice(noeud.transform,xPos,yPos-2*e,c)

def maj_zoom(la_camera):
    zoom=la_camera.camera.GetZoomFactor()
    pas_zoom=0.1
    if input.key_down(gs.InputDevice.KeyAdd):
        zoom+=pas_zoom
    elif  input.key_down(gs.InputDevice.KeySub):
        zoom-=pas_zoom
        if zoom<1.:
            zoom=1.
    la_camera.camera.SetZoomFactor(zoom)

def edit_noeud(le_noeud):
    maj_orientation(le_noeud)
    maj_position(le_noeud)
    if not le_noeud.light==None:
        edit_lumiere(le_noeud)

def edit_lumiere(le_noeud):
    sr=le_noeud.light.GetShadowRange()
    sb=le_noeud.light.GetShadowBias()
    #sd=le_noeud.light.GetShadowDistribution()
    di=le_noeud.light.GetDiffuseIntensity()
    lr=le_noeud.light.GetRange()
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

    le_noeud.light.SetShadowBias(sb)
    le_noeud.light.SetShadowRange(sr)
    #le_noeud.light.SetShadowDistribution(sd)
    le_noeud.light.SetDiffuseIntensity(di)
    le_noeud.light.SetRange(lr)

def maj_orientation(le_noeud):
    mat=le_noeud.transform
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
    le_noeud.transform.SetRotation(orientation)

def maj_position(le_noeud):
    mat=le_noeud.transform
    pas_dep=1/180*pi
    position=mat.GetPosition()

    """
    for key in range(0, gs.InputDevice.KeyLast):
        if input.key_press(key):
            print("Keyboard key pressed: %d" % key)
    """
    # Switch contrôle Danel / élément scène:
    if Demo.clavier.WasPressed(gs.InputDevice.KeyF1):
        Demo.drapeau_camera_controle_utilisateur=not Demo.drapeau_camera_controle_utilisateur

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
        le_noeud.transform.SetPosition(position)


def giration_lumiere(la_lumiere):
    orientation=la_lumiere.transform.GetRotation()
    orientation.y+=5/180.*pi
    la_lumiere.transform.SetRotation(orientation)


def affiche_donnees_environnement(ze_environnement,xPos,yPos,c=gs.Color.White):
    e=16
    bgc=ze_environnement.GetBackgroundColor()
    render.text2d(xPos,yPos,"Environnement: "+ze_environnement.GetName(),16, c)
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
