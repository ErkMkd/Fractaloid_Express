in {
	tex2D diffuse_map [wrap-u: repeat, wrap-v: repeat];
}

variant {
	vertex {
		out {
			vec2 v_uv;
		}

		source %{
			v_uv = vUV0;
		%}
	}

	pixel {
		source %{
			vec4 diffuse_color = texture2D(diffuse_map, v_uv);
			%opacity% = diffuse_color.a;
			%diffuse% = diffuse_color.rgb;
		%}
	}
}

surface { blend:alpha }
