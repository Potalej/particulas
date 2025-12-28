import pyglet
import tela

if __name__ == "__main__":
  # Exemplo 1: Imagem com 273.000 particulas
  tela.Tela(img="img/ex1.jpg", largura=800, altura=600, tamanho_ponto=10.0)
  
  # Exemplo 2: Imagem com 646.000 particulas
  # tela.Tela(img="img/ex2.jpg", largura=800, altura=600, tamanho_ponto=10.0)
  
  # Exemplo 3: Imagem com 1.265.600 particulas
  # tela.Tela(img="img/ex3.jpg", largura=800, altura=600, tamanho_ponto=10.0)

  # Exemplo 4: Tirando foto
  # tela.Tela(largura=800, altura=600, tamanho_ponto=5.0)

  pyglet.app.run()