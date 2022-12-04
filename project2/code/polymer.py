from pylab import *
import random

class PyVector:
  def __init__(self, x, y):
    self.x = x
    self.y = y

class RandomWalk:
  def __init__(self, steps = 1, source = random):
    self.rng = source
    self.step_count = steps
    self.pos = PyVector(0, 0)
    self.x_history = []
    self.y_history = []

  def do_walk(self):
    for i in range(0, self.step_count):
      direction = int(self.rng.random() * 4)
      if   direction == 0: self.pos.x += 1
      elif direction == 1: self.pos.x -= 1
      elif direction == 2: self.pos.y += 1
      elif direction == 3: self.pos.y -= 1
      self.x_history.append(self.pos.x)
      self.y_history.append(self.pos.y)

class CustomRandom:
  def __init__(self, r_0 = 1, a = 3, c = 4, m = 128):
    self.n = 0
    self.r_0 = r_0
    self.r = self.r_0
    self.a = a
    self.c = c
    self.m = m

  def random(self):
    self.r = (self.a * self.r + self.c) % self.m
    return self.r / self.m

class SelfAvoidingRandomWalk:
  def __init__(self, steps = 1):
    self.step_count = steps
    self.pos = PyVector(0, 0)
    self.pos_history = { (self.pos.x, self.pos.y) }

  def do_walk(self):
    for _ in range (0, self.step_count):
      direction = int(random.random() * 4)
      new_pos = PyVector(self.pos.x, self.pos.y)

      if   direction == 0: new_pos.x += 1
      elif direction == 1: new_pos.x -= 1
      elif direction == 2: new_pos.y += 1
      elif direction == 3: new_pos.y -= 1

      if (new_pos.x, new_pos.y) in self.pos_history:
        return False
      self.pos.x = new_pos.x
      self.pos.y = new_pos.y
      self.pos_history.add((self.pos.x, self.pos.y))
    return True

class ImprovedSelfAvoidingRandomWalk:
  def __init__(self, steps = 1):
    self.step_count = steps
    self.pos = PyVector(0, 0)
    self.last_dir = -1 # N, E, S, W
    self.pos_history = { (self.pos.x, self.pos.y) }

  def do_walk(self):
    first_step_dir = int(random.random() * 4)

    if   first_step_dir == 0: self.pos.y += 1
    elif first_step_dir == 1: self.pos.x += 1
    elif first_step_dir == 2: self.pos.y -= 1
    elif first_step_dir == 3: self.pos.x -= 1

    self.last_dir = first_step_dir

    for _ in range(self.step_count - 1):
      direction = (self.last_dir + int(random.random() * 3) + 3) % 4 # Will never turn right back on itself
      new_pos = PyVector(self.pos.x, self.pos.y)

      if   direction == 0: new_pos.y += 1
      elif direction == 1: new_pos.x += 1
      elif direction == 2: new_pos.y -= 1
      elif direction == 3: new_pos.x -= 1

      if (new_pos.x, new_pos.y) in self.pos_history: return False
      self.pos.x = new_pos.x
      self.pos.y = new_pos.y
      self.pos_history.add((self.pos.x, self.pos.y))
    return True

def plot(x_history, y_history, title, x_label = 'x', y_label = 'y'):
  plt.clf()
  plt.title(title)
  plt.plot(x_history, y_history)
  plt.xlabel(x_label)
  plt.ylabel(y_label)
  plt.show()

def a():
  total_steps = 1000
  walk = RandomWalk(steps = total_steps)
  walk.do_walk()
  
  plot(walk.x_history, walk.y_history, f'Random walk with {total_steps} unit steps in cardinal directions')

def b():
  # Something tells me we want a and c to be coprime to maximize the period
  # rng = CustomRandom()
  # rng = CustomRandom(m = 129)
  # rng = CustomRandom(r_0 = 5, a = 13, c = 17, m = 39) # Filled square
  # rng = CustomRandom(r_0 = 5, a = 13, c = 17, m = 256) # Symmetry
  rng = CustomRandom(
    r_0 = int(random.random() * 1000 - 500),
    a =   int(random.random() * 1500 + 1 - 750),
    c =   int(random.random() * 2000 + 1 - 1000),
    m =   int(random.random() * 20000 + 1 - 10000)
  ) # Try negative values?

  total_steps = 1000
  walk = RandomWalk(steps = total_steps, source = rng)
  walk.do_walk()

  plot(walk.x_history, walk.y_history, f'Pseudo-random walk with {total_steps} unit steps in cardinal directions\nParameters: r0={rng.r_0}, a={rng.a}, c={rng.c}, m={rng.m}')

def c():
  # R         Avståndet
  # <R>       Medelvärde av R
  # <R**2>    Medelvärde av R**2
  # <R>**2    (Medelvärde av R), i kvadrat
  # Sökt: sqrt(<R**2>)
  # RMSF: sqrt((<R**2> - <R>**2) * N / (N + 1))
  count = 1000

  Ns = []
  RMSDs = []
  RMSFs = []
  SEEs = []
  
  for N in range(10, 1000 + 1, 10):
    R_tot = 0
    R2_tot = 0

    for _ in range(count):
      walk = RandomWalk(steps = N)
      walk.do_walk()
      R2 = walk.pos.x ** 2 + walk.pos.y ** 2
      R_tot += np.sqrt(R2)
      R2_tot += R2

    R2_avg = R2_tot / count
    R_avg = R_tot / count

    variance = R2_avg - R_avg ** 2

    RMSD = np.sqrt(R2_avg)
    RMSF = np.sqrt(variance * N / (N - 1))
    # SEE = np.sqrt(variance / (N + 1))
    SEE = RMSF / np.sqrt(N)

    RMSDs.append(RMSD)
    RMSFs.append(RMSF)
    SEEs.append(SEE)

    Ns.append(N)
  
  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{count} iterations for every N')
  plt.plot(Ns, RMSDs)
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.show()

  plt.figure()
  plt.title(f'Root Mean Square Fluctuation\n{count} iterations for every N')
  plt.plot(Ns, RMSFs)
  plt.xlabel('N')
  plt.ylabel('RMSF')
  plt.show()

  plt.figure()
  plt.title(f'Standard Error Estimate\n{count} iterations for every N')
  plt.plot(Ns, SEEs)
  plt.xlabel('N')
  plt.ylabel('SEE')
  plt.show()

def d():
  n_walks = 10000

  percent_finished = []
  percent_finished_better = []
  Ns = []

  for N in range(1, 100+1):
    print(N)
    count_finished = 0
    count_finished_better = 0

    for _ in range(n_walks):
      walk = SelfAvoidingRandomWalk(steps = N)
      did_finish = walk.do_walk()
      count_finished += did_finish

      walk_better = ImprovedSelfAvoidingRandomWalk(steps = N)
      count_finished_better += walk_better.do_walk()
    
    percent_finished.append(count_finished / n_walks * 100)
    percent_finished_better.append(count_finished_better / n_walks * 100)
    Ns.append(N)

  plt.clf()
  plt.title(f'Finished walks (%)\n{n_walks} walks for every N')
  plt.plot(Ns, percent_finished, label='"Dumb" walk')
  plt.plot(Ns, percent_finished_better, label='Improved walk')
  plt.xlabel('N')
  plt.ylabel('%')
  plt.legend()
  # plt.yscale('log')
  # plt.ylim([10**(-2.6), 10**2.2])
  plt.show()

def e():
  walks_per_N = 2500
  limit = 35

  Ns = []
  RMSDs = []
  RMSD2s = []

  for N in range(1, limit + 1): # 30 rather arbitrary but already by then we're down to a .5% chance of success
    R2_tot = 0
    print(N)
    
    success_count = 0
    while success_count < walks_per_N:
      walk = ImprovedSelfAvoidingRandomWalk(steps = N)
      did_finish = walk.do_walk()

      if did_finish:
        success_count += 1
        R2 = walk.pos.x ** 2 + walk.pos.y ** 2
        R2_tot += R2

    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSDs.append(RMSD)
    Ns.append(N)

  for N in range(1, limit + 1):
    R2_tot = 0
    print(N)

    for _ in range(walks_per_N):
      walk = RandomWalk(steps = N)
      walk.do_walk()

      R2 = walk.pos.x ** 2 + walk.pos.y ** 2
      R2_tot += R2
    
    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSD2s.append(RMSD)
  
  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{walks_per_N} iterations for every N')
  plt.plot(Ns, RMSDs, label = '(Improved) SAW')
  plt.plot(Ns, RMSD2s, label = '"Dumb" Walk')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()

  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{walks_per_N} iterations for every N')
  plt.loglog(Ns, RMSDs, label = '(Improved) SAW')
  plt.loglog(Ns, RMSD2s, label = '"Dumb" Walk')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()

def main():
  # a()
  # b()
  c()
  # d()
  # e()

if __name__ == '__main__': main()
