#!/bin/python3

# Template for traffic simulation
# BH, MP 2021-11-15, latest version 2022-11-1.

"""
  This template is used as backbone for the traffic simulations.
  Its structure resembles the one of the pendulum project, that is you have:
  (a) a class containing the state of the system and it's parameters
  (b) a class storing the observables that you want then to plot
  (c) a class that propagates the state in time (which in this case is discrete), and
  (d) a class that encapsulates the aforementioned ones and performs the actual simulation
  You are asked to implement the propagation rule(s) corresponding to the traffic model(s) of the project.
"""

import math
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy.random as rng
import numpy as np

import matplotlib


class Cars:
  """ Class for the state of a number of cars """

  def __init__(self, numCars=5, roadLength=50, v0=1):
    self.numCars    = numCars
    self.roadLength = roadLength
    self.t  = 0
    self.x  = []
    self.v  = []
    self.c  = []
    for i in range(numCars):
      self.x.append(i)        # the position of the cars on the road
      self.v.append(v0)       # the speed of the cars
      self.c.append(i)        # the color of the cars (for drawing)

  # def distance(self, i):
  #   # TODO: Implement the function returning the PERIODIC distance 
  #   # between car i and the one in front
  #   return (self.x[(i + 1) % self.numCars] - self.x[i] + self.roadLength) % self.roadLength
  
  # def distance(self, i):
  #   if (self.x[i] < self.x[(i + 1) % self.numCars]): dist = abs(self.x[i] - self.x[(i + 1) % self.numCars])
  #   else: dist = self.roadLength - abs(self.x[i] - self.x[(i + 1) % self.numCars])
  #   return dist

  def distance(self, i):
    # Cred till Joel
    if i < self.numCars - 1:
      if self.x[i] < self.x[i + 1]:
        dist = abs(self.x[i] - self.x[i + 1])
      else:
        dist = self.roadLength - abs(self.x[i] - self.x[i + 1])
    else:
      if self.x[i] < self.x[0]:
        dist = abs(self.x[i] - self.x[0])
      else:
        dist = self.roadLength - abs(self.x[i] - self.x[0])
    return dist

class Observables:
  """ Class for storing observables """

  def __init__(self):
    self.time = []          # list to store time
    self.flowrate = []      # list to store the flow rate
        

class BasePropagator:
  def __init__(self):
    return
        
  def propagate(self, cars, obs):
    """ Perform a single integration step """
      
    fr = self.timestep(cars, obs)

    # Append observables to their lists
    obs.time.append(cars.t)
    obs.flowrate.append(fr)  # CHANGE!
              
  def timestep(self, cars, obs):
    """ Virtual method: implemented by the child classes """
    pass
      
        
class ConstantPropagator(BasePropagator) :
  """ Cars do not interact: each position is just updated using the corresponding velocity """
    
  def timestep(self, cars, obs):
    for i in range(cars.numCars):
      cars.x[i] += cars.v[i]
    cars.t += 1
    return 0

# TODO
# HERE YOU SHOULD IMPLEMENT THE DIFFERENT CAR BEHAVIOR RULES
# Define you own class which inherits from BasePropagator (e.g. MyPropagator(BasePropagator))
# and implement timestep according to the rule described in the project

class MyPropagator(BasePropagator):
  def __init__(self, vmax, p):
    BasePropagator.__init__(self)
    self.vmax = vmax
    self.p = p

  def timestep(self, cars, obs):
    # TODO Here you should implement the car behavior rules

    for i in range(cars.numCars):
      if cars.v[i] < self.vmax:
        cars.v[i] += 1
      
      dist = cars.distance(i)
      if cars.v[i] >= dist:
        cars.v[i] = dist - 1
      
      if rng.random() < self.p and cars.v[i] > 0:
        cars.v[i] -= 1
        
    v_sum = 0
    for i in range(cars.numCars):
      cars.x[i] = (cars.x[i] + cars.v[i]) % cars.roadLength

      v_sum += cars.v[i]
    
    cars.t += 1

    return v_sum / cars.roadLength

    # for i in range(cars.numCars):
    #   if cars.v[i] < self.vmax:
    #     cars.v[i] += 1
    
    # for i in range(cars.numCars):
    #   dist = cars.distance(i)
    #   if cars.v[i] >= dist:
    #     cars.v[i] = dist - 1

    # for i in range(cars.numCars):
    #   if rng.random() < self.p and cars.v[i] > 0:
    #     cars.v[i] -= 1

    # for i in range(cars.numCars):
    #   cars.x[i] = (cars.x[i] + cars.v[i]) % cars.roadLength

    # v_sum = 0
    # for i in range(cars.numCars):
    #   v_sum += cars.v[i]

############################################################################################

def draw_cars(cars, cars_drawing):
  """ Used later on to generate the animation """
  theta = []
  r     = []

  for position in cars.x:
    # Convert to radians for plotting  only (do not use radians for the simulation!)
    theta.append(position * 2 * math.pi / cars.roadLength)
    r.append(1)

  return cars_drawing.scatter(theta, r, c=cars.c, cmap='hsv')


def animate(framenr, cars, obs, propagator, road_drawing, stepsperframe):
  """ Animation function which integrates a few steps and return a drawing """

  for it in range(stepsperframe):
    propagator.propagate(cars, obs)

  return draw_cars(cars, road_drawing),


class Simulation:
  def reset(self, cars=Cars()) :
    self.cars = cars
    self.obs = Observables()

  def __init__(self, cars=Cars()) :
    self.reset(cars)

  def plot_observables(self, title="simulation"):
    plt.clf()
    plt.title(title)
    plt.plot(self.obs.time, self.obs.flowrate)
    plt.xlabel('time')
    plt.ylabel('flow rate')
    plt.savefig(title + ".pdf")
    plt.show()

  # Run without displaying any animation (fast)
  def run(
    self,
    propagator,
    numsteps=200,           # final time
    title="simulation",     # Name of output file and title shown at the top
    ):

    for it in range(numsteps):
      propagator.propagate(self.cars, self.obs)

    # self.plot_observables(title)

  # Run while displaying the animation of bunch of cars going in circe (slow-ish)
  def run_animate(
    self,
    propagator,
    numsteps=200,           # Final time
    stepsperframe=1,        # How many integration steps between visualising frames
    title="simulation",     # Name of output file and title shown at the top
    ):

    numframes = int(numsteps / stepsperframe)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')
    ax.axis('off')
    # Call the animator, blit=False means re-draw everything
    anim = animation.FuncAnimation(plt.gcf(), animate,  # init_func=init,
                                    fargs=[self.cars,self.obs,propagator,ax,stepsperframe],
                                    frames=numframes, interval=50, blit=True, repeat=False)
    plt.show()

    # If you experience problems visualizing the animation and/or
    # the following figures comment out the next line 
    # plt.waitforbuttonpress(30)

    self.plot_observables(title)

def a(): 
  d_steps = 50
  n_runs = 100
  n_steps = 1000
  
  fr_avgs = []
  densitys = []

  for x in range(1, d_steps + 1):
    density = x / d_steps

    fr_tot = 0

    n_cars = int(density * 50)
    print(density)
    for _ in range(n_runs):
      cars = Cars(numCars = n_cars, roadLength = 50)

      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5), numsteps = n_steps)

      for i in range(int(len(simulation.obs.flowrate) * 0.2), len(simulation.obs.flowrate)):
        fr_tot += simulation.obs.flowrate[i]
    fr_avgs.append(fr_tot / int(n_steps * n_runs * 0.8))
    densitys.append(density)
  
  plt.clf()
  plt.plot(densitys, fr_avgs)
  plt.xlabel('Car density')
  plt.ylabel('Average flow rate')
  plt.title('Flow rate vs density')
  plt.show() # Peak at (0.24, 0.2551)

# R         Avståndet
# <R>       Medelvärde av R
# <R**2>    Medelvärde av R**2
# <R>**2    (Medelvärde av R), i kvadrat
def b1():
  num_steps = 100
  SEE_ = []
  n_runs_ = []
  for n_runs in range(10, 1000 + 1, 10):
  # n_runs = 1000
    print(n_runs)

    fr_tot = 0
    fr2_tot = 0
    for _ in range(n_runs):
      cars = Cars(numCars = 25, roadLength = 50)
      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5), numsteps = num_steps + 20)

      for i in range(20, len(simulation.obs.flowrate)): # Skipping the first 20 steps to get better results
        fr_tot += simulation.obs.flowrate[i]
        fr2_tot += simulation.obs.flowrate[i] ** 2

    fr_avg = fr_tot / (num_steps * n_runs)
    fr2_avg = fr2_tot / (num_steps * n_runs)
    variance = fr2_avg - fr2_avg ** 2
    SEE = np.sqrt(variance / (num_steps * n_runs - 1))
    # if SEE < 0.001: print(n_runs) # 380 is first n_runs where SEE < 0.001
    # Ie, we need to run about 400 simulations to get a StdErrEst of 0.001
    SEE_.append(SEE)
    n_runs_.append(n_runs)
  
  plt.clf()
  plt.plot(n_runs_, SEE_)
  plt.xlabel('Number of runs')
  plt.ylabel('SEE')
  plt.title('Standard error estimate vs Number of runs')
  plt.show()
  
def b2():
  fr_avgs = []
  Ns = []
  for num_steps in range(10, 500 + 1, 10):
    print(num_steps)
    fr_tot = 0
    for _ in range(1000):
      cars = Cars(numCars = 25, roadLength = 50)
      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5), numsteps = num_steps)
      
      for fr in simulation.obs.flowrate:
        fr_tot += fr
    
    fr_avg = fr_tot / (100 * num_steps)
    fr_avgs.append(fr_avg)
    Ns.append(num_steps)
  
  plt.clf()
  plt.plot(Ns, fr_avgs)
  plt.xlabel('Steps in simulation')
  plt.ylabel('Average flow rate')
  plt.title('Flow rate vs numsteps in simulation')
  plt.show()

def d3():
  d_steps = 10
  vmaxs = [i for i in range(1, 11)]
  densitys = [i / d_steps for i in range(1, d_steps + 1)]

  plt.clf()
  for density in densitys:
    fr_avgs = []
    n_cars = int(density * 50)
    for vmax in vmaxs:
      fr_tot = 0
      for _ in range(100):
        cars = Cars(numCars = n_cars, roadLength = 50)
        simulation = Simulation(cars)
        simulation.run(propagator = MyPropagator(vmax = vmax, p = 0.5))
        for i in range(20, len(simulation.obs.flowrate)):
          fr_tot += simulation.obs.flowrate[i]
      fr_avg = fr_tot / (180 * 100)
      fr_avgs.append(fr_avg)
    plt.plot(vmaxs, fr_avgs, label = f'{density}')
  plt.xlabel('vmax')
  plt.ylabel('Average flow rate')
  plt.title('Cross sections of the fundamental diagram at different car densities')
  plt.legend()
  plt.xlim([0, 10])
  plt.show()


def d():
  # Could do someting similar to c in the sense of
  # displaying the fundamental diagram instead of
  # the sampled flow rate
  fr_avgs = []
  vmaxs = []
  for vmax in range(1, 11):
    print(vmax)
    fr_tot = 0
    for _ in range(100):
      cars = Cars(numCars = 25, roadLength = 50)
      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = vmax, p = 0.5))
      
      for i in range(20, len(simulation.obs.flowrate)):
        fr_tot += simulation.obs.flowrate[i]
    fr_avg = fr_tot / (180 * 100)
    fr_avgs.append(fr_avg)
    vmaxs.append(vmax)
  plt.clf()
  plt.plot(vmaxs, fr_avgs)
  plt.xlabel('vmax')
  plt.ylabel('Average flow rate')
  plt.title('Average flow rate vs vmax')
  plt.ylim([0, 0.3])
  plt.show()

def d2(): # Test me
  d_steps = 50
  vmaxs = [i for i in range(1, 11)]
  densitys = [i / d_steps for i in range(1, d_steps + 1)]

  plt.clf()
  for vmax in vmaxs:
    print(vmax)
    fr_avgs = []
    for density in densitys:
      print(density)

      n_cars = int(density * 50)

      fr_tot = 0
      for _ in range(100):
        cars = Cars(numCars = n_cars, roadLength = 50)
        simulation = Simulation(cars)
        simulation.run(propagator = MyPropagator(vmax = vmax, p = 0.5))

        for i in range(20, len(simulation.obs.flowrate)):
          fr_tot += simulation.obs.flowrate[i]
      fr_avg = fr_tot / (180 * 100) # 180 steps * 100 runs
      fr_avgs.append(fr_avg)
    plt.plot(densitys, fr_avgs, label = f'{vmax}')
  plt.xlabel('Car density')
  plt.ylabel('Average flow rate')
  plt.title('Fundamental diagram for different values of vmax')
  plt.legend()
  plt.show()

def e2(): # Test me
  d_steps = 50

  ps = [i/10 for i in range(1, 11)]
  densitys = [i / d_steps for i in range(1, d_steps + 1)]

  plt.clf()
  for p in ps:
    print(p)
    fr_avgs = []
    for density in densitys:

      n_cars = int(density * 50)

      fr_tot = 0
      for _ in range(100):
        cars = Cars(numCars = n_cars, roadLength = 50)
        simulation = Simulation(cars)
        simulation.run(propagator = MyPropagator(vmax = 2, p = p))

        for i in range(20, len(simulation.obs.flowrate)):
          fr_tot += simulation.obs.flowrate[i]
      fr_avg = fr_tot / (180 * 100) # 180 steps * 100 runs
      fr_avgs.append(fr_avg)
    plt.plot(densitys, fr_avgs, label = f'{p}')
  plt.xlabel('Car density')
  plt.ylabel('Average flow rate')
  plt.title('Fundamental diagram for different values of p')
  plt.legend()
  plt.show()

def e3():
  d_steps = 10
  ps = [i / 10 for i in range(1, 11)]
  densitys = [i / d_steps for i in range(1, d_steps + 1)]

  plt.clf()
  for density in densitys:
    fr_avgs = []
    n_cars = int(density * 50)
    for p in ps:
      fr_tot = 0
      for _ in range(100):
        cars = Cars(numCars = n_cars, roadLength = 50)
        simulation = Simulation(cars)
        simulation.run(propagator = MyPropagator(vmax = 2, p = p))
        for i in range(20, len(simulation.obs.flowrate)):
          fr_tot += simulation.obs.flowrate[i]
      fr_avg = fr_tot / (180 * 100)
      fr_avgs.append(fr_avg)
    plt.plot(ps, fr_avgs, label = f'{density}')
  plt.xlabel('p')
  plt.ylabel('Average flow rate')
  plt.title('Cross section of the fundamental diagram at different car densitites')
  plt.legend()
  plt.xlim([0, 1])
  plt.show()

def e():
  fr_avgs = []
  ps = []
  for probability in range(1, 11):
    p = probability / 10
    print(p)
    fr_tot = 0
    for _ in range(100):
      cars = Cars(numCars = 25, roadLength = 50)
      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = 2, p = p))
      
      for i in range(20, len(simulation.obs.flowrate)):
        fr_tot += simulation.obs.flowrate[i]
    fr_avg = fr_tot / (180 * 100)
    fr_avgs.append(fr_avg)
    ps.append(p)

  plt.clf()
  plt.plot(ps, fr_avgs)
  plt.xlabel('p')
  plt.ylabel('Average flow rate')
  plt.title('Average flow rate vs Probability of random breaks')
  # plt.ylim([0, 0.3])
  plt.show()

def c():
  fr_avgs = []
  road_lengths = []
  for road_length in range(10, 200 + 1, 10):

    # Target density 0.5
    num_cars = road_length // 2
    print(f'{road_length} road length, {num_cars} cars')

    fr_tot = 0

    for _ in range(100):
      cars = Cars(numCars = num_cars, roadLength = road_length)
      simulation = Simulation(cars)
      simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5), numsteps = 500)

      for i in range(len(simulation.obs.flowrate) // 5, len(simulation.obs.flowrate)): #range(len(simulation.obs.flowrate)):
        fr_tot += simulation.obs.flowrate[i]

    fr_avg = fr_tot / (10 * 500)
    fr_avgs.append(fr_avg)
    road_lengths.append(road_length)

  plt.clf()
  plt.plot(road_lengths, fr_avgs)
  plt.xlabel('Road length (constant density)')
  plt.ylabel('Average flow rate')
  plt.title('Average flow rate vs Road length at constant density')
  plt.show()

def c2():
  d_steps = 50
  n_runs = 100
  n_steps = 1000
  
  densitys = [i / d_steps for i in range(1, d_steps + 1)]

  plt.clf()

  for road_length in [10, 30, 50, 70, 100, 200, 500]:
    fr_avgs = []

    for density in densitys:
      print(density)

      fr_tot = 0

      n_cars = int(density * road_length)
      for _ in range(n_runs):
        cars = Cars(numCars = n_cars, roadLength = road_length)

        simulation = Simulation(cars)
        simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5), numsteps = n_steps)

        for i in range(int(len(simulation.obs.flowrate) * 0.2), len(simulation.obs.flowrate)):
          fr_tot += simulation.obs.flowrate[i]
      fr_avgs.append(fr_tot / int(n_steps * n_runs * 0.8))
    plt.plot(densitys, fr_avgs, label = f'{road_length}')
  plt.xlabel('Car density')
  plt.ylabel('Average flow rate')
  plt.title('Fundamental diagram for different road lengths')
  plt.legend()
  plt.show()


# It's good practice to encapsulate the script execution in 
# a main() function (e.g. for profiling reasons)
def main():
  # a()
  # b1()
  # b2()
  # c()
  # c2()
  # d()
  # d2()
  # d3()
  # e()
  # e2()
  e3()
  # Here you can define one or more instances of cars, with possibly different parameters, 
  # and pass them to the simulator 

  # Be sure you are passing the correct initial conditions!
  # cars = Cars(numCars = 25, roadLength = 50)

  # Create the simulation object for your cars instance:
  # simulation = Simulation(cars)

  # simulation.run_animate(propagator=ConstantPropagator())
  # simulation.run_animate(propagator=MyPropagator(vmax=2, p=0.2))
  # simulation.run(propagator = MyPropagator(vmax = 2, p = 0.5)) # Average flowrate 0.195905


# Calling 'main()' if the script is executed.
# If the script is instead just imported, main is not called (this can be useful if you want to
# write another script importing and utilizing the functions and classes defined in this one)
if __name__ == "__main__" : main()