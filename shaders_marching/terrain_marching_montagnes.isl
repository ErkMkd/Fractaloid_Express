/*

				Fractaloid Express - Eric Kernin - 2015
				Shader de rendu des montagnes enneigées en terrain marching
				La couleur d'ambiance est: couleur_zénith * intensite_ambiante


*/

in {
	tex2D texture_terrain [wrap-u: repeat, wrap-v: repeat];
	tex2D texture_terrain2 [wrap-u: repeat, wrap-v: repeat];
	tex2D texture_terrain3 [wrap-u: repeat, wrap-v: repeat];
	float ratio_ecran;
	float distanceFocale;
	vec3 obs_pos;
	mat3 obs_mat_normale;
	vec2 facteur_echelle_terrain;
	vec2 facteur_echelle_terrain2; 
	vec2 facteur_echelle_terrain3; 
	float amplitude_terrain;
	float amplitude_terrain2;
	float amplitude_terrain3;
	float facteur_precision_distance;
	vec3 couleur_horizon;
	vec3 couleur_zenith;
	vec3 couleur_neige;
	vec3 couleur_eau;
	float intensite_ambiante;
	float altitude_eau;
	vec3  l1_direction;
    vec3  l1_couleur;
    vec3  l2_direction;
    vec3  l2_couleur;
	vec2 zFrustum;
}

variant {
	
	//====================================================================================================
	
	vertex {
		out {
			vec2 v_uv;
			vec3 rayObs_dir; 
		}

		source %{
			v_uv = vUV0;
			rayObs_dir=vec3(vPosition.x,vPosition.y,0.)*vec3(1.,ratio_ecran,0.)+vec3(0.,0.,distanceFocale);
			%out.position% = vec4(vPosition, 1.0);
		%}
	}

	//====================================================================================================
	
	pixel {
			
		global %{
			
			#define EPSILON_NORMALE 0.5f
			vec3 obsDir,rayDir,normale_terrain,ray_position;
			float dist,zFrag,zDepth;
			vec3 l1d,l2d;
			float brouillard_min=10.;
			vec3 couleur_ambiante=couleur_zenith*intensite_ambiante;
			
			float calcule_zDepth(float d)
			{
				float a,b,z;
				z=-d*obsDir.z;
				a=zFrustum.y/(zFrustum.y-zFrustum.x);
				b=zFrustum.y*zFrustum.x/(zFrustum.x-zFrustum.y);
				return a+b/z;
			}
			
			float renvoie_altitude(vec2 p)
			{
				float a=texture2D(texture_terrain,p*facteur_echelle_terrain).r;
			   //return a*amplitude_terrain;
				//float b=texture(texture_terrain2,p*facteur_echelle_terrain2);
				//float c=texture(texture_terrain2,p*facteur_echelle_terrain3);

				//return (pow(a,5.)+pow(b,6.)+c)*(amplitude_terrain);
				return pow(a,5.)*amplitude_terrain;
			}
			
			float renvoie_altitude_details(vec2 p)
			{
				float a=texture2D(texture_terrain,p*facteur_echelle_terrain).r;
			   //return a*amplitude_terrain;
				float b=texture2D(texture_terrain2,p*facteur_echelle_terrain2).r;//12,753
				float c=texture2D(texture_terrain3,p*facteur_echelle_terrain3).r;

				return (pow(a,5.)*amplitude_terrain+pow(b,4.)*amplitude_terrain2+c*amplitude_terrain3);
				//return (a+b+c)*amplitude_terrain;
			}
			
			void calcul_normale(float d)
			{
				float f=EPSILON_NORMALE*(1.+(d/zFrustum.y)*100.);
				normale_terrain=normalize(vec3(
										renvoie_altitude_details(vec2(ray_position.x-f,ray_position.z)) - renvoie_altitude_details(vec2(ray_position.x+f,ray_position.z)),
										2.*f,
										renvoie_altitude_details(vec2(ray_position.x,ray_position.z-f)) - renvoie_altitude_details(vec2(ray_position.x,ray_position.z+f))
									  ));
			}
			
			//================ Calcul éclairage:
			
			vec3 calcul_eclairage(vec3 normale)
			{
				vec3 reflet_source;

				float angle_source1_normale  = max(dot(normale,l1d),0.);
				float angle_source2_normale  = max(dot(normale,l2d),0.);


				vec3 materiau_luminosite;
				vec3 materiau_diffusion;
				vec3 materiau_specularite;
				float materiau_brillance;

				if(normale.y>0.85)
				{
					float c=texture2D(texture_terrain3,ray_position.xz*facteur_echelle_terrain3).r;
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


				vec3 eclairage    = 	materiau_luminosite + couleur_ambiante; //La couleur utilisée pour l'ambiance

				eclairage    += 	materiau_diffusion * (l1_couleur *  angle_source1_normale
													 + l2_couleur *  angle_source2_normale
													);



				if (angle_source1_normale>0.)
				{
					reflet_source	=   normalize(-rayDir+l1d);
					eclairage    +=   l1_couleur * materiau_specularite * pow(max(dot(reflet_source,normale),0.),materiau_brillance);
				}

				if (angle_source2_normale>0.)
				{
					reflet_source	=   normalize(-rayDir+l2d);
					eclairage    +=   l2_couleur * materiau_specularite * pow(max(dot(reflet_source,normale),0.),materiau_brillance);
				}


				return eclairage;
			}
			
			
			//===================================== Calcul distance précise:
			
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
			
			
		%}
		
	//====================================================================================================
		
		
		source %{
			
			//obsDir=normalize(rayObs_dir);
			//vec4 couleur_texture = texture2D(texture_terrain, v_uv);
			//%out.color% = couleur_texture;
			
			//Rayon:

			obsDir=normalize(rayObs_dir);
			//zDepth=calcule_zDepth(zFrustum.y-zFrustum.y/100.);

			//Calcul la position et le vecteur directeur du rayon dans l'espace absolu (pour le moment l'observateur est dans le même repère que l'espace)
				rayDir=normalize(obs_mat_normale*obsDir);
				l1d=-l1_direction;
				l2d=-l2_direction;

			//Couleur ciel:
			vec3 couleur_brouillard_h=mix(couleur_zenith,couleur_horizon,pow(min(1.,1.-rayDir.y),3.));
			float angle_soleil=pow(max(dot(l1d,rayDir),0.),16.);
			couleur_brouillard_h=mix(couleur_brouillard_h,l1_couleur,angle_soleil);
			vec3 couleur=couleur_brouillard_h;

			//Marche:
			
				float alt,alt_prec,dist_prec;
				//ray_position=obs_pos+rayDir*zFrustum.x;
				float pas=.1;
				
				for(dist=zFrustum.x;dist<zFrustum.y;dist+=pas)
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

						//zDepth=calcule_zDepth(dist);

						calcul_normale(dist);
						
						//if(alt==altitude_eau)
						//{
							//couleur=couleur_eau;
							//break;
						//	normale_terrain=normalize(normale_terrain*0.5 + vec3(0.,1.,0.));
						//}

						couleur=calcul_eclairage(normale_terrain);

						break;
					}
					pas*=facteur_precision_distance;
					dist_prec=dist;
					alt_prec=alt;
				}
				
				//dist=zFrustum.y;

				float facteur_brouillard=clamp((dist-brouillard_min)/(zFrustum.y-brouillard_min),0.,1.);

				%out.color% = vec4(mix(couleur,couleur_brouillard_h,facteur_brouillard),1.);
				//%out.depth%=zDepth;
			

		%}
	}
}
