"""
Funções de imagem

`imagem_para_particulas`: Transforma uma imagem em um conjunto de particulas.
"""
import numpy as np
from PIL import Image

def imagem_para_particulas (imagem:str, escala=1.0):
  # Carrega a imagem
  img = Image.open(imagem).convert("RGB")
  w, h = img.size

  # Normaliza em [0,1]
  pixels = np.asarray(img, dtype=np.float32) / 255.0
  pixels = pixels.reshape(-1,3)

  # Agora em [-1,1]
  xs = np.linspace(-1,1,w)
  ys = np.linspace(-1,1,h)
  X,Y = np.meshgrid(xs,ys)
  posicoes = np.stack([X.ravel(), -Y.ravel()], axis=1)

  return (
    posicoes.astype("f8", order="F"),
    pixels.astype("f4")
  )