import numpy as np

#######################################################################
# Rotinas de utilidades
#######################################################################

def angulo(a:float, b:float, c:float)->float:
  """ 
  Angulo ABC 
  """
  ba = a - b
  bc = c - b
  cosang = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc) + 1e-8)
  return np.degrees(np.arccos(np.clip(cosang, -1, 1)))

def dedo_estendido (pts:list, base:int, ponta:int)->bool:
  """
  Aqui se verifica se entre o pulso e a ponta do dedo, o
  angulo formado na base do dedo eh de pelo menos 160
  graus.
  """
  return angulo(pts[0], pts[base], pts[ponta]) > 160

def escala_mao (pts:list)->float:
  """
  Distancia entre o pulso e a base do dedo medio
  """
  return np.linalg.norm(pts[0] - pts[9])

def verifica_saudacao_vulcana (mao)->float:
  """
  Verifica se a mao detectada esta fazendo a saudacao vulcana.
  """
  pts = np.array([(lm.x, lm.y, lm.z) for lm in mao])
  s = escala_mao(pts)

  # Indices considerados
  i, m, r, p = 8, 12, 16, 20

  # Distancias normalizadas
  d_im = np.linalg.norm(pts[i] - pts[m]) / s
  d_mr = np.linalg.norm(pts[m] - pts[r]) / s
  d_rp = np.linalg.norm(pts[r] - pts[p]) / s

  # Dedos estendidos
  if not all([
    dedo_estendido(pts, 6, i),
    dedo_estendido(pts, 10, m),
    dedo_estendido(pts, 14, r),
    dedo_estendido(pts, 18, p),
  ]):
    return False

  # regras
  juntos_1 = d_im < d_mr
  juntos_2 = d_rp < d_mr
  separados = d_mr > 0.5

  return juntos_1 and juntos_2 and separados
