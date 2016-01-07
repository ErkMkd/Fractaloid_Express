/*

	Simple affichage d'une texture sur la surface de l'écran
	
*/

in {
		tex2D u_tex1;
		tex2D u_tex2;
		float alpha_1;
		float alpha_2;
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
			
			vec4 p1=texture2D(u_tex1,v_uv);
			vec4 p2=texture2D(u_tex2,v_uv);
			p1*=alpha_1;
			p2*=alpha_2;
			
			%out.color% = p2+p1;
		%}
	}
}
