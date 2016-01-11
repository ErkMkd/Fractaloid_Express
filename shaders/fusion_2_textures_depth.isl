/*

	Fusionne 2 textures contenant deux scènes différentes, en fonction de leurs zBuffer.
	
*/

in {
		tex2D u_tex_scene1;
		tex2D u_tex_scene2;
		tex2D u_tex_scene1_depth;
		tex2D u_tex_scene2_depth;
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
			
			// --------------- Sélection de la scène:
			
			vec4 texel_scene1=texture2D(u_tex_scene1,v_uv);
			vec4 texel_scene2=texture2D(u_tex_scene2,v_uv);
			//float depth1=texture2D(u_tex_scene1_depth,v_uv).r;
			//float depth2=texture2D(u_tex_scene2_depth,v_uv).r;
			//if (depth1<depth2) texel_scene=texture2D(u_tex_scene1,v_uv);
			//else texel_scene=texture2D(u_tex_scene2,v_uv);
			//PREVOIR LE FOND !
			
			%out.color% = vec4(texel_scene1.rgb*texel_scene1.a+texel_scene2.rgb*(1.-texel_scene1.a),1.);
		%}
	}
}
