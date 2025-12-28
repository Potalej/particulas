# particulas

Testes com muitas partículas. A ideia é tirar uma foto, transformar essa foto em partículas e aí ir mexendo elas de alguma forma.

A forma escolhida no momento depende de uma webcam. O vídeo é capturado e através do [Mediapipe](https://github.com/google-ai-edge/mediapipe) há detecção de mãos (uma por vez). Conforme a mão se mexe, as partículas são movidas. 

Para tirar a foto, é só fazer uma saudação vulcano.

## Instalação

Primeiro, instale os requisitos:

```bash
pip install -r requirements.txt
```

Depois, rode o script de configuração. Ele baixa o modelo de detecção de mão e também compila o módulo em Fortran:

```bash
python configurar.py
```
