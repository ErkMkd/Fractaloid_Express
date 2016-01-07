/*

	Contraste pour préparer l'aura des surfaces claires

*/

in {
		tex2D u_tex; 
		float saturation;
		float contraste;
		float seuil;	//Limite 0 pour le contraste (les valeurs inférieures sont assombries, les supérieures éclaircies)
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
			
			//-------------- Filtre de contraste et saturation sélectifs (sert surtout pour préparer l'effet d'aura):
			
			vec4 c;
			vec4 p=texture2D(u_tex,v_uv);
			
			float c0=p.r*FACTEUR_GRIS_R+p.g*FACTEUR_GRIS_V+p.b*FACTEUR_GRIS_B;

			//Saturation:
			c.r=saturation*(p.r-c0)+c0;
			c.g=saturation*(p.g-c0)+c0;
			c.b=saturation*(p.b-c0)+c0;

			//Contraste:
			c.r=clamp(c.r+contraste*(c0-seuil),0.,1.);
			c.g=clamp(c.g+contraste*(c0-seuil),0.,1.);
			c.b=clamp(c.b+contraste*(c0-seuil),0.,1.);

			
			//c.a=clamp(c.b+contraste*(c0-seuil),0.,1.);	//Couche alpha en fonction de la luminosité du pixel
			c.a=1.;
			
			%out.color% = c;
		%}
	}
}
