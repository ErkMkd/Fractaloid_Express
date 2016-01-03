in {
	vec4 diffuse_color = vec4(0.7,0.7,0.7,1.0) [hint:color];
}

variant {
	pixel {
		source %{
			%constant% = diffuse_color.xyz;
			%diffuse% = diffuse_color.xyz;
		%}
	}
}

