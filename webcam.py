import cv2
import numpy as np
import moderngl
import shaders

class Webcam:
  def __init__ (self, contextoGL, largura:int, altura:int):
    self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Para começar, vai ter o tamanho da tela
    self.cam_largura = largura
    self.cam_altura  = altura

    # Textura
    self.cam_texture = contextoGL.texture(
      (self.cam_largura, self.cam_altura),
      components=3
    )
    self.cam_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    
    # Shader
    self.cam_prog = contextoGL.program(
      vertex_shader   = shaders.carregar("webcam.vert"),
      fragment_shader = shaders.carregar("webcam.frag")
    )
    # Diz pro shader que o sampler usa a textura 0
    self.cam_prog["tex"].value = 0

    # Agora monta a parte visual
    # O quad indica onde a camera vai estar. No comeco, vai ocupar toda a tela
    self.cam_quad = np.array([
      # x,    y      u,   v
      -1.0,  1.0,   0.0, 1.0,   # superior esquerdo
       1.0,  1.0,   1.0, 1.0,   # superior direito
       1.0, -1.0,   1.0, 0.0,   # inferior direito
      -1.0, -1.0,   0.0, 0.0    # inferior esquerdo
    ], dtype="f4")

    # Atualiza o vbo
    self.atualizar_vbo(contextoGL)
    self.ctx = contextoGL

  def atualizar_vbo (self, ctx):
    self.cam_vbo = ctx.buffer(self.cam_quad.tobytes())
    self.cam_vao = ctx.vertex_array(
      self.cam_prog,
      [(self.cam_vbo, "2f 2f", "in_pos", "in_uv")]
    )
  
  def ler_cap (self):
    self.ret, self.frame = self.cap.read()
    return self.ret, self.frame
