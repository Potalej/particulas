import pygame
import random
import sys
import math

# Inicialize o Pygame
pygame.init()

# Defina as dimensões da janela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Partículas no Pygame")

# Para texto
font = pygame.font.Font(None, 36)  # Usando a fonte padrão e tamanho 36
font_small = pygame.font.Font(None, 24)  # Fonte menor para o FPS

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

DIST_MIN = 50

# Classe para particulas
class Particula:
  def __init__ (self, x, y):
    self.x = x
    self.y = y
    # self.size = random.randint(3, 6)
    self.size = 1.0
    self.color = RED
    self.life = random.randint(30, 60)  # Tempo de vida da partícula
    self.vx = random.uniform(-2, 2)
    self.vy = random.uniform(-2, 2)

  def atualizar (self, mouse):
    
    # colidindo com as paredes
    if self.x >= WIDTH or self.x <= 0:
      if self.x > WIDTH: self.x = WIDTH - 1
      if self.x < 0: self.x = 1
      self.vx *= -1
      
    if self.y >= HEIGHT or self.y <= 0:
      if self.x > HEIGHT: self.x = HEIGHT - 1
      if self.x < 0: self.x = 1
      self.vy *= -1
      
    # colidindo com o mouse
    dx = mouse.x - self.x
    dy = mouse.y - self.y
    distance = math.sqrt(dx**2 + dy**2)  # Distância entre a partícula e o mouse

    if distance < DIST_MIN:  # Se a partícula está perto do mouse
      distance = math.sqrt(dx**2 + dy**2)  # Recalcular a distância normalizada

      if distance > 0:  # Evitar divisão por zero
        # Normalizar a direção e multiplicar para controlar a velocidade
        dx /= DIST_MIN
        dy /= DIST_MIN
        
        dvx = mouse.vx - self.vx
        dvy = mouse.vy - self.vy
        
        produto = dvx * dx + dvy * dy
        if produto < 0:
          self.vx = self.vx - abs(produto) * (1 if dx > 0 else -1) * mouse.x / mouse.d
          self.vy = self.vy - abs(produto) * (1 if dy > 0 else -1) * mouse.y / mouse.d

    self.x += self.vx
    self.y += self.vy
    
    self.vx *= 0.98
    self.vy *= 0.98

  def desenhar (self):
    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Mouse:
  def __init__ (self):
    self.vx = 0
    self.vy = 0
    self.x = 0
    self.y = 0
    self.d = 0
    
  def velocidade (self):
    x, y = pygame.mouse.get_pos()
    self.vx = x - self.x
    self.vy = y - self.y
    self.x = x
    self.y = y
    self.d = math.sqrt(x*x + y*y)

# Lista de partículas
particulas = []

# Loop principal
clock = pygame.time.Clock()

mouse = Mouse()
chance = 0.4

N = 20000
particulas = [Particula(WIDTH // 2, HEIGHT // 2) for i in range(N)]

while True:
  screen.fill(BLACK)  # Limpa a tela com a cor preta

  # Verifique eventos
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

  # # Crie novas partículas
  # if random.random() < chance:  # Adiciona uma partícula aleatória com probabilidade de 10%
  #   particulas.append(Particula(WIDTH // 2, HEIGHT // 2))  # Partículas surgem no centro da tela

  # Quantidade de particulas
  text = font.render(f"Particulas: {len(particulas)}", True, WHITE)  # Renderiza o texto
  screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))  # Desenha o texto na tela

  # FPS  
  fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
  screen.blit(fps_text, (WIDTH - 100, 20))  # Desenha o FPS no canto superior direito

  # Mouse
  mouse.velocidade()

  # Atualize e desenhe as partículas
  for particula in particulas[:]:
    particula.atualizar(mouse)
    particula.desenhar()
    
  pygame.draw.circle(screen, BLUE, (mouse.x, mouse.y), DIST_MIN, 10)

  pygame.display.flip()  # Atualize a tela
  clock.tick(60)  # Limite a 60 FPS
