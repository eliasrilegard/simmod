from pylab import *
import random
from enum import Enum

class Direction(Enum):
  UP = 0
  DOWN = 1
  LEFT = 2
  RIGHT = 3
  FRONT = 4
  BACK = 5

  def get_antagonist(direction):
    match direction:
      case Direction.UP:    return Direction.DOWN
      case Direction.DOWN:  return Direction.UP
      case Direction.LEFT:  return Direction.RIGHT
      case Direction.RIGHT: return Direction.LEFT
      case Direction.FRONT: return Direction.BACK
      case Direction.BACK:  return Direction.FRONT

class PyVector:
  def __init__(self, x = 0, y = 0, z = 0):
    self.x = x
    self.y = y
    self.z = z

  def as_tuple(self):
    return (self.x, self.y, self.z)

  # https://math.stackexchange.com/questions/44689/how-to-find-a-random-axis-or-unit-vector-in-3d
  def random_3D(source):
    theta = source.random() * 2 * np.pi
    vz = source.random() * 2 - 1
    vx = np.sqrt(1 - vz * vz) * np.cos(theta)
    vy = np.sqrt(1 - vz * vz) * np.sin(theta)
    return PyVector(vx, vy, vz)

  def random_2D(rng_source):
    theta = rng_source.random() * 2 * np.pi
    vx = np.cos(theta)
    vy = np.sin(theta)
    return PyVector(vx, vy)

class SimpleWalk3D:
  def __init__(
    self,
    source = random,
    step_count = 1
    # history = []
  ):
    self.rng = source
    self.step_count = step_count
    self.position = PyVector()
    # self.history = history
    # self.history.append(self.position.as_tuple())

  def walk_grid(self):
    for _ in range(self.step_count):
      direction = int(self.rng.random() * 6)
      match direction:
        case 0: self.position.x += 1
        case 1: self.position.x -= 1
        case 2: self.position.y += 1
        case 3: self.position.y -= 1
        case 4: self.position.z += 1
        case 5: self.position.z -= 1
        case _: pass
      # self.history.append(self.position.as_tuple())

  def walk_chain(self):
    for _ in range(self.step_count):
      unit_dir = PyVector.random_3D(self.rng)
      self.position.x += unit_dir.x
      self.position.y += unit_dir.y
      self.position.z += unit_dir.z
      # self.history.append(self.position.as_tuple())

  def walk_chain_2d(self):
    for _ in range(self.step_count):
      unit_dir = PyVector.random_2D(self.rng)
      self.position.x += unit_dir.x
      self.position.y += unit_dir.y
      # self.history.append(self.position.as_tuple())

  def walk_grid_2d(self):
    for _ in range(self.step_count):
      direction = int(self.rng.random() * 4)
      match direction:
        case 0: self.position.x += 1
        case 1: self.position.x -= 1
        case 2: self.position.y += 1
        case 3: self.position.y -= 1
        case _: raise ValueError('Unknown direction')
      # self.history.append(self.position.as_tuple())

class SelfAvoiding3D:
  # Sphere radius 0.5, ie we do "sphere packing" of sorts?
  def __init__(
    self,
    source = random,
    step_count = 1,
  ):
    self.rng = source
    self.step_count = step_count
    self.position = PyVector()
    self.hash = { self.position.as_tuple() }
    self.history = [self.position.as_tuple()]

  # I opted to use the slightly improved version here where the walk won't backtrack on itself immediately
  def walk_grid(self):
    direction = Direction(int(self.rng.random() * 6))
    
    match direction:
      case Direction.UP:    self.position.y += 1
      case Direction.DOWN:  self.position.y -= 1
      case Direction.LEFT:  self.position.x -= 1
      case Direction.RIGHT: self.position.x += 1
      case Direction.FRONT: self.position.z += 1
      case Direction.BACK:  self.position.z -= 1
    
    self.hash.add(self.position.as_tuple())
    self.history.append(self.position.as_tuple())

    for _ in range(1, self.step_count):
      backwards = Direction.get_antagonist(direction)
      direction = Direction(int(self.rng.random() * 6))

      while direction == backwards: # Only kicks in if we select the backwards step
        direction = Direction(int(self.rng.random() * 6)) # Reroll

      new_pos = PyVector(self.position.x, self.position.y, self.position.z)

      match direction:
        case Direction.UP:    new_pos.y += 1
        case Direction.DOWN:  new_pos.y -= 1
        case Direction.LEFT:  new_pos.x -= 1
        case Direction.RIGHT: new_pos.x += 1
        case Direction.FRONT: new_pos.z += 1
        case Direction.BACK:  new_pos.z -= 1

      if new_pos.as_tuple() in self.hash: return False

      self.position = new_pos
      self.hash.add(self.position.as_tuple())
      self.history.append(self.position.as_tuple())

    return True

  def walk_chain(self, r = 0.5):
    self.position = PyVector.random_3D(self.rng) # Cheeky way to take a step lol
    self.hash.add(self.position.as_tuple())

    for _ in range(1, self.step_count):
      unit_dir = PyVector.random_3D(self.rng)
      new_pos = PyVector(
        self.position.x + unit_dir.x,
        self.position.y + unit_dir.y,
        self.position.z + unit_dir.z
      )

      for other_pos in self.hash:
        # r^2 = x^2 + y^2 + z^2
        distance_to_squared = (new_pos.x - other_pos[0]) ** 2 + (new_pos.y - other_pos[1]) ** 2 + (new_pos.z - other_pos[2]) ** 2
        if distance_to_squared < 4 * r ** 2: return False
      
      self.position = new_pos
      self.hash.add(self.position.as_tuple())
      # self.history.append(self.position.as_tuple())
    
    return True


def chain_2d():
  steps = 1000
  walk = SimpleWalk3D(step_count = steps)
  walk.walk_chain_2d()

  xs, ys = [], []

  for pos in walk.history:
    xs.append(pos[0])
    ys.append(pos[1])

  plt.figure()
  plt.title(f'Random walk with {steps} unit steps in random directions')
  plt.plot(xs, ys)
  plt.xlabel('x')
  plt.ylabel('y')
  plt.show()

def grid_2d():
  steps = 1000
  walk = SimpleWalk3D(step_count = steps)
  walk.walk_grid_2d()

  xs, ys = [], []

  for pos in walk.history:
    xs.append(pos[0])
    ys.append(pos[1])

  plt.figure()
  plt.title(f'Random walk with {steps} unit steps in cardinal directions')
  plt.plot(xs, ys)
  plt.xlabel('x')
  plt.ylabel('y')
  plt.show()

def grid():
  steps = 1000
  walk = SimpleWalk3D(step_count = steps)
  walk.walk_grid()
  
  xs, ys, zs = [], [], []

  for pos in walk.history:
    xs.append(pos[0])
    ys.append(pos[1])
    zs.append(pos[2])

  ax = plt.figure().add_subplot(projection = '3d')
  ax.plot(xs, ys, zs)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')
  plt.title(f'3D random walk with {steps} unit steps in cardinal directions')
  plt.show()

def chain():
  steps = 1000
  walk = SimpleWalk3D(step_count = steps)
  walk.walk_chain()

  xs, ys, zs = [], [], []

  for pos in walk.history:
    xs.append(pos[0])
    ys.append(pos[1])
    zs.append(pos[2])

  ax = plt.figure().add_subplot(projection = '3d')
  ax.plot(xs, ys, zs)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')
  plt.title(f'3D random walk with {steps} unit steps in random directions')
  plt.show()

def rmsdf():
  count = 1000
  Ns = [i for i in range(10, 1000 + 1, 10)]
  RMSDs = []
  RMSFs = []

  for N in Ns:
    print(N)

    R_tot = 0
    R2_tot = 0

    for _ in range(count):
      walk = SimpleWalk3D(step_count = N)
      walk.walk_chain()

      R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
      R_tot += np.sqrt(R2)
      R2_tot += R2

    R2_avg = R2_tot / count
    R_avg = R_tot / count

    variance = R2_avg - R_avg ** 2

    RMSD = np.sqrt(R2_avg)
    RMSF = np.sqrt(variance * N / (N - 1))

    RMSDs.append(RMSD)
    RMSFs.append(RMSF)
  
  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{count} iterations for every N')
  plt.plot(Ns, RMSDs)
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.show()

  plt.figure()
  plt.title(f'Root Mean Squared Fluctuation\n{count} iterations for every N')
  plt.plot(Ns, RMSFs)
  plt.xlabel('N')
  plt.ylabel('RMSF')
  plt.show()

def fraction_finished():
  n_walks = 10000
  N_max = 100
  Ns = [i for i in range(1, N_max + 1)]
  radii = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05]

  percent_finished_matrix = []

  for radius in radii:
    print(radius)
    percent_finished = []

    for N in Ns:
      print(N)
      count_finished = 0

      for _ in range(n_walks):
        walk = SelfAvoiding3D(step_count = N)
        count_finished += walk.walk_chain(r = radius)
      
      percent_finished.append(count_finished / n_walks * 100)
    percent_finished_matrix.append(percent_finished)

  plt.figure()
  plt.title(f'Finished walks (%)\n{n_walks} walks for every N')
  # plt.plot(Ns, percent_finished)
  for i in range(len(radii)):
    plt.plot(Ns, percent_finished_matrix[i], label = f'Sphere radius {radii[i]}')
  plt.legend()
  plt.xlabel('N')
  plt.ylabel('%')
  plt.xlim([0 - 0.2, N_max + 0.2])
  plt.show()

  plt.figure()
  plt.title(f'Finished walks (%)\n{n_walks} walks for every N')
  # plt.plot(Ns, percent_finished)
  for i in range(len(radii)):
    plt.plot(Ns, percent_finished_matrix[i], label = f'Sphere radius {radii[i]}')
  plt.legend()
  plt.xlabel('N')
  plt.ylabel('%')
  plt.yscale('log')
  plt.xlim([0 - 0.2, N_max + 0.2])
  plt.ylim([10**(-2.6), 10**2.2])
  plt.show()

def rmsd_comparison():
  walks_per_N = 1000
  limit = 75

  Ns = [i for i in range(1, limit + 1)]
  RMSD_matrix = [[], [], [], []]

  print('GRID WALK BEGIN')

  for N in Ns:
    R2_tot = 0
    print(N)

    for _ in range(walks_per_N):
      walk = SimpleWalk3D(step_count = N)
      walk.walk_grid()

      R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
      R2_tot += R2

    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSD_matrix[0].append(RMSD)

  print('CHAIN WALK BEGIN')

  for N in Ns:
    R2_tot = 0
    print(N)

    for _ in range(walks_per_N):
      walk = SimpleWalk3D(step_count = N)
      walk.walk_chain()

      R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
      R2_tot += R2

    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSD_matrix[1].append(RMSD)

  print('GRID SAW BEGIN')

  for N in Ns:
    R2_tot = 0
    print(N)

    success_count = 0
    while success_count < walks_per_N:
      walk = SelfAvoiding3D(step_count = N)
      did_finish = walk.walk_grid()

      if did_finish:
        success_count += 1
        R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
        R2_tot += R2

    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSD_matrix[2].append(RMSD)

  print('CHAIN SAW BEGIN')

  for N in Ns:
    R2_tot = 0
    print(N)

    success_count = 0
    while success_count < walks_per_N:
      walk = SelfAvoiding3D(step_count = N)
      did_finish = walk.walk_chain(r = 0.2)

      if did_finish:
        success_count += 1
        R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
        R2_tot += R2

    R2_avg = R2_tot / walks_per_N
    RMSD = np.sqrt(R2_avg)
    RMSD_matrix[3].append(RMSD)

  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{walks_per_N} iterations for every N')
  plt.plot(Ns, RMSD_matrix[0], label = 'Grid Walk')
  plt.plot(Ns, RMSD_matrix[1], label = 'Chain Walk')
  plt.plot(Ns, RMSD_matrix[2], label = 'Grid Self Avoiding Walk')
  plt.plot(Ns, RMSD_matrix[3], label = 'Chain Self Avoiding Walk')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()

  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\n{walks_per_N} iterations for every N')
  plt.loglog(Ns, RMSD_matrix[0], label = 'Grid Walk')
  plt.loglog(Ns, RMSD_matrix[1], label = 'Chain Walk')
  plt.loglog(Ns, RMSD_matrix[2], label = 'Grid Self Avoiding Walk')
  plt.loglog(Ns, RMSD_matrix[3], label = 'Chain Self Avoiding Walk')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()

def rmsd_comparison_vary_radius():
  walks_per_N = 1000
  limit = 15

  Ns = [i for i in range(1, limit + 1)]
  radii = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01] 
  RMSD_matrix = [[] for _ in range(len(radii))]

  for i, r in enumerate(radii):
    print(f'RADIUS {r} BEGIN')

    for N in Ns:
      R2_tot = 0
      print(N)

      success_count = 0
      while success_count < walks_per_N:
        walk = SelfAvoiding3D(step_count = N)
        did_finish = walk.walk_chain(r = r)

        if did_finish:
          success_count += 1
          R2 = walk.position.x ** 2 + walk.position.y ** 2 + walk.position.z ** 2
          R2_tot += R2

      R2_avg = R2_tot / walks_per_N
      RMSD = np.sqrt(R2_avg)
      RMSD_matrix[i].append(RMSD)

  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\nChain Self Avoiding Walk, {walks_per_N} iterations per N')
  for i in range(len(radii)):
    plt.plot(Ns, RMSD_matrix[i], label = f'Sphere Radius {radii[i]}')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()

  plt.figure()
  plt.title(f'Root Mean Squared end-to-end Distance\nChain Self Avoiding Walk, {walks_per_N} iterations per N')
  for i in range(len(radii)):
    plt.loglog(Ns, RMSD_matrix[i], label = f'Sphere Radius {radii[i]}')
  plt.xlabel('N')
  plt.ylabel('RMSD')
  plt.legend()
  plt.show()


if __name__ == '__main__':
  # grid()
  # chain()
  # chain_2d()
  # grid_2d()
  # rmsdf()
  # fraction_finished()
  # rmsd_comparison()
  rmsd_comparison_vary_radius()

