/*

	Simple affichage d'une texture sur la surface de l'écran
	
*/

in {
		tex2D u_tex; 
		float alpha;
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
			
			vec4 p=texture2D(u_tex,v_uv);
			p.a=alpha;
			
			%out.color% = p;
		%}
	}
}
