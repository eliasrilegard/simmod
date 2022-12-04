#!/bin/python3

# Python simulation of a simple planar pendulum with real time animation
# BH, OF, MP, AJ, TS 2020-10-20, latest version 2022-10-25.

from matplotlib import animation
from pylab import *
import copy

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
G = 9.8  # Gravitational acceleration

class Oscillator:

    """ Class for a general, simple oscillator """

    def __init__(self, m=1, c=4, t0=0, theta0=0, dtheta0=0, gamma=0):
        self.m = m              # Mass of the pendulum bob
        self.c = c              # c = g/L
        self.L = G / c          # String length
        self.t = t0             # The time
        self.theta = theta0     # The position/angle
        self.dtheta = dtheta0   # The velocity
        self.gamma = gamma      # Damping

class Observables:

    """ Class for storing observables for an oscillator """

    def __init__(self):
        self.time = []          # List to store time
        self.pos = []           # List to store positions
        self.vel = []           # List to store velocities
        self.energy = []        # List to store energy


class BaseSystem:
    
    def force(self, osc):

        """ Virtual method: implemented by the child classes """

        pass


class Harmonic(BaseSystem):
    def force(self, osc):
        return - osc.m * (osc.c * osc.theta + osc.gamma * osc.dtheta)


class Pendulum(BaseSystem):
    def force(self, osc):
        return - osc.m * (osc.c * np.sin(osc.theta) + osc.gamma * osc.dtheta)


class BaseIntegrator:

    def __init__(self, _dt=0.2):
        self.dt = _dt   # Time step

    def integrate(self, simsystem, osc, obs):

        """ Perform a single integration step """
        
        self.timestep(simsystem, osc, obs)

        # Append observables to their lists
        obs.time.append(osc.t)
        obs.pos.append(osc.theta)
        obs.vel.append(osc.dtheta)
        # Function 'isinstance' is used to check if the instance of the system object is 'Harmonic' or 'Pendulum'
        if isinstance(simsystem, Harmonic):
            # Harmonic oscillator energy
            obs.energy.append(0.5 * osc.m * osc.L ** 2 * osc.dtheta ** 2 + 0.5 * osc.m * G * osc.L * osc.theta ** 2)
        else :
            # Pendulum energy
            # TODO: Append the total energy for the pendulum (use the correct formula!)
            obs.energy.append(0.5 * osc.m * osc.L ** 2 * osc.dtheta ** 2 + osc.m * G * osc.L * (1 - np.cos(osc.theta)))


    def timestep(self, simsystem, osc, obs):

        """ Virtual method: implemented by the child classes """
        
        pass


# HERE YOU ARE ASKED TO IMPLEMENT THE NUMERICAL TIME-MARCHING SCHEMES:

class EulerCromerIntegrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        accel = simsystem.force(osc) / osc.m
        osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta
        osc.dtheta -= G / osc.L * osc.theta * self.dt
        osc.theta += osc.dtheta * self.dt


class VerletIntegrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        accel = simsystem.force(osc) / osc.m
        osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta
        osc.theta += osc.dtheta * self.dt + 0.5 * accel * self.dt ** 2
        # Gamma = 0 => osc.gamma * osc.dtheta = 0 in Pendulum.force()
        accel_future = simsystem.force(osc) / osc.m
        osc.dtheta += 0.5 * (accel_future + accel) * self.dt


class RK4Integrator(BaseIntegrator):
    def timestep(self, simsystem, osc, obs):
        # accel = simsystem.force(osc) / osc.m

        # Get the acceleration of the system at the current state
        def accel():
            return simsystem.force(osc) / osc.m 
        
        # osc.t += self.dt
        # TODO: Implement the integration here, updating osc.theta and osc.dtheta
        
        # Save current state
        x = osc.theta
        v = osc.dtheta
        t = osc.t

        a1 = accel() * self.dt
        b1 = v * self.dt

        # First advance
        osc.theta = x + b1 / 2
        osc.dtheta = v + a1 / 2
        osc.t = t + self.dt / 2

        a2 = accel() * self.dt
        b2 = (v + a1 / 2) * self.dt

        # Second advance
        osc.theta = x + b2 / 2
        osc.dtheta = v + a2 / 2

        a3 = accel() * self.dt
        b3 = (v + a2 / 2) * self.dt

        # Final advance
        osc.theta = x + b3
        osc.dtheta = v + a3
        osc.t = t + self.dt # Final value

        a4 = accel() * self.dt
        b4 = (v + a3) * self.dt

        # Write final values
        osc.dtheta = v + (a1 + 2 * a2 + 2 * a3 + a4) / 6
        osc.theta = x + (b1 + 2 * b2 + 2 * b3 + b4) / 6


# Animation function which integrates a few steps and return a line for the pendulum
def animate(framenr, simsystem, oscillator, obs, integrator, pendulum_line, stepsperframe):
    
    for it in range(stepsperframe):
        integrator.integrate(simsystem, oscillator, obs)

    x = np.array([0, np.sin(oscillator.theta)])
    y = np.array([0, -np.cos(oscillator.theta)])
    pendulum_line.set_data(x, y)
    return pendulum_line,


class Simulation:

    def reset(self):
        self.oscillator = Oscillator()
        self.obs = Observables()

    def __init__(self):
        self.reset()

    # Run without displaying any animation (fast)
    def run(
            self,
            simsystem,
            integrator,
            tmax=30.,               # Final time
        ):

        n = int(tmax / integrator.dt)

        for it in range(n):
            integrator.integrate(simsystem, self.oscillator, self.obs)

    # Run while displaying the animation of a pendulum swinging back and forth (slow-ish)
    # If too slow, try to increase stepsperframe
    def run_animate(
            self,
            simsystem,
            integrator,
            tmax=30.,               # Final time
            stepsperframe=1         # How many integration steps between visualising frames
        ):

        numframes = int(tmax / (stepsperframe * integrator.dt)) - 2

        # WARNING! If you experience problems visualizing the animation try to comment/uncomment this line
        plt.clf()

        # If you experience problems visualizing the animation try to comment/uncomment this line
        # fig = plt.figure()

        ax = plt.subplot(xlim=(-1.2, 1.2), ylim=(-1.2, 1.2))
        plt.axhline(y=0)  # Draw a default hline at y=1 that spans the xrange
        plt.axvline(x=0)  # Draw a default vline at x=1 that spans the yrange
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
        # plt.title(title)
        plt.title("Verlet over long time period")
        plt.plot(self.obs.time, self.obs.pos, 'b-', label="Position")
        plt.plot(self.obs.time, self.obs.vel, 'r-', label="Velocity")
        plt.plot(self.obs.time, self.obs.energy, 'g-', label="Energy")
        if ref_E != None:
            plt.plot([self.obs.time[0], self.obs.time[-1]], [ref_E, ref_E], 'k--', label="Ref.")
        plt.xlabel('time')
        plt.ylabel('observables')
        plt.legend()
        plt.savefig(title + ".pdf")
        plt.show()


# It's good practice to encapsulate the script execution in a function (e.g. for profiling reasons)
def exercise_11():
    # m=1, c=4, t0=0, theta0=0, dtheta0=0, gamma=0
    sim = Simulation()
    sim.oscillator.theta = np.pi * 0.5

    system = Pendulum()

    # integrator = EulerCromerIntegrator()
    integrator = VerletIntegrator()
    # integrator = RK4Integrator()
    
    sim.run(system, integrator, 300)
    sim.plot_observables()

def exercise_12():
    times_harmonic = []
    times_pendulum = []
    start_angles = []
    perturbations = []

    steps = 30
    for i in range(1, steps):
        start_angle = np.pi * i / steps
        start_angles.append(start_angle)

        sim_pendulum = Simulation()
        sim_pendulum.oscillator.theta = start_angle

        sim_harmonic = Simulation()
        sim_harmonic.oscillator.theta = start_angle

        system_harmonic = Harmonic()
        system_pendulum = Pendulum()

        integrator = VerletIntegrator()

        sim_pendulum.run(system_pendulum, integrator)
        sim_harmonic.run(system_harmonic, integrator)

        indices = []
        for j in range(len(sim_pendulum.obs.vel) - 1):
            if (sim_pendulum.obs.vel[j] * sim_pendulum.obs.vel[j + 1] < 0):
                indices.append(j)
        T = sim_pendulum.obs.time[indices[3]] - sim_pendulum.obs.time[indices[1]]
        times_pendulum.append(T)

        indices = []
        for j in range(len(sim_harmonic.obs.vel) - 1):
            if (sim_harmonic.obs.vel[j] * sim_harmonic.obs.vel[j + 1] < 0):
                indices.append(j)
        T = sim_harmonic.obs.time[indices[3]] - sim_harmonic.obs.time[indices[1]]
        times_harmonic.append(T)

        # More terms on this will make it more accurate
        perturbation_time = np.pi * (1 + start_angle ** 2 / 16 + 11 * start_angle ** 4 / 3072 + 173 * start_angle ** 6 / 737280)
        perturbations.append(perturbation_time)

    plt.clf()
    plt.title("Period time vs Starting angle")
    plt.plot(start_angles, times_pendulum, "b-", label = "Pendulum period time")
    plt.plot(start_angles, perturbations, "r-", label = "Perturbation time (pendulum)")
    plt.plot(start_angles, times_harmonic, "g-", label = "Harmonic osc. period time")
    plt.xlabel("Starting angle (radians)")
    plt.ylabel("Period time")
    plt.legend()
    plt.show()

def exercise_13_1():
    sim = Simulation()
    sim.oscillator.theta = 1
    sim.oscillator.gamma = 3
    
    system = Harmonic()
    integrator = VerletIntegrator()

    sim.run(system, integrator)
    sim.plot_observables()


def exercise_13_2():
    for x in range(5, 51):
        gamma = x / 10

        sim = Simulation()
        sim.oscillator.theta = 1
        sim.oscillator.gamma = gamma

        system = Harmonic()
        integrator = VerletIntegrator()

        sim.run(system, integrator)

        passing = True
        for pos in sim.obs.pos:
            if pos < 0:
                passing = False
        if passing:
            print(gamma)

def exercise_13_3():
    taus = []
    gammas = []

    for x in range(1, 51):
        gamma = x / 10
        gammas.append(gamma)

        sim = Simulation()
        sim.oscillator.theta = 1
        sim.oscillator.gamma = gamma

        system = Harmonic()

        integrator = VerletIntegrator()

        sim.run(system, integrator)

        vel_zeros = []
        for i in range(0, len(sim.obs.vel)):
            if (abs(sim.obs.vel[i]) < 0.01):
                vel_zeros.append(i)
        tau = 0
        time = 0

        for extreme_point in vel_zeros:
            if (abs(sim.obs.pos[extreme_point]) < 0.37 and tau == 0):
                tau = integrator.dt * extreme_point

        taus.append(tau)

    # Hack kan bero på att tau blir någonstans mellan topparna som jag letar efter
    plt.clf()
    plt.title("Tau vs damping (gamma)")
    plt.plot(gammas, taus, label = "Tau")
    plt.xlabel("Gamma")
    plt.ylabel("Tau")
    plt.legend()
    plt.show()

def exercise_14():
    sim = Simulation()
    sim.oscillator.gamma = 1
    sim.oscillator.theta = np.pi / 2

    system = Pendulum()
    integrator = VerletIntegrator()

    sim.run(system, integrator)

    plt.clf()
    plt.plot(sim.obs.pos, sim.obs.vel)
    plt.title("Phase portrait")
    plt.xlabel("Theta")
    plt.ylabel("DTheta")
    plt.show()

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
    # exercise_13_1()
    # exercise_13_2()
    # exercise_13_3()
    # exercise_14()
