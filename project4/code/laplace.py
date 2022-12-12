import matplotlib.pyplot as plt


def print_matrix(matrix):
  print('\n'.join(['\t'.join(['{:.2f}'.format(cell) for cell in row]) for row in matrix]))

def make_2D_array(n):
  array = []
  for i in range(n):
    array.append([])
    for _ in range(n):
      array[i].append(0)
  return array


class SquareRegion:
  # Edge values in clockwise order [N E S W]
  def __init__(self, L = 10, d = 1, edge_values = [10, 10, 10, 10], init_fn = lambda i, j: 10 * 0.9):
    self.d = d
    self.N = int(L / d) + 1
    self.edge_values = edge_values
    self.grid = self.init_edges(make_2D_array(self.N), edge_values)
    self.init_values(init_fn)

  @staticmethod
  def init_edges(matrix, values):
    n = len(matrix) - 1
    for i in range(1, n):
      matrix[0][i] = values[0]
      matrix[i][n] = values[1]
      matrix[n][i] = values[2]
      matrix[i][0] = values[3]
    return matrix

  @staticmethod
  def average_around(matrix, i, j):
    return 0.25 * (matrix[i + 1][j] + matrix[i - 1][j] + matrix[i][j + 1] + matrix[i][j - 1])

  def init_values(self, init_fn):
    for i in range(1, self.N - 1):
      for j in range(1, self.N - 1):
        self.grid[i][j] = init_fn(i, j)

  def update(self):
    grid_new = self.init_edges(make_2D_array(self.N), self.edge_values)

    for i in range(1, self.N - 1):
      for j in range(1, self.N - 1):
        grid_new[i][j] = self.average_around(self.grid, i, j)
    
    self.grid = grid_new


def e_41a_1():
  L = 10
  N = 100
  Ns = [i for i in range(N + 1)]

  region = SquareRegion(L = L)
  center = region.N // 2
  
  Es = [abs(region.grid[center][center] - 10) / 10]
  
  for i in range(N):
    region.update()
    Es.append(abs(region.grid[center][center] - 10) / 10)
  
  print(f'Iterations required for error < 0.01: {next(i for i,v in enumerate(Es) if v < 0.01)}') # 56

  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xlabel('Number of iterations')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs number of iterations\nCenter point regarded. ∆x = ∆y = {region.d}')
  plt.savefig('../report/img/4_1a_errorvsn_default.pdf')
  plt.show()

def e_41a_2():
  L = 10
  N = 410
  Ns = [i for i in range(N + 1)]

  region = SquareRegion(L = L, d = 0.5)
  center = region.N // 2

  Es = [abs(region.grid[center][center] - 10) / 10]
  
  for i in range(N):
    region.update()
    Es.append(abs(region.grid[center][center] - 10) / 10)
  
  print(f'Iterations required for error < 0.01: {next(i for i,v in enumerate(Es) if v < 0.01)}') # 225

  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xlabel('Number of iterations')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs number of iterations\nCenter point regarded. ∆x = ∆y = {region.d}')
  plt.savefig('../report/img/4_1a_errorvsn_smallerd.pdf')
  plt.show()

def e_41b():
  L = 10
  N = 140
  Ns = [i for i in range(N + 1)]

  region = SquareRegion(L = L, init_fn = lambda i, j: 4 if i == j == 5 else 0)
  center = region.N // 2

  Es = [abs(region.grid[center][center] - 10) / 10]
  
  for i in range(N):
    region.update()
    Es.append(abs(region.grid[center][center] - 10) / 10)

  print(f'Iterations required for error < 0.01: {next(i for i,v in enumerate(Es) if v < 0.01)}') # 102

  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xlabel('Number of iterations')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs number of iterations\nCenter point regarded. ∆x = ∆y = {region.d}')
  plt.savefig('../report/img/4_1b_errorvsn.pdf')
  plt.show() 

def e_41c_1():
  d = 0.1
  L = 10
  N = 150
  Ns = [i for i in range(N + 1)]

  reference = SquareRegion(L = L, d = d, edge_values = [10, 5, 10, 5], init_fn = lambda i, j: 7.5)
  for i in range(1000):
    reference.update()

  region = SquareRegion(L = L, d = d, edge_values = [10, 5, 10, 5], init_fn = lambda i, j: 7.5)

  major_change = True
  count = 0
  while major_change:
    region.update()
    count += 1

    major_change = False
    for i in range(1, region.N - 1):
      for j in range(1, region.N - 1):
        if abs(region.grid[i][j] - reference.grid[i][j]) / reference.grid[i][j] > 0.01:
          major_change = True

  xs = ys = [i * L / (region.N - 1) for i in range(region.N)]
  prepared = [[cell - 7.5 for cell in row] for row in region.grid]
  prepared[0][0] = prepared[0][region.N - 1] = prepared[region.N - 1][0] = prepared[region.N - 1][region.N - 1] = 0
  
  plt.figure().add_subplot().set_aspect('equal')
  plt.contour(xs, ys, prepared, 15, cmap = 'winter')
  plt.xlabel('V = 10')
  plt.ylabel('V = 5')
  plt.title('Equipotential surfaces for [10, 5, 10, 5]')
  # plt.savefig('../report/img/4_1c_equipotential_510510.pdf')
  plt.show()

def e_41c_2():
  d = 0.1
  L = 10
  N = 150
  edges = [10, 10, 0, 10]
  Ns = [i for i in range(N + 1)]

  reference = SquareRegion(L = L, d = d, edge_values = edges, init_fn = lambda i, j: 7.5)
  for i in range(1000):
    reference.update()

  region = SquareRegion(L = L, d = d, edge_values = edges, init_fn = lambda i, j: 7.5)

  major_change = True
  count = 0
  while major_change:
    region.update()
    count += 1

    major_change = False
    for i in range(1, region.N - 1):
      for j in range(1, region.N - 1):
        if abs(region.grid[i][j] - reference.grid[i][j]) / reference.grid[i][j] > 0.01:
          major_change = True

  # print_matrix(region.grid)

  xs = ys = [i * L / (region.N - 1) for i in range(region.N)]
  prepared = [[cell - 7.5 for cell in row] for row in region.grid]
  prepared[0][0] = prepared[0][region.N - 1] = prepared[region.N - 1][0] = prepared[region.N - 1][region.N - 1] = 0
  
  plt.figure().add_subplot().set_aspect('equal')
  plt.contour(xs, ys, prepared, 15, cmap = 'winter')
  plt.xlabel('V = 10 here, V = 0 at the top')
  plt.ylabel('V = 10')
  plt.title('Equipotential surfaces for [0, 10, 10, 10]')
  # plt.savefig('../report/img/4_1c_equipotential_1010010.pdf')
  plt.show()

if __name__ == '__main__':
  pass
  # e_41a_1()
  # e_41a_2()
  # e_41b()
  # e_41c_1()
  # e_41c_2()