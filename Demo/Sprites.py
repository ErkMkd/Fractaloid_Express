# -*-coding:Utf-8 -*

"""

    Fractaloid Express - Mankind - 2016

    Gestion des sprites animés - Classes de base.

"""

import gs
from Demo.Demo import Demo as Demo
from utils.MathsSupp import MathsSupp as MathsSupp
from math import pi

#-----------------------------------------------------------------------------------
# Position / échelle / rotation des sprites
#-----------------------------------------------------------------------------------
class SpriteTransform:
    def __init__(self,x=0,y=0,z=0,ex=1,ey=1,r=0,t=0,l=0,axe_x=gs.Vector3.Right,axe_y=gs.Vector3.Up):
        self.x,self.y,self.z=x,y,z
        self.ex,self.ey=ex,ey
        self.r,self.t,self.l=r,t,l
        self.axe_x=axe_x #Le plan de projection du sprite
        self.axe_y=axe_y
        self.axe_z=axe_x.Cross(self.axe_y)  #Juste comme info, après il est calculé au fil des rotations.
        self.distance_camera=0  #Pour le tri des sprites
        self.drapeau_gauche=False
        self.rotation=gs.Matrix3()
        self.determine_RTL(r,t,l)

    def affiche(self):
        raise NotImplementedError

    def affiche_geometrie(self):
        raise NotImplementedError

    def determine_position(self,x,y,z):
        self.x,self.y,self.z=x,y,z

    def determine_RTL(self,r,t,l):
        self.r,self.t,self.l = r,t,l
        self.rotation=gs.Matrix3().FromEuler(t,l,r)
        self.axe_x=self.rotation.GetX()
        self.axe_y=self.rotation.GetY()
        self.axe_z=self.rotation.GetZ()



#-----------------------------------------------------------------------------------
# Calculs avec les sprites:
#-----------------------------------------------------------------------------------

class SpriteMaths:
    @classmethod
    def calcul_point_plan_projection(cls,cx,cy,cz,spx,spy,axe_x,axe_y):
        """
        Projette un point du plan du sprite dans l'espace
        :param cx: position spatiale de l'origine du plan du sprite
        :param cy:
        :param cz:
        :param spx: Position dans le plan du sprite
        :param spy:
        :param axe_x: Plan du sprite
        :param axe_y:
        :return: gs.Vector3 - la position du point dans l'espace
        """
        projX=gs.Vector3(spx*axe_x.x,spx*axe_x.y,spx*axe_x.z)
        projY=gs.Vector3(spy*axe_y.x,spy*axe_y.y,spy*axe_y.z)
        point=gs.Vector3(projX+projY)+gs.Vector3(cx,cy,cz)
        return point



#-----------------------------------------------------------------------------------
# Gestion des bitmaps
#-----------------------------------------------------------------------------------

class SpriteFrame:

    #Le point de collision de base, le barycentre:
    PC_BARYCENTRE=0

    def __init__(self,p_nomFichier="",cx=0,cy=0,px=0,py=0):
        self.nomFichier=p_nomFichier
        self.texture=None
        self.largeur,self.hauteur=0,0
        if p_nomFichier!="":
            self.texture=Aquagena.rendu.LoadTexture(self.nomFichier)
            self.largeur=float(self.texture.GetWidth())
            self.hauteur=float(self.texture.GetHeight())
        self.cx,self.cy=cx,cy
        self.dx,self.dy=px,py

        self.core_geometrie=None
        self.core_material=None
        self.geometrie=None #L'objet RenderGeometry - Appeler la fonction genere_geometrie(), une fois toutes les inits terminées pour créer cet objet.
        self.materiau=None


    #--------- Affichage:

    def affiche(self,x,y,z,ex,ey,axe_x,axe_y,teinte):

        cx=self.cx*ex
        cy=self.cy*ey
        xs=self.largeur*ex
        ys=self.hauteur*ey

        p1=SpriteMaths.calcul_point_plan_projection(x,y,z,-cx,-cy,axe_x,axe_y)
        p2=SpriteMaths.calcul_point_plan_projection(x,y,z,-cx,ys-cy,axe_x,axe_y)
        p3=SpriteMaths.calcul_point_plan_projection(x,y,z,xs-cx,ys-cy,axe_x,axe_y)
        p4=SpriteMaths.calcul_point_plan_projection(x,y,z,xs-cx,-cy,axe_x,axe_y)

        Aquagena.rendu2d.Quad(p1.x,p1.y,p1.z, \
                              p2.x,p2.y,p2.z, \
                              p3.x,p3.y,p3.z, \
                              p4.x,p4.y,p4.z, \
                              0,0, 1,1,self.texture,teinte,teinte,teinte,teinte)


    def affiche_inverse_X(self,x,y,z,ex,ey,axe_x,axe_y,teinte):
        cx=(self.largeur-self.cx)*ex
        cy=self.cy*ey
        xs=self.largeur*ex
        ys=self.hauteur*ey

        p1=SpriteMaths.calcul_point_plan_projection(x,y,z,-cx,-cy,axe_x,axe_y)
        p2=SpriteMaths.calcul_point_plan_projection(x,y,z,-cx,ys-cy,axe_x,axe_y)
        p3=SpriteMaths.calcul_point_plan_projection(x,y,z,xs-cx,ys-cy,axe_x,axe_y)
        p4=SpriteMaths.calcul_point_plan_projection(x,y,z,xs-cx,-cy,axe_x,axe_y)

        """
        Aquagena.rendu2d.Quad(self.xPos-cx,self.yPos-cy,z, \
                              self.xPos-cx,self.yPos+ys-cy,z, \
                              self.xPos+xs-cx,self.yPos+ys-cy,z, \
                              self.xPos+xs-cx,self.yPos-cy,z, \
                              1,0, 0,1,self.frames[indice].texture,teinte,teinte,teinte,teinte)
        """
        Aquagena.rendu2d.Quad(p1.x,p1.y,p1.z, \
                              p2.x,p2.y,p2.z, \
                              p3.x,p3.y,p3.z, \
                              p4.x,p4.y,p4.z, \
                              1,0, 0,1,self.texture,teinte,teinte,teinte,teinte)


    # Pour plus tard, si nécessaire, calculer la largeur de l'ombre en fonction de la rotation du billboard.
    def affiche_ombre_sol(self,x,z,ex,y_sol=0.,largeur_ombre=1.,alpha=1.):
        c=gs.Color.White
        c.a=alpha
        debord=1.5
        xs=self.largeur*ex*debord/2
        Aquagena.rendu2d.Quad(x-xs,y_sol,z-largeur_ombre/2, \
                              x-xs,y_sol,z+largeur_ombre/2, \
                              x+xs,y_sol,z+largeur_ombre/2, \
                              x+xs,y_sol,z-largeur_ombre/2, \
                              0,0, 1,1,Aquagena.texture_ombre_sol,c,c,c,c)

    def affiche_ombre_sol_inverse_X(self,x,z,ex,y_sol=0.,largeur_ombre=1.,alpha=1.):
        c=gs.Color.White
        c.a=alpha
        debord=1.5
        xs=self.largeur*ex*debord/2
        Aquagena.rendu2d.Quad(x-xs,y_sol,z-largeur_ombre/2, \
                              x-xs,y_sol,z+largeur_ombre/2, \
                              x+xs,y_sol,z+largeur_ombre/2, \
                              x+xs,y_sol,z-largeur_ombre/2, \
                              0,0, 1,1,Aquagena.texture_ombre_sol,c,c,c,c)

    #--------- Crée l'objet RenderGeometry qui va servir à afficher le sprite.

    def genere_geometrie(self):
        print ("Création géométrie: "+self.nomFichier)
        #---- Géométrie:

        self.core_geometrie=gs.CoreGeometry()
        self.core_geometrie.SetName(self.nomFichier)
        self.core_geometrie.AllocateVertex(4)
        self.core_geometrie.AllocateVertexNormal(4)
        self.core_geometrie.AllocatePolygon(1)

        self.core_geometrie.AllocateMaterialTable(1)
        self.core_geometrie.AllocateUVChannel(1,4)

        self.core_geometrie.SetVertex(0,-self.cx,-self.cy,0)
        self.core_geometrie.SetVertex(1,-self.cx,self.hauteur-self.cy,0)
        self.core_geometrie.SetVertex(2,self.largeur-self.cx,self.hauteur-self.cy,0)
        self.core_geometrie.SetVertex(3,self.largeur-self.cx,-self.cy,0)

        self.core_geometrie.SetVertexNormal(0,0,0,1)
        self.core_geometrie.SetVertexNormal(1,0,0,1)
        self.core_geometrie.SetVertexNormal(2,0,0,1)
        self.core_geometrie.SetVertexNormal(3,0,0,1)

        self.core_geometrie.SetUV(0,0,[gs.Vector2(0,1) , gs.Vector2(0,0) , gs.Vector2(1,0) , gs.Vector2(1,1)])
        #self.core_geometrie.SetUV(0,0,[gs.Vector2(0,1)])
        #self.core_geometrie.SetUV(0,1,[gs.Vector2(0,0)])
        #self.core_geometrie.SetUV(0,2,[gs.Vector2(1,0)])
        #self.core_geometrie.SetUV(0,3,[gs.Vector2(1,1)])

        self.core_geometrie.SetPolygon(0,4,0)
        self.core_geometrie.AllocatePolygonBinding()
        self.core_geometrie.SetPolygonBinding(0,[0,1,2,3])

        print (str(self.core_geometrie.Validate()))

        #---- Matériau:

        self.texture=Aquagena.rendu.LoadTexture(self.nomFichier)
        self.core_material=gs.CoreMaterial()
        self.core_material.SetShader("shaders/sprite_alpha.isl")
        self.core_material.AddValue("diffuse_map",gs.ShaderTexture2D)
        self.materiau=Aquagena.systeme.CreateMaterial(self.core_material,False)
        self.materiau.SetTexture("diffuse_map",self.texture)
        self.geometrie=Aquagena.systeme.CreateGeometry(self.core_geometrie,False)
        self.geometrie.SetMaterial(0,self.materiau)

        print ("...OK")

        #------ Affiche via la géométrie (au sein d'une scène 3d):

    def affiche_geometrie(self,x,y,z,ex,ey,axe_x,axe_y,axe_z,teinte):
        pos=gs.Vector3(x,y,z)
        rot=gs.Matrix3(axe_x,axe_y,axe_z)
        mat=gs.Matrix4.TransformationMatrix(pos,rot)
        mat.SetScale(gs.Vector3(ex,ey,1))
        materiau=self.geometrie.GetMaterial(0)
        materiau.SetFloat4("teinte",teinte.r,teinte.g,teinte.b,teinte.a)
        Aquagena.rendu_scene.DrawGeometry(self.geometrie,mat)


    def affiche_geometrie_inverse_X(self,x,y,z,ex,ey,axe_x,axe_y,axe_z,teinte):
        pos=gs.Vector3(x,y,z)
        #axe_x_inverse=MathsSupp.rotation_vecteur(axe_x,axe_y,pi*2)
        rot=gs.Matrix3(gs.Vector3(-axe_x.x,-axe_x.y,-axe_x.z),axe_y,gs.Vector3(-axe_z.x,-axe_z.y,-axe_z.z))
        mat=gs.Matrix4.TransformationMatrix(pos,rot)
        mat.SetScale(gs.Vector3(ex,ey,1))
        materiau=self.geometrie.GetMaterial(0)
        materiau.SetFloat4("teinte",teinte.r,teinte.g,teinte.b,teinte.a)
        Aquagena.rendu_scene.DrawGeometry(self.geometrie,mat)

    def affiche_geometrie_ombre_sol(self,x,z,ex,y_sol=0.,largeur_ombre=1.,alpha=1.):
        pass

    def affiche_geometrie_ombre_sol_inverse_X(self,x,z,ex,y_sol=0.,largeur_ombre=1.,alpha=1.):
        pass

#-----------------------------------------------------------------------------------
# Simple sprite sans animation, qui sert au décors:
#-----------------------------------------------------------------------------------

class BillBoard(SpriteTransform,SpriteFrame):
    def __init__(self,nom=""):
        SpriteTransform.__init__(self)
        SpriteFrame.__init__(self)
        self.teinte=gs.Color.White
        self.nom=nom

    #----- Crée un billboard à partir d'une texture, et génère sa géométrie.
    def creation(self,p_nomFichier,cx=0,cy=0,x=0,y=0,z=0,ex=1,ey=1,r=0,t=0,l=0):
        SpriteTransform.__init__(self,x,y,z,ex,ey,r,t,l)
        SpriteFrame.__init__(self,p_nomFichier,cx,cy,0,0)
        self.teinte=gs.Color.White
        self.genere_geometrie()

    #------- Instance d'un billboard déjà créé. Ca évite de recharger la texture et de recréer la géométrie.
    def instance(self,original,x=0,y=0,z=0,ex=1,ey=1,r=0,t=0,l=0):
        SpriteTransform.__init__(self,x,y,z,ex,ey,r,t,l)
        self.texture=original.texture
        self.largeur=original.largeur
        self.hauteur=original.hauteur
        self.geometrie=original.geometrie
        self.materiau=original.materiau
        self.teinte=gs.Color.White

    #------- Convertion d'un noeud de scène en Billboard:
    def convertion_node(self,noeud):
        mat=noeud.GetTransform().GetWorld()
        position,echelle,rotation=mat.Decompose(gs.RotationOrder_Default)
        SpriteTransform.__init__(self,position.x,position.y,position.z,echelle.x,echelle.y,rotation.z,rotation.x,rotation.y)

        self.geometrie=noeud.GetObject().GetGeometry()
        self.materiau=self.geometrie.GetMaterial(0)
        self.texture=self.materiau.GetTexture("diffuse_map")
        self.largeur=self.texture.GetWidth()
        self.hauteur=self.texture.GetHeight()
        self.nom=noeud.GetName()
        self.teinte=gs.Color.White

#------ Affiche via la géométrie:

    def affiche_geometrie(self):
        #SpriteFrame.affiche_geometrie(self,self.x,self.y,self.z,self.ex,self.ey,self.axe_x,self.axe_y,self.axe_z,self.teinte)
        #Version optimisée:
        pos=gs.Vector3(self.x,self.y,self.z)
        mat=gs.Matrix4.TransformationMatrix(pos,self.rotation)
        mat.SetScale(gs.Vector3(self.ex,self.ey,1))
        materiau=self.geometrie.GetMaterial(0)
        materiau.SetFloat4("teinte",self.teinte.r,self.teinte.g,self.teinte.b,self.teinte.a)
        Aquagena.rendu_scene.DrawGeometry(self.geometrie,mat)

#-----------------------------------------------------------------------------------
# Séquence d'animation:
#-----------------------------------------------------------------------------------

class SpriteSeq:

    def __init__(self,nFrames,premiereFrame,nomSequence,nomFichier,centresTab=[],pasTab=[]):
        """
        Charge une séquence de sprites
        :param nFrames:
        :param premiereFrame:
        :param nomSequence:
        :param nomFichier:
        :param centresTab:
        :param pasTab:
        :return:
        """
        """
        :param nFrames:
        :param premiereFrame: le numero du premier fichier de la série
        :param nomSequence:
        :param nomFichier:
        :param centresTab:
        :param pasTab:
        :return:
        """
        self.xPos,self.yPos=400.,300.
        self.numFrames=nFrames
        self.frame_actuelle=0
        self.frames=[]
        self.nom=nomSequence
        self.couleur=gs.Color(1.,1.,1.,1.)
        self.c3,self.c2,self.c1,self.c0=0,0,0,0

        i=0
        while i<premiereFrame:
            self.incCompteur()
            i+=1
        i=0

        if len(centresTab)>0 and len(pasTab)>0:
            while i<nFrames:
                self.frames.append(SpriteFrame(nomFichier+str(self.c3)+str(self.c2)+str(self.c1)+str(self.c0)+".png"),centresTab[i*2],centresTab[i*2+1],pasTab[i*2],pasTab[i*2+1])
                self.incCompteur()
                i+=1
        else:
            while i<nFrames:
                self.frames.append(SpriteFrame(nomFichier+str(self.c3)+str(self.c2)+str(self.c1)+str(self.c0)+".png"))
                self.incCompteur()
                i+=1

    def incCompteur(self):
        self.c0+=1
        if self.c0>9:
            self.c1+=1
            self.c0=0
            if self.c1>9:
                self.c2+=1
                self.c1=0
                if self.c2>9:
                    self.c3+=1
                    self.c2=0
                    if self.c3>9:
                        self.c3=0

    def affiche(self,ex=1.,ey=1.,z=0.,alpha=1.):
        self.couleur.a=alpha
        frame=self.frames[self.frame_actuelle]
        frame.affiche(self.xPos,self.yPos,z,ex,ey,gs.Vector3.Right,gs.Vector3.Up,self.couleur)

    def affiche_frame(self,indice,ex=1.,ey=1.,z=0.,teinte=gs.Color.White,axe_x=gs.Vector3.Right,axe_y=gs.Vector3.Up):
        frame=self.frames[indice]
        frame.affiche(self.xPos,self.yPos,z,ex,ey,axe_x,axe_y,teinte)

    def affiche_frame_inverse_X(self,indice,ex=1.,ey=1.,z=0.,teinte=gs.Color.White,axe_x=gs.Vector3.Right,axe_y=gs.Vector3.Up):
        frame=self.frames[indice]
        frame.affiche_inverse_X(self.xPos,self.yPos,z,ex,ey,axe_x,axe_y,teinte)


    def affiche_ombre_sol(self,indice,ex=1.,ey=1.,z=0.,y_sol=0.,largeur_ombre=1.,alpha=1.):
        frame=self.frames[indice]
        frame.affiche_ombre_sol(self.xPos,z,ex,y_sol,largeur_ombre,alpha)

    def affiche_ombre_sol_inverse_X(self,indice,ex=1.,ey=1.,z=0.,y_sol=0.,largeur_ombre=1.,alpha=1.):
        frame=self.frames[indice]
        frame.affiche_ombre_sol_inverse_X(self.xPos,z,ex,y_sol,largeur_ombre,alpha)

    def incFrame(self):
        self.frame_actuelle+=1
        if self.frame_actuelle>=self.numFrames:
            self.frame_actuelle=0

    def decFrame(self):
        self.frame_actuelle-=1
        if self.frame_actuelle<0:
            self.frame_actuelle=self.numFrames-1

    def renvoie_total_pas_actuel(self):
        px,py=0.,0.
        i=0
        while i<=self.frame_actuelle:
            frame=self.frames[i]
            px+=frame.dx
            py+=frame.dy
            i+=1
        return px,py

    def renvoie_total_pas_frame(self,indice):
        px,py=0.,0.
        i=0
        while i<=indice:
            frame=self.frames[i]
            px+=frame.dx
            py+=frame.dy
            i+=1
        return px,py


    def genere_geometrie(self):
        for frame in self.frames:
            frame.genere_geometrie()


