/*

	Fusionne 2 textures contenant deux scènes différentes, en fonction de leurs zBuffer, puis applique différents filtres de traitement des couleurs.
	
*/

in {
		tex2D u_tex_scene1;
		tex2D u_tex_scene2;
		tex2D u_tex_scene1_depth;
		tex2D u_tex_scene2_depth;
		tex2D u_tex_aura;
		float alpha_scene;
		float alpha_aura;
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
			
			// --------------- Sélection de la scène:
			
			vec4 texel_scene1;
			vec4 texel_scene2;
			//float depth1=texture2D(u_tex_scene1_depth,v_uv).r;
			//float depth2=texture2D(u_tex_scene2_depth,v_uv).r;
			//if (depth1<depth2) texel_scene=texture2D(u_tex_scene1,v_uv);
			//else texel_scene=texture2D(u_tex_scene2,v_uv);
			//PREVOIR LE FOND !
	
			texel_scene1=texture2D(u_tex_scene1,v_uv);
			texel_scene2=texture2D(u_tex_scene2,v_uv);
			vec4 texel_scene=vec4(texel_scene1.rgb*texel_scene1.a+texel_scene2.rgb*(1.-texel_scene1.a),1.);
			
			
			
			//-------------- Filtre de contraste et saturation sélectifs:
			
			vec4 texel_aura=texture2D(u_tex_aura,v_uv);
	
			vec4 p=texel_scene*alpha_scene+texel_aura*alpha_aura;
			
			float c0=p.r*FACTEUR_GRIS_R+p.g*FACTEUR_GRIS_V+p.b*FACTEUR_GRIS_B;

			
			//Contraste:
			vec3 c;
			
			c.r=clamp(p.r+contraste*(c0-seuil),0.,1.);
			c.g=clamp(p.g+contraste*(c0-seuil),0.,1.);
			c.b=clamp(p.b+contraste*(c0-seuil),0.,1.);

			
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
			
			p.a=1.;
			
			
			%out.color% = p;
		%}
	}
}
