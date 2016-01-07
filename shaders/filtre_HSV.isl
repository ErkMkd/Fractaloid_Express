/*

	Filtre HSV (hue, saturation,value) sur une texture

*/

in {
		tex2D u_tex; 

		//Premier passage:
		float H;
		float S;
		float V;
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
			
			
			vec4 p;
			vec4 c=texture2D(u_tex,v_uv);
		
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
