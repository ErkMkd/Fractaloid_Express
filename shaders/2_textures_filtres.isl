/*

	Fusionne 2 textures et applique différents filtres de traitement des couleurs.
	
*/

in {
		tex2D u_tex1;
		tex2D u_tex2;
		float alpha_1;
		float alpha_2;

		//Premier passage:
		//float saturation;
		float contraste;
		float seuil;
		float H;
		float S;
		float V; //Limite 0 pour le contrast (les valeurs inférieures sont assombries, les supérieures éclaircies);
	}

variant {
	
	vertex {
		out { vec2 v_uv; }

		source %{
			v_uv = vUV0;
			%out.position% = vec4(vPosition, 1.0);
		%}
	}

	pixel {
		in { vec2 v_uv;
				
			}

		source %{
			#define M_PI 3.14159
			#define FACTEUR_GRIS_R 0.11
			#define FACTEUR_GRIS_V 0.59
			#define FACTEUR_GRIS_B 0.3
			
			//-------------- Filtre de contraste et saturation sélectifs:
			
			vec4 c;
			vec4 p=texture2D(u_tex1,v_uv);
			vec4 p1=texture2D(u_tex2,v_uv);
			p=p*alpha_1+p1*alpha_2;
			
			float c0=p.r*FACTEUR_GRIS_R+p.g*FACTEUR_GRIS_V+p.b*FACTEUR_GRIS_B;


			//Contraste:
			c.r=clamp(p.r+contraste*(c0-seuil),0.,1.);
			c.g=clamp(p.g+contraste*(c0-seuil),0.,1.);
			c.b=clamp(p.b+contraste*(c0-seuil),0.,1.);

			
			//c.a=clamp(c.b+contraste*(c0-seuil),0.,1.);	//Couche alpha en fonction de la luminosité du pixel
			c.a=1.;
			
			//--------------- Filtre Hue,Saturation(de couleurs),Value: 
			
			float VSU = V*S*cos(H*M_PI/180.);
			
			float VSW = V*S*sin(H*M_PI/180.);
			
			p.r = (.299*V+.701*VSU+.168*VSW)*c.r
				+ (.587*V-.587*VSU+.330*VSW)*c.g
				+ (.114*V-.114*VSU-.497*VSW)*c.b;
			p.g = (.299*V-.299*VSU-.328*VSW)*c.r
				+ (.587*V+.413*VSU+.035*VSW)*c.g
				+ (.114*V-.114*VSU+.292*VSW)*c.b;
			p.b = (.299*V-.3*VSU+1.25*VSW)*c.r
				+ (.587*V-.588*VSU-1.05*VSW)*c.g
				+ (.114*V+.886*VSU-.203*VSW)*c.b;
			
			p.a=c.a;

			
			%out.color% = p;
		%}
	}
}
