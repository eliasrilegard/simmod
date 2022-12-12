import random as rng
import matplotlib.pyplot as plt
import json

def print_matrix(matrix):
  print('\n'.join(['\t'.join(['{:.2f}'.format(cell) for cell in row]) for row in matrix]))

def make_2D_array(n):
  array = []
  for i in range(n):
    array.append([])
    for _ in range(n):
      array[i].append(0)
  return array

class RandomWalk:
  def __init__(self, x, y, grid_size):
    self.x = x
    self.y = y
    self.grid_size = grid_size

  def walk_to_edge(self):
    reached_edge = False
    while not reached_edge:
      self.take_step()
      reached_edge = 0 in { self.x, self.y } or (self.grid_size - 1) in { self.x, self.y }

  def take_step(self):
    direction = int(rng.random() * 4)
    if   direction == 0: self.x += 1
    elif direction == 1: self.x -= 1
    elif direction == 2: self.y += 1
    elif direction == 3: self.y -= 1

  def get_coords(self):
    return self.x, self.y

class SquareRegion:
  def __init__(self, L = 10, edge_values = [10, 5, 10, 5]):
    self.N = L + 1
    self.grid = self.init_edges(make_2D_array(self.N), edge_values) # 2/3D

  @staticmethod
  def init_edges(matrix, values):
    n = len(matrix) - 1
    for i in range(1, n):
      matrix[0][i] = values[0]
      matrix[i][n] = values[1]
      matrix[n][i] = values[2]
      matrix[i][0] = values[3]
    return matrix

  def sample(self, i, j, n):
    Vs = []
    for _ in range(n):
      walk = RandomWalk(i, j, self.N)
      walk.walk_to_edge()
      dest_i, dest_j = walk.get_coords()
      Vs.append(self.grid[dest_i][dest_j])
    self.grid[i][j] = Vs

def estimate(pos, N, prefix):
  region = SquareRegion()
  region.sample(*pos, N)

  estimations = [region.grid[pos[0]][pos[1]][0]]
  for i in range(1, N):
    estimations.append((estimations[-1] * i + region.grid[pos[0]][pos[1]][i]) / (i + 1))
  
  Ns = [i + 1 for i in range(N)]

  margin = 0.15

  plt.figure()
  plt.plot(Ns, estimations)
  plt.xscale('log')
  plt.ylim([5 - margin, 10 + margin])
  plt.xlabel('Number of walks')
  plt.ylabel('Estimated potential')
  plt.title(f'Estimated potential at x = {pos[0]}, y = {pos[1]}')
  plt.savefig(f'../report/img/{prefix}_V{pos[0]}{pos[1]}.pdf')
  plt.show()

  Es = [abs(v - estimations[-1]) / estimations[-1] for v in estimations]
  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xscale('log')
  plt.ylim([10 ** (-4), 10 ** 0])
  plt.xlabel('Number of walks')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs N walks\nx = {pos[0]}, y = {pos[1]}')
  plt.savefig(f'../report/img/{prefix}_E{pos[0]}{pos[1]}.pdf')
  plt.show()

def e_43a():
  estimate((5, 5), 10_000, '4_3a')

def e_43b():
  estimate((2, 5), 10_000, '4_3b_1')
  estimate((1, 1), 10_000, '4_3b_2')

def e_44a():
  region = SquareRegion()
  N = 100_000

  for i in range(1, region.N - 1):
    for j in range(1, region.N - 1): # -i
      # print(f'{i} {j}')
      destinations = make_2D_array(region.N)
      for n in range(N):
        walk = RandomWalk(i, j, region.N)
        walk.walk_to_edge()
        di, dj = walk.get_coords()
        destinations[di][dj] += 1 / N
      region.grid[i][j] = destinations

  # for i in range(1, region.N - 1 - 1):
  #   for j in range(1, region.N - i - 1):
  #     region.grid[region.N - 1 - i][region.N - 1 - j] = region.grid[i][j]

  with open('G.json', 'w') as file:
    json.dump(region.grid, file)

def process(data):
  n = len(data) - 1
  for i in range(1, n):
    for j in range(1, n):
      V = 0
      mapping = data[i][j]

      V = 0
      for k in range(1, n): # Ignore corners
        V += mapping[0][k] * data[0][k]
        V += mapping[k][n] * data[k][n]
        V += mapping[n][k] * data[n][k]
        V += mapping[k][0] * data[k][0]

      data[i][j] = V

  data[0][0] = data[n][0] = data[0][n] = data[n][n] = 7.5 # Makes visualization better (less range)
  return data

def e_44b_1():
  # No modifications

  data = []
  with open('G.json') as f:
    data = json.load(f)

  data = process(data)

  plt.subplot(111)
  plt.imshow(data, cmap = 'winter')
  plt.colorbar()
  plt.title('Calculated V using Green\'s function\nthrough random walks')
  plt.xlabel('V = 10')
  plt.ylabel('V = 5')
  plt.savefig('../report/img/4_4b_VfromG.pdf')
  plt.show()

def set_20(matrix, *positions):
  for pos in positions:
    matrix[pos[0]][pos[1]] = 20
  return matrix

def e_44b_2():
  data = []
  with open('G.json') as f:
    data = json.load(f)

  # Make modifications here
  data = set_20(data, (0,3), (0,4), (0,5), (0,6), (0,7))

  data = process(data)

  # data[3][5] = 0

  plt.subplot(111)
  plt.imshow(data, cmap = 'winter')
  plt.colorbar()
  plt.title('Calculated V using Green\'s function\nthrough random walks')
  plt.xlabel('V = 10')
  plt.ylabel('V = 5')
  plt.savefig('../report/img/4_4b_1_VfromG.pdf')
  plt.show()

def e_44b_3():
  data = []
  with open('G.json') as f:
    data = json.load(f)

  data = set_20(data, (3,0), (4,0), (5,0), (6,0), (7,0))

  data = process(data)

  # data[5][3] = 0

  plt.subplot(111)
  plt.imshow(data, cmap = 'winter')
  plt.colorbar()
  plt.title('Calculated V using Green\'s function\nthrough random walks')
  plt.xlabel('V = 10')
  plt.ylabel('V = 5')
  plt.savefig('../report/img/4_4b_2_VfromG.pdf')
  plt.show()

def e_44b_x():
  data = []
  with open('G.json') as f:
    data = json.load(f)

  # data = set_20(data, (0,5), (3,0), (2,0), (3,10), (2,10))
  data = set_20(data, (0,5), (0,4), (0,3), (0,6), (0,7))

  data = process(data)

  # data[3][5] = 0

  plt.subplot(111)
  plt.imshow(data, cmap = 'winter')
  plt.colorbar()
  plt.title('Calculated V using Green\'s function\nthrough random walks')
  plt.xlabel('V = 10')
  plt.ylabel('V = 5')
  # plt.savefig('../report/img/4_4b_x_VfromG.pdf')
  plt.show()

def check_G():
  data = []
  with open('G.json') as f:
    data = json.load(f)

  print_matrix(data[5][3])

if __name__ == '__main__':
  pass
  # e_43a()
  # e_43b()
  # e_44a()
  # e_44b_1()
  # e_44b_2()
  # e_44b_3()
  # e_44b_x()
  # check_G()