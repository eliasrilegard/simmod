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

  def average_around(self, i, j):
    return 0.25 * (self.grid[i + 1][j] + self.grid[i - 1][j] + self.grid[i][j + 1] + self.grid[i][j - 1])

  def init_values(self, init_fn):
    for i in range(1, self.N - 1):
      for j in range(1, self.N - 1):
        self.grid[i][j] = init_fn(i, j)

  def update(self):
    for i in range(1, self.N - 1):
      for j in range(1, self.N - 1):
        self.grid[i][j] = self.average_around(i, j)

  def update_checker(self):
    for parity in range(2):
      for i in range(1, self.N - 1):
        for j in range(1, self.N - 1):
          if (i + j) % 2 == parity:
            self.grid[i][j] = self.average_around(i, j)
    
def e_42a():
  N = 50
  Ns = [i for i in range(N + 1)]

  region = SquareRegion()
  center = region.N // 2
  
  Es = [abs(region.grid[center][center] - 10) / 10]
  
  for i in range(N):
    region.update()
    Es.append(abs(region.grid[center][center] - 10) / 10)
  
  print(f'Iterations required for error < 0.01: {next(i for i,v in enumerate(Es) if v < 0.01)}') # 29

  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xlabel('Number of iterations')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs number of iterations\nCenter point regarded. ∆x = ∆y = {region.d}')
  plt.savefig('../report/img/4_2a_errorvsn_default.pdf')
  plt.show()

def e_42b():
  N = 50
  Ns = [i for i in range(N + 1)]

  region = SquareRegion()
  center = region.N // 2
  
  Es = [abs(region.grid[center][center] - 10) / 10]
  
  for i in range(N):
    region.update_checker()
    Es.append(abs(region.grid[center][center] - 10) / 10)
  
  print(f'Iterations required for error < 0.01: {next(i for i,v in enumerate(Es) if v < 0.01)}') # 29

  plt.figure()
  plt.plot(Ns, Es)
  plt.yscale('log')
  plt.xlabel('Number of iterations')
  plt.ylabel('Relative error')
  plt.title(f'Relative error vs number of iterations\nCenter point regarded. ∆x = ∆y = {region.d}')
  plt.savefig('../report/img/4_2b_errorvsn_checker.pdf')
  plt.show()

if __name__ == '__main__':
  pass
  e_42a()
  e_42b()