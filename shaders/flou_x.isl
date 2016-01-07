/*

	Floutage vertical
	
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
			
			int dx;
			//textureSize(u_tex,0).x;
			
			float intensite;
			float amplitude=0.;
			
			vec4 p=vec4(0.);
			
			
			for (dx=-taille_flou;dx<taille_flou;dx++)
			{
			  intensite=1.-abs(float(dx)/float(taille_flou));
			  p+= intensite *(texture2D(u_tex,vec2(v_uv.x+float(dx)/taille_texture,v_uv.y)));
			  amplitude+=intensite;
			}
			p*=saturation_flou/amplitude;
			//p.a=1.;
			
			
			%out.color% = p;
		%}
	}
}
