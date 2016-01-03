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
			%diffuse% = vec3(0.,0.,0.);
			%specular% = vec3(0.,0.,0.);
			%constant% = diffuse_color.xyz;
		%}
	}
}
