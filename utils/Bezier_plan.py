# -*-coding:Utf-8 -*

"""

    Courbe de Bezier 2d - Eric Kernin - 2015

   Sert surtout pour les variations de paramètres d'interpolations.

"""

from math import sqrt

class Courbe_Bezier_Plan:

    def __init__( self, P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y, fact=1):
        self.precision=1e-6
        self.facteur = fact
        self.P0_x = P0x
        self.P0_y = P0y
        self.P1_x = P1x
        self.P1_y = P1y
        self.P2_x = P2x
        self.P2_y = P2y
        self.P3_x = P3x
        self.P3_y = P3y
        
        self.alpha=0
        self.beta=0
        self.gamma=0
        self.delta=0
        
        self.tangenteA_x = (self.P1_x - self.P0_x) * self.facteur + self.P0_x
        self.tangenteA_y = (self.P1_y - self.P0_y) * self.facteur + self.P0_y
        self.tangenteB_x = (self.P2_x - self.P3_x) * self.facteur + self.P3_x
        self.tangenteB_y = (self.P2_y - self.P3_y) * self.facteur + self.P3_y
        self.resolution()
		

    def determine_P0(self,px, py):

        self.P0_x = px
        self.P0_y = py
        self.tangenteA_x = (self.P1_x - self.P0_x) * self.facteur + self.P0_x
        self.tangenteA_y = (self.P1_y - self.P0_y) * self.facteur + self.P0_y
        self.resolution()



    def determine_P1(self, px, py):

        self.P1_x = px
        self.P1_y = py
        self.tangenteA_x = (self.P1_x - self.P0_x) * self.facteur + self.P0_x
        self.tangenteA_y = (self.P1_y - self.P0_y) * self.facteur + self.P0_y
        self.resolution()



    def determine_P2(self, px, py):

        self.P2_x = px
        self.P2_y = py
        self.tangenteB_x = (self.P2_x - self.P3_x) * self.facteur + self.P3_x
        self.tangenteB_y = (self.P2_y - self.P3_y) * self.facteur + self.P3_y
        self.resolution()



    def determine_P3(self, px,  py):

        self.P3_x = px
        self.P3_y = py
        self.tangenteB_x = (self.P2_x - self.P3_x) * self.facteur + self.P3_x
        self.tangenteB_y = (self.P2_y - self.P3_y) * self.facteur + self.P3_y
        self.resolution()


    def determine_facteur(self, f):

        self.facteur = f
        self.tangenteA_x = (self.P1_x - self.P0_x) * self.facteur + self.P0_x
        self.tangenteA_y = (self.P1_y - self.P0_y) * self.facteur + self.P0_y
        self.tangenteB_x = (self.P2_x - self.P3_x) * self.facteur + self.P3_x
        self.tangenteB_y = (self.P2_y - self.P3_y) * self.facteur + self.P3_y
        self.resolution()


    def renvoie_P0(self):

        return self.P0_x,self.P0_y


    def renvoie_P1(self):

        return self.P1_x,self.P1_y


    def renvoie_P2(self):

        return self.P2_x,self.P2_y


    def renvoie_P3(self):

        return self.P3_x,self.P3_y


    def renvoie_facteur(self):
    
        return self.facteur
    

    #Renvoie la postion d'un point de la courbe pour une valeur de t comprise entre 0 (point A) et 1 (point B)
    def renvoie_position(self,t):
    
        if t > 1: t = 1
        elif t < 0: t = 0


        t1 = 1 - t
        t12  = t1 * t1
        t13  = t12 * t1

        t2 = t * t
        t3 = t2 * t

        x = self.P0_x * t13 + 3 * self.tangenteA_x * t * t12 + 3 * self.tangenteB_x * t2 * t1 + self.P3_x * t3
        y = self.P0_y * t13 + 3 * self.tangenteA_y * t * t12 + 3 * self.tangenteB_y * t2 * t1 + self.P3_y * t3
        
        return x,y

    

    #Renvoie la coordonnée en y d'un point de la courbe pour une valeur de t comprise entre 0 (point A) et 1 (point B)
    def renvoie_ordonnee(self,t):
    
        #if (t > 1) { t = 1 }
        #else if (t < 0) { t = 0 }

        t1 = 1 - t
        t12  = t1 * t1
        t13  = t12 * t1

        t2 = t * t
        t3 = t2 * t

        return self.P0_y * t13 + 3 * self.tangenteA_y * t * t12 + 3 * self.tangenteB_y * t2 * t1 + self.P3_y * t3
    

    #Renvoie la coordonnée en x d'un point de la courbe pour une valeur de t comprise entre 0 (point A) et 1 (point B)
    def renvoie_abscisse(self, t):
    
        #if (t > 1) { t = 1 }
        #else if (t < 0) { t = 0 }

        t1 = 1 - t
        t12  = t1 * t1
        t13  = t12 * t1

        t2 = t * t
        t3 = t2 * t

        return self.P0_x * t13 + 3 * self.tangenteA_x * t * t12 + 3 * self.tangenteB_x * t2 * t1 + self.P3_x * t3

    

    #Renvoie l'ordonnée d'un point de la courbe pour une valeur de l'abscisse comprise entre P0x et P3x.
    #Il y a quelques restrictions:
    # -self.P0_x doit être inférieur à self.P3_x
    #Renvoie NaN si aucune solution.
    def renvoie_ordonnee_via_abscisse(self, xt):

        if xt<self.P0_x or xt>self.P3_x: return 0
        t = 0.5
        div = 0.25
        t1 = self.renvoie_t1_retournement_x()
        #Cas d'un retournement:
        if t1 > 0:
            abscisse_t1 = self.renvoie_abscisse(t1)
            while True: #for (var i:int = 0 i < 10i++)
            
                x_test = self.renvoie_abscisse(t)
                if (t > t1) and (x_test<abscisse_t1):
                
                    x_test = abscisse_t1
                

                if x_test == xt: break
                if x_test < xt:
                
                    if xt - x_test < self.precision: break
                    else: t += div
                
                else:
                
                    if x_test-xt < self.precision: break
                    else: t -= div
                
                div /= 2.
            
        
        #Pas de retournement:
        else:
        
            while True: #for (var i:int = 0 i < 10i++)
            
                x_test = self.renvoie_abscisse(t)
                #if (t>0.00001)printf("xt:%f, x_test:%f, t:%f\n",xt,x_test,t)
                if x_test == xt: break
                if x_test < xt:
                
                    if (xt - x_test) < self.precision: break
                    else: t += div
                
                else:
                
                    if (x_test-xt) < self.precision: break
                    else: t -= div
                
                div /= 2.
            
        return self.renvoie_ordonnee(t)
    

    #Calcul les données qui servent pour résoudre y(x):
    def resolution(self):
    
        self.alpha = -self.P0_x + 3 * self.tangenteA_x - 3 * self.tangenteB_x + self.P3_x
        self.beta = 2 * self.P0_x - 4 * self.tangenteA_x + 2 * self.tangenteB_x
        self.gamma = self.tangenteA_x - self.P0_x
        self.delta = self.beta * self.beta - 4 * self.alpha * self.gamma
    

    #Si la courbe effectue un retour sur X, renvoie la valeur de t ou ce retour débute.
    #Sinon renvoie 0.
    def renvoie_t1_retournement_x(self):

        if self.delta > 0:

            t = ( -self.beta - sqrt(self.delta)) / ( 2 * self.alpha)
            if t<1 and t>0: return t
            else: return 0

        else: return 0



    #Si la courbe effectue un retour sur X, renvoie la valeur de t ou ce retour débute.
    #Sinon renvoie 0.
    def renvoie_t2_retournement_x(self):

        if self.delta > 0:

            t = ( -self.beta + sqrt(self.delta)) / ( 2 * self.alpha)
            if t<1 and t>0: return t
            else: return 0

        else: return 0



