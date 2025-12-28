import time
from collections import deque

class FPSContador:

  def __init__ (self, window=30):
    self.times = deque(maxlen=window)
    self.ultimo = time.perf_counter()

  def atualizar (self):
    agora = time.perf_counter()
    dt = agora - self.ultimo
    self.ultimo = agora
    self.times.append(dt)
    return 1.0 / (sum(self.times) / len(self.times))