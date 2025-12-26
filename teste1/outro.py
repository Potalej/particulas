import pygame
import random
import sys

# Inicialize o Pygame
pygame.init()

# Defina as dimensões da janela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Imagem para Partículas")

# Cores
BLACK = (0, 0, 0)

# Classe para Partículas
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = 2  # O tamanho da partícula
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Carregar a imagem
image = pygame.image.load("imagem.png")  # Substitua pelo caminho correto da sua imagem
image = pygame.transform.scale(image, (WIDTH, HEIGHT))  # Redimensiona a imagem para caber na tela

# Obter as dimensões da imagem
image_width, image_height = image.get_size()

# Lista de partículas
particles = []

# Loop principal
clock = pygame.time.Clock()

# Iterar sobre os pixels da imagem e criar partículas
for x in range(0, image_width):
    for y in range(0, image_height):
        color = image.get_at((x, y))  # Obtém a cor do pixel (r, g, b, a)
        if color == (255,255,255,255): continue
        if color.a > 0:  # Considera apenas pixels visíveis (não transparentes)
            particles.append(Particle(x, y, (color.r, color.g, color.b)))  # Cria a partícula

while True:
    screen.fill(BLACK)  # Limpa a tela com a cor preta

    # Verifique eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Atualiza e desenha as partículas
    for particle in particles[:]:
        particle.update()  # Atualiza a posição da partícula
        particle.draw()  # Desenha a partícula na tela

    # Atualize a tela
    pygame.display.flip()

    # Limite o FPS para 60 quadros por segundo
    clock.tick(60)
