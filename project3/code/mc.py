# Use the Metropolis method to calculate:
# <x> = Integral([0, Inf], x * e^-x) / Integral([0, Inf], e^-x)
# Here, P(x) = e^-x
# Use P(x) = 0 for x < 0

import random as rng
import matplotlib.pyplot as plt
import numpy as np

def f(x):
  return x

def P(x):
  if x < 0: return 0
  return np.exp(-x)

def main():
  Ns = [int(10 ** (i / 2)) for i in range(2, 17)]
  delta = 2
  sigmas = []

  for N in Ns:
    print(N)

    fs = []
    f2s = []

    xs = [0]

    for _ in range(N):
      d = (rng.random() * 2 - 1) * delta
      x_i = xs[-1]
      x_j = x_i + d

      w = P(x_j) / P(x_i)
      r = rng.random()

      xs.append(x_j if w > r else x_i) # This syntax is so backwards
    
    f_avg = 0
    f2_avg = 0

    for i in range(N):
      f_avg += f(xs[i])
      f2_avg += f(xs[i]) ** 2

    f_avg *= 1 / N
    f2_avg *= 1 / N

    sigmas.append(np.sqrt((f2_avg - f_avg ** 2) / N))
  
  plt.figure()
  plt.plot(Ns, sigmas)
  plt.xscale('log')
  plt.xlabel('Value of N')
  plt.ylabel('Error size σ/sqrt(N)')
  plt.title('Error size vs size of N')
  plt.show()

  plt.figure()
  plt.plot(Ns, sigmas)
  plt.xscale('log')
  plt.yscale('log')
  plt.xlabel('Value of N')
  plt.ylabel('Error size σ/sqrt(N)')
  plt.title('Error size vs size of N')
  plt.show()

def main2():
  # Try different delta within [0.01, 10]
  delta_steps = 15
  denominator = (delta_steps - 1) / 3
  N0_steps = 5

  N = 1_000_000

  deltas = [10 ** (-2 + i / denominator) for i in range(delta_steps)]
  # deltas = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10] # Rough logarithmic scaling

  N0s = [int(N * i / N0_steps) for i in range(N0_steps)]

  for N0 in N0s:
    fs = []
    f2s = []
    for delta in deltas:
      print(delta)

      xs = [0]

      for _ in range(N):
        d = (rng.random() * 2 - 1) * delta
        
        x_i = xs[-1]
        x_j = x_i + d

        w = P(x_j) / P(x_i)
        r = rng.random()

        if w > r: xs.append(x_j)
        else: xs.append(x_i)

      f_avg = 0
      f2_avg = 0

      for i in range(N0, N):
        f_avg += f(xs[i])
        f2_avg += f(xs[i]) ** 2
      
      f_avg *= 1 / (N - N0) # Important! *Not* division by N, yields sqewed results
      f2_avg *= 1 / (N - N0)
      fs.append(f_avg)

      sigma = np.sqrt(f2_avg - f_avg ** 2) # = 0.000995... for every iteration

    plt.plot(deltas, fs, label = N0)
  plt.xlabel('Delta')
  plt.ylabel('Calculated average')
  plt.title(f'Calculated average <x> with N = {N} for different values of N_0')
  plt.xscale('log')
  plt.legend()
  plt.show()

if __name__ == '__main__': main()