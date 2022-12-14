#!/bin/python3

# Python simulation of a simple planar pendulum with real time animation
# BH, OF, MP, AJ, TS 2020-10-20, latest version 2022-10-25.

from matplotlib import animation
from pylab import *

"""
    This script defines all the classes needed to simulate (and animate) a single pendulum.
    Hierarchy (somehow in order of encapsulation):
    - Oscillator: a struct that stores the parameters of an oscillator (harmonic or pendulum)
    - Observable: a struct that stores the oscillator's coordinates and energy values over time
    - BaseSystem: harmonic oscillators and pendolums are distinguished only by the expression of
                    the return force. This base class defines a virtual force method, which is
                    specified by its child classes
                    -> Harmonic: specifies the return force as -k*t (i.e. spring)
                    -> Pendulum: specifies the return force as -k*sin(t)
    - BaseIntegrator: parent class for all time-marching schemes; function integrate performs
                    a numerical integration steps and updates the quantity of the system provided
                    as input; function timestep wraps the numerical scheme itself and it's not
                    directly implemented by BaseIntegrator, you need to implement it in his child
                    classes (names are self-explanatory)
                    -> EulerCromerIntegrator: ...
                    -> VerletIntegrator: ...
                    -> RK4Integrator: ...
    - Simulation: this last class encapsulates the whole simulation procedure; functions are 
                    self-explanatory; you can decide whether to just run the simulation or to
                    run while also producing an animation: the latter option is slower
"""

# Global constants
G = 9.8  # gravitational acceleration

class Oscillator:

    """ Class for a general, simple oscillator """

    def __init__(self, m=1, c=4, t0=0, theta0=0, dtheta0=0, gamma=0):
        self.m = m              # mass of the pendulum bob
        self.c = c              # c = g/L
        self.L = G / c          # string length
        self.t = t0             # the time
        self.theta = theta0     # the position/angle
        self.dtheta = dtheta0   # the velocity
        self.gamma = gamma      # damping

class Observables:

    """ Class for storing observables for an oscillator """

    def __init__(self):
        self.time = []          # list to store time
        self.pos = []           # list to store positions
        self.vel = []           # list to store velocities
        self.energy = []        # list to store energy


class BaseSystem:
    
    def force(self, osc):

        """ Virtual method: implemented by the childc lasses  """

        pass


class Harmonic(BaseSystem):
    def force(self, osc):
        return - osc.m * ( osc.c*osc.theta + osc.gamma*osc.dtheta )


class Pendulum(BaseSystem):
    def force(self, osc):
        return - osc.m * ( osc.c*np.sin(osc.theta) + osc.gamma*osc.dtheta )


class BaseIntegrator:

    def __init__(self, _dt=0.01) :
        self.dt = _dt   # time step

    def integrate(self, simsystem, osc, obs):

        """ Perform a single integration step """
        
        self.timestep(simsystem, osc, obs)

        # Append observables to their lists
        obs.time.append(osc.t)
        obs.pos.append(osc.theta)
        obs.vel.append(osc.dtheta)
        # Function 'isinstance' is used to check if the instance of the system object is 'Harmonic' or 'Pendulum'
        if isinstance(simsystem, Harmonic) :
            # Harmonic oscillator energy
            obs.energy.append(0.5 * osc.m * osc.L ** 2 * osc.dtheta ** 2 + 0.5 * osc.m * G * osc.L * osc.theta ** 2)
        else :
            # Pendulum energy
            # TODO: Append the total energy for the pendulum (use the correct formula!)


    def timestep(self, simsystem, osc, obs):

        """ Virtual method: implemented by the child classes """
        
        pass


# HERE YOU ARE ASKED TO IMPLEMENT THE NUMERICAL TIME-MARCHING SCHEMES:

class EulerCromerIntegrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        accel = simsystem.force(osc) / osc.m
        osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta


class VerletIntegrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        accel = simsystem.force(osc) / osc.m
        osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta


class RK4Integrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        accel = simsystem.force(osc) / osc.m 
        # osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta


# Animation function which integrates a few steps and return a line for the pendulum
def animate(framenr, simsystem, oscillator, obs, integrator, pendulum_line, stepsperframe):
    
    for it in range(stepsperframe):
        integrator.integrate(simsystem, oscillator, obs)

    x = np.array([0, np.sin(oscillator.theta)])
    y = np.array([0, -np.cos(oscillator.theta)])
    pendulum_line.set_data(x, y)
    return pendulum_line,


class Simulation:

    def reset(self, osc=Oscillator()) :
        self.oscillator = osc
        self.obs = Observables()

    def __init__(self, osc=Oscillator()) :
        self.reset(osc)

    # Run without displaying any animation (fast)
    def run(self,
            simsystem,
            integrator,
            tmax=30.,               # final time
            ):

        n = int(tmax / integrator.dt)

        for it in range(n):
            integrator.integrate(simsystem, self.oscillator, self.obs)

    # Run while displaying the animation of a pendulum swinging back and forth (slow-ish)
    # If too slow, try to increase stepsperframe
    def run_animate(self,
            simsystem,
            integrator,
            tmax=30.,               # final time
            stepsperframe=1         # how many integration steps between visualising frames
            ):

        numframes = int(tmax / (stepsperframe * integrator.dt))-2

        # WARNING! If you experience problems visualizing the animation try to comment/uncomment this line
        plt.clf()

        # If you experience problems visualizing the animation try to comment/uncomment this line
        # fig = plt.figure()

        ax = plt.subplot(xlim=(-1.2, 1.2), ylim=(-1.2, 1.2))
        plt.axhline(y=0)  # draw a default hline at y=1 that spans the xrange
        plt.axvline(x=0)  # draw a default vline at x=1 that spans the yrange
        pendulum_line, = ax.plot([], [], lw=5)
        plt.title(title)
        # Call the animator, blit=True means only re-draw parts that have changed
        anim = animation.FuncAnimation(plt.gcf(), animate,  # init_func=init,
                                       fargs=[simsystem,self.oscillator,self.obs,integrator,pendulum_line,stepsperframe],
                                       frames=numframes, interval=25, blit=True, repeat=False)

        # If you experience problems visualizing the animation try to comment/uncomment this line
        # plt.show()

        # If you experience problems visualizing the animation try to comment/uncomment this line
        plt.waitforbuttonpress(10)

    # Plot coordinates and energies (to be called after running)
    def plot_observables(self, title="simulation", ref_E=None):

        plt.clf()
        plt.title(title)
        plt.plot(self.obs.time, self.obs.pos, 'b-', label="Position")
        plt.plot(self.obs.time, self.obs.vel, 'r-', label="Velocity")
        plt.plot(self.obs.time, self.obs.energy, 'g-', label="Energy")
        if ref_E != None :
            plt.plot([self.obs.time[0],self.obs.time[-1]] , [ref_E, ref_E], 'k--', label="Ref.")
        plt.xlabel('time')
        plt.ylabel('observables')
        plt.legend()
        plt.savefig(title + ".pdf")
        plt.show()


# It's good practice to encapsulate the script execution in 
# a function (e.g. for profiling reasons)
def exercise_11() :
    # TODO


"""
    This directive instructs Python to run what comes after ' if __name__ == "__main__" : '
    if the script pendulum_template.py is executed 
    (e.g. by running "python3 pendulum_template.py" in your favourite terminal).
    Otherwise, if pendulum_template.py is imported as a library 
    (e.g. by calling "import pendulum_template as dp" in another Python script),
    the following is ignored.
    In this way you can choose whether to code the solution to the exericises here in this script 
    or to have (a) separate script(s) that include pendulum_template.py as library.
"""
if __name__ == "__main__" :
    exercise_11()
    # exercise_12()
    # ...
