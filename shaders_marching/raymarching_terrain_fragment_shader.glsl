//******************************************************************
//
//		Ray marching
//
//*******************************************************************

#version 400

#define EPSILON_NORMALE 0.5f

layout (location=0) out vec4 outColor;

layout(std140) uniform eclairages_2si
{
    vec4 lumiere_ambiante;
    vec4 couleur_brouillard;
    float brouillard_min;
    float brouillard_max;

    vec3  l1_direction; ///La direction doit avoir été calculée dans le bon repère au moment de l'initialisation du bloc
    vec4  l1_couleur;   //L'intensité est gérée en amont
    vec4  l1_ambiance;

    vec3  l2_direction;
    vec4  l2_couleur;
    vec4  l2_ambiance;
};

uniform vec3 obs_pos;		//Position observateur
uniform mat3 obs_mat_normale;		//Matrice normale de l'observateur
uniform float zMin;
uniform float zMax;
uniform vec2 facteur_echelle_terrain; // à calculer en amont: 1./taille_terrain.x, 1./taille_terrain.y
uniform vec2 facteur_echelle_terrain2; // à calculer en amont: 1./taille_terrain.x, 1./taille_terrain.y
uniform vec2 facteur_echelle_terrain3; // à calculer en amont: 1./taille_terrain.x, 1./taille_terrain.y
uniform sampler2D texture_terrain;
uniform sampler2D texture_terrain2;
uniform sampler2D texture_terrain3;
uniform float amplitude_terrain;
uniform float amplitude_terrain2;
uniform float amplitude_terrain3;
uniform float facteur_precision_distance;

in vec3 rayObs_dir;
vec3 obsDir,rayDir,normale_terrain,ray_position;
float dist,zFrag,zDepth;
vec3 l1d,l2d;


float altitude_eau=150.;

const vec3 couleur_eau=const vec3(117./255.,219./255.,211./255.);


const vec3 couleur_brouillard_horizon=const vec3(10./255.,1./255.,5./255.);
const vec3 couleur_neige=const vec3(.91,.91,1.);

float renvoie_altitude(vec2 p)
{
    float a=texture(texture_terrain,p*facteur_echelle_terrain);
   //return a*amplitude_terrain;
    //float b=texture(texture_terrain2,p*facteur_echelle_terrain2);
    //float c=texture(texture_terrain2,p*facteur_echelle_terrain3);

    //return (pow(a,5.)+pow(b,6.)+c)*(amplitude_terrain);
    return pow(a,5.)*amplitude_terrain;
}

float renvoie_altitude_details(vec2 p)
{
    float a=texture(texture_terrain,p*facteur_echelle_terrain);
   //return a*amplitude_terrain;
    float b=texture(texture_terrain2,p*facteur_echelle_terrain2);//12,753
    float c=texture(texture_terrain3,p*facteur_echelle_terrain3);

    return (pow(a,5.)*amplitude_terrain+pow(b,4.)*amplitude_terrain2+c*amplitude_terrain3);
    //return (a+b+c)*amplitude_terrain;
}

void calcul_normale(float d)
{
    float f=EPSILON_NORMALE*(1.+(d/zMax)*100.);
    normale_terrain=normalize(vec3(
                            renvoie_altitude_details(vec2(ray_position.x-f,ray_position.z)) - renvoie_altitude_details(vec2(ray_position.x+f,ray_position.z)),
                            2.*f,
                            renvoie_altitude_details(vec2(ray_position.x,ray_position.z-f)) - renvoie_altitude_details(vec2(ray_position.x,ray_position.z+f))
                          ));
}


vec3 calcul_eclairage(vec3 normale)
{
    vec3 reflet_source;

    float angle_source1_normale  = max(dot(normale,l1d),0.);
    float angle_source2_normale  = max(dot(normale,l2d),0.);


    vec3 materiau_luminosite;
    vec3 materiau_ambiance=vec3(1.,1.,1.);
    vec3 materiau_diffusion;
    vec3 materiau_specularite;
    float materiau_brillance;

    if(normale.y>0.85)
    {
        float c=texture(texture_terrain3,ray_position.xz*facteur_echelle_terrain3);
        if(c<0.25)
        {
           materiau_luminosite=max(1.-dist/500.,0.)*couleur_neige;
        }
        else
        {
            materiau_luminosite=vec3(0.,0.,0.);
        }
        materiau_diffusion=couleur_neige;
        materiau_specularite=vec3(.3,.3,.3);
        materiau_brillance=10.;
    }
    else
    {
        vec3 couleur_mineral1=vec3(0.3,0.3,0.3);
        vec3 couleur_mineral2=vec3(122./255.,105./255.,95./255.);
        materiau_luminosite=vec3(0.,0.,0.);
        materiau_diffusion=mix(couleur_mineral2,couleur_mineral1,clamp((ray_position.y-50.)/(200.-50.),0.,1.));
        materiau_specularite=vec3(.1,.1,.1);
        materiau_brillance=30.;
    }


    vec3 eclairage    = 	materiau_luminosite + materiau_ambiance * (l1_ambiance.rgb+l2_ambiance.rgb) * lumiere_ambiante.rgb;

    eclairage    += 	materiau_diffusion * (l1_couleur.rgb *  angle_source1_normale
                                         + l2_couleur.rgb *  angle_source2_normale
                                        );



    if (angle_source1_normale>0.)
    {
        reflet_source	=   normalize(-rayDir+l1d);
        eclairage    +=   l1_couleur.rgb * materiau_specularite * pow(max(dot(reflet_source,normale),0.),materiau_brillance);
    }

    if (angle_source2_normale>0.)
    {
        reflet_source	=   normalize(-rayDir+l2d);
        eclairage    +=   l2_couleur.rgb * materiau_specularite * pow(max(dot(reflet_source,normale),0.),materiau_brillance);
    }


    return eclairage;
}


float renvoie_dist_precise(float d0,float d1,float a0, float a1)
{
    /*
    float d_mid,alt_mid;
    vec3 ray;

    for(int i=0;i<10;i++)
    {
        d_mid=d0+(d1-d0)/2.;
        ray=obs_pos+rayDir*d_mid;
        alt_mid=renvoie_altitude_details(ray.xz);
        if(alt_mid<ray.y) d0=d_mid;
        else if(alt_mid>ray.y) d1=d_mid;
        else break;
    }
    return d_mid;
    */

    /*
    vec3 ray0=obs_pos+rayDir*d0;
    vec3 ray1=obs_pos+rayDir*d1;
    float alt0=renvoie_altitude_details(ray0.xz);
    float alt1=renvoie_altitude_details(ray1.xz);
    float d_alt0=ray0.y-alt0;
    float d_alt1=alt1-ray1.y;
    return d0+(d1-d0)*(d_alt0/(d_alt0+d_alt1));
    */


    float ray0=obs_pos.y+rayDir.y*d0;
    float ray1=obs_pos.y+rayDir.y*d1;
    float d_alt0=ray0-a0;
    float d_alt1=a1-ray1;
    return d0+(d1-d0)*(d_alt0/(d_alt0+d_alt1));
}

float calcule_zDepth(float d)
{
    float a,b,z;
    z=-d*obsDir.z;
    a=zMax/(zMax-zMin);
    b=zMax*zMin/(zMin-zMax);
    return a+b/z;
}

void main( void )
{


    //Rayon:

        obsDir=normalize(rayObs_dir);
        zDepth=calcule_zDepth(zMax-zMax/100.);

    //Calcul la position et le vecteur directeur du rayon dans l'espace absolu (pour le moment l'observateur est dans le même repère que l'espace)
        rayDir=normalize(obs_mat_normale*obsDir);
        l1d=obs_mat_normale*l1_direction;
        l2d=obs_mat_normale*l2_direction;

    //Couleur ciel:
    vec3 couleur_brouillard_h=mix(couleur_brouillard.rgb,couleur_brouillard_horizon,pow(min(1.,1.-rayDir.y),3.));
    float angle_soleil=pow(max(dot(l1d,rayDir),0.),16.);
    couleur_brouillard_h=mix(couleur_brouillard_h,l1_couleur.rgb,angle_soleil);
    vec3 couleur=couleur_brouillard_h;

    //Marche:

        float alt,alt_prec,dist_prec;
        //ray_position=obs_pos+rayDir*zMin;
        float pas=.1;

        for(dist=zMin;dist<zMax;dist+=pas)
        {

            ray_position=obs_pos+rayDir*dist;
            if(rayDir.y>0. && ray_position.y>amplitude_terrain) break;
            if(rayDir.y>0.7) break;

            //alt=max(renvoie_altitude(ray_position.xz),altitude_eau);
            alt=renvoie_altitude_details(ray_position.xz);
            if (alt>ray_position.y)
            {
                dist=renvoie_dist_precise(dist_prec,dist,alt_prec,alt);
                ray_position=obs_pos+rayDir*dist;

                zDepth=calcule_zDepth(dist);

                calcul_normale(dist);
                /*
                if(alt==altitude_eau)
                {
                    //couleur=couleur_eau;
                    //break;
                    normale_terrain=normalize(normale_terrain*0.5 + vec3(0.,1.,0.));
                }*/

                couleur=calcul_eclairage(normale_terrain);

                break;
            }
            pas*=facteur_precision_distance;
            dist_prec=dist;
            alt_prec=alt;
        }



        float facteur_brouillard=clamp((dist-brouillard_min)/(brouillard_max-brouillard_min),0.,1.);

        outColor = vec4(mix(couleur,couleur_brouillard_h,facteur_brouillard),1.);


        gl_FragDepth=zDepth;
}
