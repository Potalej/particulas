import cv2
import time
import moderngl
import numpy as np
import shaders
from mao import *

#######################################################################
# Threads
#######################################################################
import threading
   
# Para o programa poder encerrar
evento_parada_thread = threading.Event()

# Para atualizar os frames
ultimo_frame = None
frame_lock = threading.Lock()

#######################################################################
# Mediapipe, para deteccao da mao
#######################################################################
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class Mao:
  
  def __init__ (self, foto_saida:str="foto.png", x:float=0.0, y:float=0.0, vx:float=0.0, vy:float=0.0):
    # Posicoes e velocidades
    self.x, self.y, self.vx, self.vy = x, y, vx, vy
    
    # Pontos da mao
    self.pontos_mao = []

    # Se a mao esta ativa
    self.ativa = False

    # Thread
    self.lock = threading.Lock()

    # Se a foto foi tirada
    self.foto_tirada_evento = threading.Event()
    self.foto_saida = foto_saida

    # Cronometro
    self.cronometro      = 0.0
    self.cronometro_teto = 3.0

    # Criterio para tirar a foto
    self.foto_funcao_criterio = verifica_saudacao_vulcana

    # Inicializacao do Mediapipe
    BaseOptions = python.BaseOptions
    HandLandmarker = vision.HandLandmarker
    HandLandmarkerOptions = vision.HandLandmarkerOptions
    VisionRunningMode = vision.RunningMode

    opcoes = HandLandmarkerOptions(
      base_options=BaseOptions(model_asset_path="models/hand_landmarker.task"),
      running_mode=VisionRunningMode.VIDEO,
      num_hands=1
    )
    self.detector = HandLandmarker.create_from_options(opcoes)

  def atualiza_frame (self, webcam):
    """
    Rotina que roda dentro das threads desta classe.
    """
    global ultimo_frame, frame_lock

    ret, frame = webcam.ler_cap()
    if not ret: 
      return False, False, False
    frame = cv2.flip(frame,1)

    # Salva frame para OpenGL
    with frame_lock: ultimo_frame = frame.copy()

    # Mediapipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_imagem = mp.Image(
      image_format = mp.ImageFormat.SRGB,
      data = frame_rgb
    )

    # Detecta a mao
    ts = int(time.time()*1e3)
    resultado = self.detector.detect_for_video(mp_imagem, ts)

    return True, frame, resultado

  def thread_foto (self, webcam):
    """
    Aqui se roda um loop para tirar uma foto do usuario
    """
    
    self.ativar_captura = False
    self.cronometro = 0.0 

    try:
      while not self.foto_tirada_evento.is_set():
        # Captura e atualiza o frame e o resultado da deteccao de mao
        ret, frame, resultado = self.atualiza_frame(webcam)
        if not ret: continue

        # Se bater o timer, tira a foto
        if self.ativar_captura and self.cronometro >= self.cronometro_teto:
          # Salva a foto
          cv2.imwrite(self.foto_saida, frame)
          print("Foto tirada.")

          # Encerra a thread
          self.cronometro = 0.0
          self.ativar_captura = False
          self.foto_tirada_evento.set()
          continue

        # Para tirar a foto, vamos ver se a mao fez o gesto
        tempo_agora = time.time()
        if resultado.hand_landmarks:
          # Se tem alguma mao, ativa
          self.ativa = True
          
          # Pega a primeira mao
          mao = resultado.hand_landmarks[0]
          self.pontos_mao = mao

          # Roda o a funcao de criterio
          if self.foto_funcao_criterio(mao) and not self.ativar_captura:
            # Se esta no criterio, ativa
            self.ativar_captura = True
            hora_fechamento = tempo_agora
            self.cronometro = 0.0
        
        # Se nao detectar nenhuma mao, desativa
        else:
          self.ativa = False

        # Cronometro
        if self.ativar_captura and self.cronometro < self.cronometro_teto:
          self.cronometro = tempo_agora - hora_fechamento

        # Para sair, apertar esc
        if cv2.waitKey(1) == 27: 
          self.foto_tirada_evento.set()
          return

    except Exception as e:
      print(f"Exception: {e}")
      exit()
  
  def _atualizar_estado_mao (self, mao, agora):
    """
    Calcula a nova posicao e a nova velocidade da mao
    em um instante a partir do anterior.
    """    
    # Calcula o centro
    centro = np.array([
      np.mean([lm.x for lm in mao]),
      np.mean([lm.y for lm in mao]),
    ])

    # Calcula velocidade
    if self._centro_anterior is not None:
      dt = max(agora - self._tempo_anterior, 1e-6)
      vx = (centro[0] - self._centro_anterior[0]) / dt
      vy = (centro[1] - self._centro_anterior[1]) / dt
    else:
      vx = vy = 0.0
    
    # Atualiza valores anteriores
    self._centro_anterior = centro
    self._tempo_anterior  = agora

    # Atualiza a mao
    with self.lock:
      self.x = 2 * centro[0] - 1
      self.y = 1 - 2 * centro[1]
      self.vx = 2 * vx
      self.vy = -2 * vy
      self.ativa = True

  def thread_loop (self, webcam):
    """
    Aqui se roda o loop para o usuario interagir com as particulas da tela.
    """
    global evento_parada_thread

    self._centro_anterior = None
    self._tempo_anterior  = None

    try:
      while not evento_parada_thread.is_set():
        # Captura e atualiza o frame e o resultado da deteccao de mao
        ret, frame, resultado = self.atualiza_frame(webcam)
        if not ret: continue

        # Para tirar a foto, vamos ver se a mao fez o gesto
        tempo_agora = time.time()
        if resultado.hand_landmarks:
          # Se tem alguma mao, ativa
          self.ativa = True
          
          # Pega a primeira mao
          mao = resultado.hand_landmarks[0]
          self.pontos_mao = mao

          # Calcula a posicao da mao
          self._atualizar_estado_mao(mao, tempo_agora)
        
        # Se nao detectar nenhuma mao, desativa
        else:
          self.ativa = False

        # Limita FPS
        time.sleep(1 / 60)

    except Exception as e:
      print(f"Exception: {e}")
      exit()

#######################################################################
# Tela
#######################################################################
import pyglet
from webcam import Webcam
from imagem import imagem_para_particulas
from particulas import particulas_mod as pf
from fps import FPSContador

teclado = pyglet.window.key.KeyStateHandler()

def circulo (raio=5.0, segmentos=32):
  angulos = np.linspace(0, 2*np.pi, segmentos, endpoint=False)
  circ = np.stack([raio*np.cos(angulos),raio*np.sin(angulos)], axis=1)
  return circ.astype("f4")

class Tela (pyglet.window.Window):

  def __init__ (self, largura:int, altura:int, img:str="", tamanho_ponto:float=3.0, forca:float=0.5):
    # Inicializando a classe pai
    super().__init__(largura, altura, "Matemateca", resizable=True)
    self.tela_largura = largura
    self.tela_altura  = altura

    self.tirar_foto = (img == "")
    self.img = img if img != "" else "img/tmp.png"

    # Contexto do OpenGL
    self.ctx = moderngl.create_context()

    # Tamanho dos pontos
    self._tamanho_ponto = tamanho_ponto
    self.forca = forca

    # Webcam
    self._iniciar_webcam()

    # Mao
    self._iniciar_mao()

    # Contador de FPS
    fps = 60
    self.fps_contador = FPSContador(fps)
    self.fps_texto    = pyglet.text.Label(
      "FPS: 0", x = 10, y = 10, color = (255, 255, 255, 255)
    )

    # Deteccao de teclas
    self.push_handlers(teclado)

    # Comeca a chamar a funcao de atualizar
    pyglet.clock.schedule_interval(self.atualizar, 1 / fps)

  def _iniciar_estado_particulas (self):
    """
    Inicia o estado das particulas.
    """
    self.posicoes, self.cores = imagem_para_particulas(self.img)
    self.N = self.posicoes.shape[0]
    self.posicoes = self.posicoes.T.copy(order="F")
    self.velocidades = np.zeros_like(self.posicoes)

  def _iniciar_particulas (self):
    """
    Inicializa as particulas do sistema.
    """
    self.prog = self.ctx.program(
      vertex_shader   = shaders.carregar("particulas.vert"),
      fragment_shader = shaders.carregar("particulas.frag")
    )
    self.prog["point_size"].value = self._tamanho_ponto

    self._iniciar_estado_particulas()

    # OpenGL das particulas e das cores
    self.vbo_pos = self.ctx.buffer(self.posicoes.T.astype("f4", copy=False).tobytes())
    self.vbo_cor = self.ctx.buffer(self.cores.tobytes())

    # Buffer na GPU
    self.vbo = self.ctx.buffer(self.posicoes.tobytes())

    # VAO (Vertex Array Object)
    self.vao = self.ctx.vertex_array(
      self.prog,
      [
        (self.vbo_pos, "2f", "in_pos"),
        (self.vbo_cor, "3f", "in_color")
      ]
    )

  def _iniciar_webcam (self):
    """
    Inicializa a webcam na tela.
    """
    self.webcam = Webcam(self.ctx, self.tela_largura, self.tela_altura)
    self.ctx = self.webcam.ctx

    self.texto_central = pyglet.text.Label(
      "", font_name="Consolas", font_size=24,
      x=self.tela_largura // 2, y=self.tela_altura // 2,
      anchor_x="center", anchor_y="center", color=(255, 255, 255, 255),
      weight="bold"
    )

  def _iniciar_mao (self):
    """
    Inicializa a deteccao da mao.
    """
    self.mao = Mao(self.img)
    self.foto_tirada = False
    self.inicio_contador = None if self.tirar_foto else 1.0

    # Textos
    self.texto_cronometro = pyglet.text.Label(
      "Inicializando...", font_name="Consolas", font_size=14,
      x=10, y=self.tela_altura - 10,
      anchor_x="left", anchor_y="top", color=(255, 0, 0, 255)
    )
    self.texto_mao = pyglet.text.Label(
      "Inicializando...", font_name="Consolas", font_size=14,
      x=10, y=self.tela_altura - 40,
      anchor_x="left", anchor_y="top", color=(255, 255, 255, 255)
    )
    
    # Parte visual
    self.mao_prog = self.ctx.program(
      vertex_shader   = shaders.carregar("mao.vert"),
      fragment_shader = shaders.carregar("mao.frag")
    )
    self.mao_circulo = circulo(raio=0.05, segmentos=10)
    self.mao_vbo = self.ctx.buffer(self.mao_circulo.tobytes())
    self.mao_vao = self.ctx.vertex_array(
      self.mao_prog,
      [(self.mao_vbo, "2f", "in_pos")]
    )

    if self.tirar_foto:
      self._iniciar_mao_foto()
    else:
      self._iniciar_mao_thread() # Inicia a mao          
      self._iniciar_particulas() # Inicia as particulas
      self.foto_tirada = True

  def _iniciar_mao_foto (self):
    """
    Inicializa a deteccao da mao para tirar foto.
    """
    # Thread da foto
    self.mao_foto_thread = threading.Thread(
      target=self.mao.thread_foto,
      args=(self.webcam,),
      daemon=True
    )
    self.mao_foto_thread.start()

  def _iniciar_mao_thread (self):
    # Diminui o tamanho da webcam
    self.webcam.cam_quad = np.array([
      #   x,     y,     u, v
      -1.0,   1.0,    0.0, 1.0,
      -0.4,   1.0,    1.0, 1.0,
      -0.4,   0.4,    1.0, 0.0,
      -1.0,   0.4,    0.0, 0.0,
    ], dtype="f4")
    
    self.webcam.atualizar_vbo(self.ctx)
    self.ctx = self.webcam.ctx

    # Inicia a thread da mao
    self.mao_thread = threading.Thread(
      target=self.mao.thread_loop,
      args=(self.webcam,),
      daemon=True
    )
    self.mao_thread.start()

  def _loop_foto_ainda_nao_tirar (self, frame):
    """
    Loop interno da funcao atualizar, que eh chamado toda vez que a foto
    ainda nao tiver sido tirada (se for o caso).
    """
    if frame is not None:
      if not self.mao.foto_tirada_evento.is_set():
        # Atualiza as informacoes
        if self.mao.ativa: 
          self.texto_mao.text = "Mão detectada!"
          self.texto_mao.color = (0, 255, 0, 255)
        else:
          self.texto_mao.text = "Mão não detectada!"
          self.texto_mao.color = (255, 0, 0, 255)

        # Cronometro
        if self.mao.cronometro == 0:
          self.texto_cronometro.text = f"Vida longa e próspera para tirar foto!"
          self.texto_cronometro.color = (255, 0, 0, 255)
        else:
          self.texto_cronometro.text = f"Tirando a foto em {3 - int(self.mao.cronometro)}"
          self.texto_cronometro.color = (0, 255, 0, 255)

      # Se tiver sido tirada, faz o timer
      else:
        if self.inicio_contador is None:
          self.inicio_contador = time.time()
        
        else:
          dif_t = time.time() - self.inicio_contador
          if dif_t <= 3.0:
            self.texto_central.text = f"Iniciando em {3.0 - int(dif_t)}..."
          else:
            self._iniciar_mao_thread() # Inicia a mao          
            self._iniciar_particulas() # Inicia as particulas
            self.foto_tirada = True

  def _loop_atualizar_webcam (self, frame):
    """
    Parte do loop dentro da funcao de atualizacao que atualizaca
    a imagem da webcam, incluindo os pontinhos da mao.
    """
    if frame is not None:
      # Pontos da mao
      if self.mao.ativa:
        for ponto in self.mao.pontos_mao:
          x = int(ponto.x * frame.shape[1])
          y = int(ponto.y * frame.shape[0])
          cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

      # Exibe a camera
      frame = cv2.resize(frame, (self.webcam.cam_largura, self.webcam.cam_altura))
      frame = cv2.flip(frame, 0)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      self.webcam.cam_texture.write(frame.tobytes())
    
    return frame

  def atualizar (self, dt:float):
    """
    Faz a atualizacao das posicoes das particulas e das texturas.
    """
    global frame_lock, ultimo_frame, teclado

    # FPS
    fps = self.fps_contador.atualizar()
    self.fps_texto.text = f"FPS: {fps:.1f}"

    # Atualiza a textura da webcam
    with frame_lock:
      frame = None if ultimo_frame is None else ultimo_frame.copy()
    
    # Atualiza a webcam
    frame = self._loop_atualizar_webcam(frame)

    # Agora vamos ver se a foto ja foi tirada
    if not self.foto_tirada:
      self._loop_foto_ainda_nao_tirar(frame)
      return

    # Le o estado da mao
    with self.mao.lock:
      mx, my = self.mao.x, self.mao.y
      mvx, mvy = self.mao.vx, self.mao.vy
      mativa = self.mao.ativa

    if mativa:
      self.mao_prog["offset"].value = (mx, my)
    
    # Interacao com as particulas
    # Existe apenas se a mao estiver na tela
    forca = self.forca if mativa else 0.0
    pf.atualizar_particulas(
      self.posicoes, self.velocidades, # particulas
      mx, my, mvx, mvy,                # mouse
      dt, 1.0, forca
    )

    # Envia as posicoes para a GPU
    self.vbo_pos.write(
      self.posicoes.T.astype("f4", copy=False).tobytes()
    )
  
  def on_draw (self):
    """
    Chamada automaticamente na hora de fazer os desenhos
    """
    self.clear()
    self.ctx.clear(0.05, 0.05, 0.05)
    
    # Reinicia se apertar espaco
    if teclado[pyglet.window.key.SPACE]:
      self._iniciar_estado_particulas()
      return
    
    if self.foto_tirada:
      self.vao.render(mode = moderngl.POINTS)

    # Mao
    if self.mao.ativa:
      self.mao_vao.render(mode=moderngl.TRIANGLE_FAN)
    
    # Webcam
    self.webcam.cam_texture.use(location=0)
    self.webcam.cam_vao.render(mode=moderngl.TRIANGLE_FAN)
    if not self.foto_tirada:
      self.texto_mao.draw()
      self.texto_cronometro.draw()

    # Inicializador
    if not self.foto_tirada and self.inicio_contador is not None:
      self.texto_central.draw()

    # FPS
    self.fps_texto.draw()

  def on_close (self):
    """
    Quando fechar
    """
    evento_parada_thread.set()
    if self.foto_tirada:
      if self.mao_thread.is_alive():
        self.mao_thread.join(timeout=1.0)
    super().on_close()
    