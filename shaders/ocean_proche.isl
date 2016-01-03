/*

				AQUAGENA - Eric Kernin - 2015
				Shader de rendu de l'océan


*/
in {
	tex2D texture_couleur [wrap-u: repeat, wrap-v: repeat];
	tex2D texture_bruit [wrap-u: repeat, wrap-v: repeat];
}

variant {
	vertex {
		out {
			vec2 v_uv;
			vec3 position_sommet;
			vec3 position_sommet_espace;
			vec2 texture_bruit_coord;
		}

		source %{
			float echelle_texture_bruit_ondes=10.;
			
			v_uv = vUV0;
			position_sommet=vPosition.xyz;
			position_sommet_espace=(vModelViewMatrix*vec4(vPosition,1.)).xyz;
			texture_bruit_coord = (vPosition.xz)/echelle_texture_bruit_ondes;
		%}
	}

	pixel {
		source %{
		
			#define M_PI 3.14159
			
			//======================== Calcul de la normale:
			float vitesse_ondes_0=3.;
			float quantite_ondes_0=1.;
			float frequence_ondes_0=0.3;
			float amplitude_ondes_0=15.;
			float intensite_ondes_0=0.1;
			float niveau_perturbations_ondes_0=2.;
			float facteur_perturbation_octave_0=1;
			float pas_0=vitesse_ondes_0*quantite_ondes_0*vClock;
			
			float vitesse_ondes_1=-10.;
			float quantite_ondes_1=0.03;
			float frequence_ondes_1=0.025;
			float amplitude_ondes_1=20.;
			float intensite_ondes_1=0.5;
			float niveau_perturbations_ondes_1=70;
			float facteur_perturbation_octave_1=0.;
			float pas_1=vitesse_ondes_1*quantite_ondes_1*vClock;
			
			float ocean_zNear=9000;
			float ocean_zFar=30000;
			float ocean_facteur=clamp((position_sommet_espace.z-ocean_zNear)/(ocean_zFar-ocean_zNear),0,1);
			
			
			float vitesse_ondes=vitesse_ondes_0*(1-ocean_facteur)+vitesse_ondes_1*ocean_facteur;
			float quantite_ondes=quantite_ondes_0*(1-ocean_facteur)+quantite_ondes_1*ocean_facteur;
			float frequence_ondes=frequence_ondes_0*(1-ocean_facteur)+frequence_ondes_1*ocean_facteur;
			float amplitude_ondes=amplitude_ondes_0*(1-ocean_facteur)+amplitude_ondes_1*ocean_facteur;
			float intensite_ondes=intensite_ondes_0*(1-ocean_facteur)+intensite_ondes_1*ocean_facteur;
			float facteur_perturbation_octave=facteur_perturbation_octave_0*(1-ocean_facteur)+facteur_perturbation_octave_1*ocean_facteur;
			float niveau_perturbations_ondes=niveau_perturbations_ondes_0*(1-ocean_facteur)+niveau_perturbations_ondes_1*ocean_facteur;
			float pas=pas_0*(1-ocean_facteur)+pas_1*ocean_facteur;
			
			float octave1=texture2D(texture_bruit,vec2(pas/100,0)+vec2(texture_bruit_coord.x,texture_bruit_coord.y/2)).x*2.-1.;
			float octave2=texture2D(texture_bruit,vec2(-pas/100,pas/100)+vec2(texture_bruit_coord.x/50,texture_bruit_coord.y/30)).x*2.-1.;
			float perturbation=niveau_perturbations_ondes*(octave1+octave2*facteur_perturbation_octave);
			
			
			vec3 normale=vec3(0.,1.,0.);
			vec3 tangente_sommet=vec3(1.,0.,0.);
			vec3 binormale_sommet=vec3(0.,0.,1.);
			

			normale+=normalize(tangente_sommet)
						*cos(
								position_sommet.x*quantite_ondes+perturbation
								+sin(position_sommet.z*frequence_ondes)*(amplitude_ondes*quantite_ondes)
								+pas
							)*intensite_ondes;


			normale+=normalize(binormale_sommet)
						*sin(
								position_sommet.z*quantite_ondes+perturbation
								+cos(position_sommet.x*frequence_ondes/10.123)*(amplitude_ondes*quantite_ondes)
								+pas*0.5
							)*intensite_ondes*perturbation*0.9;

			normale=normalize(normale);
			
			//============== Déplacement de la texture:
			float echelle_texture_ocean=4000.;
			float intensite_deplacement_texture=100.;
			vec2 deplacement_texture=v_uv+intensite_deplacement_texture*normale.xz/echelle_texture_ocean;
			vec4 couleur_ocean_perturbe = texture2D(texture_couleur, deplacement_texture);
			vec4 couleur_ocean = texture2D(texture_couleur, v_uv);
			couleur_ocean =couleur_ocean_perturbe*0.5+couleur_ocean*0.5;
			
			//============== Réglages HSV de la couleur de l'océan:
			float H_depart=5;
			float H_fin=0;
			float H_zNear=0.;
			float H_zFar=7000.;
			float H_facteur=clamp((position_sommet_espace.z-H_zNear)/(H_zFar-H_zNear),0,1);
			float H=H_depart*(1-H_facteur)+H_fin*H_facteur;
			
			float V_depart=1.;
			float V_fin=0.75;
			float V_zNear=100.;
			float V_zFar=2000.;
			float V_facteur=clamp((position_sommet_espace.z-V_zNear)/(V_zFar-V_zNear),0,1);
			float V=V_depart*(1-V_facteur)+V_fin*V_facteur;
			
			float S_depart=0.75;
			float S_fin=1.;
			float S_zNear=200.;
			float S_zFar=5000.;
			float S_facteur=clamp((position_sommet_espace.z-S_zNear)/(S_zFar-S_zNear),0,1);
			float S=S_depart*(1-S_facteur)+S_fin*S_facteur;
			
			
			vec4 c;
			float VSU = V*S*cos(H*M_PI/180.);
			float VSW = V*S*sin(H*M_PI/180.);

			c.r = (.299*V+.701*VSU+.168*VSW)*couleur_ocean.r
				+ (.587*V-.587*VSU+.330*VSW)*couleur_ocean.g
				+ (.114*V-.114*VSU-.497*VSW)*couleur_ocean.b;
			c.g = (.299*V-.299*VSU-.328*VSW)*couleur_ocean.r
				+ (.587*V+.413*VSU+.035*VSW)*couleur_ocean.g
				+ (.114*V-.114*VSU+.292*VSW)*couleur_ocean.b;
			c.b = (.299*V-.3*VSU+1.25*VSW)*couleur_ocean.r
				+ (.587*V-.588*VSU-1.05*VSW)*couleur_ocean.g
				+ (.114*V+.886*VSU-.203*VSW)*couleur_ocean.b;
			
			
			%diffuse% = c.rgb;
			%specular% = vec3(1.,1.,1.);
			%normal% = normale;
			//%constant% = c.rgb;
		%}
	}
}
