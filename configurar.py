"""
Para configurar o projeto.

1. Baixa o hand_landmarker.task para detectar maos;
2. Compila o Fortran.
"""
import sys
import subprocess
import urllib.request
from pathlib import Path

def compilar_fortran_f2py(
  arquivo_fortran: str,
  nome_modulo: str
):
  """
  Compila um arquivo Fortran em um módulo Python usando f2py,
  com flags de otimização agressivas.

  Parâmetros
  ----------
  arquivo_fortran : str
    Caminho para o arquivo .f90 / .f / .f95
  nome_modulo : str
    Nome do módulo Python a ser gerado
  """

  arquivo_fortran = Path(arquivo_fortran)
  if not arquivo_fortran.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_fortran}")

  flags_otimizacao = [
    "-O3",
    "-ffast-math",
    "-funroll-loops",
    "-march=native",
  ]

  cmd = [
    sys.executable,
    "-m", "numpy.f2py",
    str(arquivo_fortran),
    "-m", nome_modulo,
    "-c",
    "--opt=" + " ".join(flags_otimizacao),
  ]

  print("Executando comando:")
  print(" ".join(cmd))

  subprocess.run(cmd, check=True)

if __name__ == "__main__":

  ########################################################
  # Baixa o modelo de mao
  ########################################################
  URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
  DEST = Path("models/hand_landmarker.task")

  DEST.parent.mkdir(parents=True, exist_ok=True)

  if not DEST.exists():
    print("Baixando hand_landmarker.task...")
    urllib.request.urlretrieve(URL, DEST)
  else:
    print("Modelo já existe.")

  ########################################################
  # Agora compila o Fortran
  ########################################################
  compilar_fortran_f2py(
    arquivo_fortran="particulas.f90",
    nome_modulo="particulas"
  )