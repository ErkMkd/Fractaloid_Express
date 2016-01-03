in {
	tex2D diffuse_map;
	vec3 ambient_color;
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
			%constant% = vec4(ambient_color,1.);
			%opacity% = diffuse_color.a;
			%diffuse% = diffuse_color;
		%}
	}
}

surface { blend:alpha }
