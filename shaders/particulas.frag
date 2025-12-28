#version 330

in vec3 v_color;
out vec4 f_color;

void main() {
  vec2 c = gl_PointCoord - vec2(0.5);
  if (dot(c,c) > 0.25) discard;
  f_color = vec4(v_color, 1.0);
}