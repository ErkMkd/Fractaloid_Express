# -*-coding:Utf-8 -*

"""
       Générateur de bruits de perlin et interpolations basiques
"""

from random import *
from math import pi, cos
from random import *




class Bruit:

    #-----------------------------------------------------
    #  Interpolation linéaire entre deux valeurs a et b
    #  t varie entre 0 et 1 (0=a, 1=b)
    # renvoie la valeur intermédiaire.
    #-----------------------------------------------------
        @classmethod
        def interpolation_lineaire(cls,a,b,t):
            return a*(1-t)+b*t

        @classmethod
        def interpolation_lineaire_2(cls,a,b,t):
            return  a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t

        @classmethod
        def interpolation_lineaire_3(cls,a,b,t):
            return  a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t

    #-----------------------------------------------------
    #  Interpolation sinusoïdale entre deux valeurs a et b
    #  x varie entre 0 et 1 (0=a, 1=b)
    # renvoie la valeur intermédiaire.
    #-----------------------------------------------------
        @classmethod
        def interpolation_cosinusoidale(cls,a,b,t,durete):
            return cls.interpolation_lineaire(a,b,(-cos(pi*pow(t,durete))+1.)/2.)
        @classmethod
        def interpolation_cosinusoidale_2(cls,a,b,t,durete):
            return cls.interpolation_lineaire_2(a,b,(-cos(pi*pow(t,durete))+1.)/2.)
        @classmethod
        def interpolation_cosinusoidale_3(cls,a,b,t,durete):
            return cls.interpolation_lineaire_3(a,b,(-cos(pi*pow(t,durete))+1.)/2.)


   #=============================================================================================
    #                               Constructeur:
    #=============================================================================================
        def __init__(self,nom):

            self.position_trame_aleatoire_precedente=0
            self.borne_0=random()
            self.borne_1=random()
            self.reset_suite()
            self.nom=nom
            self.t0=0


    #===================================================================================
    #          Génère une valeur temporelle aléatoire, lissée selon un bruit de Perlin
    #          La valeur renvoyée est comprise entre 0 et 1
    #          t: temps en s
    #          t_prec: temps précédent en s
    #          intervalle: l'intervalle de temps entre les valeurs aléatoires à interpôler (en s)
    #===================================================================================
        def valeur_aleatoire_temporelle(self,t,intervalle,durete):

            position_interpolation=t/intervalle
            position_trame_aleatoire=int(position_interpolation)
            position_interpolation-=self.position_trame_aleatoire_precedente

            #Génère une nouvelle valeur aléatoire:
            if position_trame_aleatoire>self.position_trame_aleatoire_precedente:

                self.position_trame_aleatoire_precedente=position_trame_aleatoire
                self.borne_0=self.borne_1
                self.borne_1=random()
                position_interpolation=0.

            #Interpolation entre les deux valeurs aléatoires:
            return Bruit.interpolation_cosinusoidale(self.borne_0,self.borne_1,position_interpolation,durete)



        #--------- Avec des bornes d'interpolation extérieures:
        def valeur_aleatoire_temporelle_ext(self,t,intervalle,borne0,borne1,durete):

            position_interpolation=t/intervalle
            position_trame_aleatoire=int(position_interpolation)
            position_interpolation-=self.position_trame_aleatoire_precedente

            #Génère une nouvelle valeur aléatoire:
            if position_trame_aleatoire>self.position_trame_aleatoire_precedente:
                self.position_trame_aleatoire_precedente=position_trame_aleatoire
                position_interpolation=0

            #Interpolation entre les deux valeurs aléatoires:
            return Bruit.interpolation_cosinusoidale(borne0,borne1,position_interpolation,durete)


    #===================================================================================
    #          Génère une valeur temporelle selon une suite donnée.
    #          La valeur renvoyée est comprise entre 0 et 1
    #          t: temps en s
    #          t_prec: temps précédent en s
    #          intervalle: l'intervalle de temps entre les valeurs à interpôler (en s)
    #          suite: le tableau de valeurs à interpoler
    #===================================================================================
        def valeur_suite_temporelle(self,t,intervalle,suite):
            if self.t0==-1: self.t0=t
            t-=self.t0
            position_interpolation=t/intervalle
            position_trame=int(position_interpolation)
            position_interpolation-=position_trame
            position_trame=position_trame % len(suite)
            self.borne_0=suite[position_trame]
            if position_trame==len(suite)-1: self.borne_1=suite[0]
            else: self.borne_1=suite[position_trame+1]
            #Interpolation entre les deux valeurs aléatoires:
            return Bruit.interpolation_cosinusoidale(self.borne_0,self.borne_1,position_interpolation)

    #------------------------------------------
    #Sert à initialiser une suite fixe
    #------------------------------------------

        def reset_suite(self):
            self.t0=-1.



