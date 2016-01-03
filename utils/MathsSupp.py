"""

    Fonctions mathématiques supplémentaires
    Eric Kernin - 2015

"""

from math import sin,cos,fabs
import gs

class MathsSupp:

    #---------------------------------------------------------------
    #Rotation de points autour d'un axe:
    #---------------------------------------------------------------
    @classmethod
    def rotation_points(cls,cx,cy,cz,ax,ay,az,angle,points,points_resultat,numPoints):
        i=0
        while i<numPoints:

            px = points[3 * i] - cx
            py = points[3 * i + 1] - cy
            pz = points[3 * i + 2] - cz
            prod_scal =  px * ax + py * ay + pz * az
            cos_angle = cos(angle)
            sin_angle = sin(angle)

            points_resultat[3 * i] = cos_angle * px + sin_angle * (ay * pz - az * py) + (1 - cos_angle) * prod_scal * ax + cx
            points_resultat[3 * i + 1] = cos_angle * py + sin_angle * (az * px - ax * pz) + (1 - cos_angle) * prod_scal * ay + cy
            points_resultat[3 * i + 2] = cos_angle * pz + sin_angle * (ax * py - ay * px) + (1 - cos_angle) * prod_scal * az + cz
            i+=1

    #Version simplifiée pour la rotation d'un point:
    @classmethod
    def rotation_vecteur(cls,point,axe,angle):

        prod_scal =  point.x * axe.x + point.y * axe.y + point.z * axe.z
        cos_angle = cos(angle)
        sin_angle = sin(angle)

        return gs.Vector3(cos_angle * point.x + sin_angle * (axe.y * point.z - axe.z * point.y) + (1 - cos_angle) * prod_scal * axe.x,\
                        cos_angle * point.y + sin_angle * (axe.z * point.x - axe.x * point.z) + (1 - cos_angle) * prod_scal * axe.y,\
                        cos_angle * point.z + sin_angle * (axe.x * point.y - axe.y * point.x) + (1 - cos_angle) * prod_scal * axe.z)


    #---------------------------------------------------------------
    #Rotation de points en fonction des angles de Roulis, Tangage et Lacet:
    #  Les angles sont en radians.
    #---------------------------------------------------------------
    @classmethod
    def rotation_RTL(cls,cx,cy,cz,roulis,tangage,lacet,points,resultat,numPoints):
        sin_aR=sin(roulis)
        cos_aR=cos(roulis)
        sin_aT=sin(tangage)
        cos_aT=cos(tangage)
        sin_aL=sin(lacet)
        cos_aL=cos(lacet)
        i=0
        while i<numPoints:
            px=points[3*i]-cx
            py=points[3*i+1]-cy
            pz=points[3*i+2]-cz
            resultat[3*i]= sin_aL * ( pz*cos_aT - sin_aT * ( px*sin_aR + py*cos_aR ) ) +  cos_aL * ( px*cos_aR - py*sin_aR )+cx
            resultat[3*i+1]= pz * sin_aT + cos_aT * ( px*sin_aR + py*cos_aR )+cy
            resultat[3*i+2]= cos_aL * ( pz*cos_aT - sin_aT * ( px*sin_aR + py*cos_aR ) ) - sin_aL * ( px*cos_aR - py*sin_aR )+cz
            i+=1

    #---------------------------------------------------------------
    # Distance d'un point à un plan
    #---------------------------------------------------------------
    @classmethod
    def distance_point_plan(cls,px,py,pz, ox,oy,oz, nx,ny,nz):

        # equation du plan (OAB) : nx * ox + ny * oy + nz * oz + d = 0 or O € (OAB) donc :
        d = -nx * ox - ny * oy - nz * oz

        return fabs( -nx * px - ny * py - nz * pz - d) / (nx * nx + ny * ny + nz * nz)

    #---------------------------------------------------------------
    # Intersection d'une droite avec un plan
    #---------------------------------------------------------------
    #Renvoie le paramètre correspondant à l'intersection entre la droite (dO,dV) et plan(pO,pN)
    #La normale pN doit être unitaire.
    #Renvoie Nan si la droite est parallèle au plan.
    @classmethod
    def intersection_droite_plan(cls,dox,doy,doz, dvx,dvy,dvz,  pox,poy,poz,  pnx,pny,pnz):

        dist= - pnx*pox - pny*poy - pnz*poz
        #Test la parallèléité:
        temp=dvx*pnx + dvy*pny + dvz*pnz

        epsilon=1e-5
        if temp > -epsilon and temp < epsilon: return float('nan')

        #Calcul le facteur:
        #if (N->x<0.) return -(N->x*segment_A->x+N->y*segment_A->y+N->z*segment_A->z+D)/temp;
        #else
        return -(pnx*dox + pny*doy + pnz*doz + dist ) / temp

    #---------------------------------------------------------------
    # Altitude d'un point du plan
    #---------------------------------------------------------------
    #La normale pN doit être unitaire.
    @classmethod
    def altitude_plan(cls,x,z, pox,poy,poz,  pnx,pny,pnz):

        dist= - pnx*pox - pny*poy - pnz*poz

        return  -pnx*x-pnz*z-dist/pny

    #---------------------------------------------------------------
    # Calcul une matrice de rotation en fonction d'une cible
    #---------------------------------------------------------------
    @classmethod
    def loucate(cls,direction,normale_socle):
        axeZ=direction.Normalized()
        axeX=normale_socle.Cross(axeZ)
        axeX.Normalize()
        axeY=axeZ.Cross(axeX)
        return gs.Matrix3(axeX,axeY,axeZ)
