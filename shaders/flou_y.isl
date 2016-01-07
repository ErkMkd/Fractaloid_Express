/*

	Floutage horizontal
	
*/

in {
		tex2D u_tex; 

		int taille_flou;
		float saturation_flou;
		float taille_texture;
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
	
			int dy;
			//textureSize(u_tex,0).y;
			float intensite;
			float amplitude=0.;
			vec4 p=vec4( 0.);
			for (dy=-taille_flou;dy<taille_flou;dy++)
			{
			  intensite=1.-abs(float(dy)/float(taille_flou));
			  p+= intensite *(texture2D(u_tex,vec2(v_uv.x,v_uv.y+float(dy)/taille_texture)));
			  amplitude+=intensite;
			}
			p*=saturation_flou/amplitude;
			//p.a=1.;
			
			%out.color% = p;
		%}
	}
}
