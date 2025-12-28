from pathlib import Path

SHADERS_DIR = Path(__file__).parent / "shaders"

def carregar (nome: str) -> str:
  return (SHADERS_DIR / nome).read_text(encoding="utf-8")