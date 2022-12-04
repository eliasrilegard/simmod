# 1. Oscillations and Chaos

The lecture on oscillations and chaos (minor correction in text of project 1.5 a):

[Lecture1-1.pdf](Lecture1-1.pdf)

The assignments only (minor correction in text of project 1.5 a):

[Assignments1-1.pdf](Assignments1-1.pdf)

Here is the Python template file for the pendulum: [pendulum_template.py](templates/pendulum_template.py)

**Tip:** For the RK4 integrator you probably want to make a copy of the `Oscillator` state `osc`. In Python you need to use `copy.deepcopy()` for this (and add `import copy` at the top), just using = makes a reference, not a copy.

The double pendulum template has two versions. Please try the numba version. This is precompiled using numba, which we will also use for assignment number 3. This improves performance. You likely need to install numba. If you have trouble getting numba to work, please inform us.

[doublependulum_numba.py](templates/doublependulum_numba.py)

Non-numba version in case numba doesn't work: [doublependulum_template.py](templates/doublependulum_template.py)