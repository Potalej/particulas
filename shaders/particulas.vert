#version 330

in vec2 in_pos;
in vec3 in_color;

out vec3 v_color;

uniform float point_size;

void main() {
  gl_Position = vec4(in_pos, 0.0, 1.0);
  gl_PointSize = point_size;
  v_color = in_color;
}