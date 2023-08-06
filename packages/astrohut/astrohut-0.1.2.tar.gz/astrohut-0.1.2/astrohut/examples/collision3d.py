import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

G = 1.0
m = 1.0
N = 50

pos1 = np.zeros((N, 3))
pos2 = np.zeros_like(pos1)

pos1[:, :2] = np.random.normal(size = (N, 2))

pos2[:, :2] = np.random.normal(loc = 3.0, size = (N, 2))
pos2[:, 2] = 5.0

speeds1 = ah.generateSpeeds(pos1, G, m)
speeds2 = ah.generateSpeeds(pos2, G, m)

pos = np.vstack((pos1, pos2))
speeds = np.vstack((speeds1, speeds2))

system = ah.createArray(pos, speeds)

sim = ah.Simulation(system, dim = 3, dt = 1e-3, G = G, mass_unit = m, epsilon = 1e-2)

sim.start(5000, save_to_array_every = 125, print_progress = True)

# if boxes are wanted: boxed = True
ani = sim.makeAnimation()

sim.ax.set_xlim(-3, 5)
sim.ax.set_ylim(-3, 5)

# ani.save("collision3d.gif", writer="imagemagick", dpi = 72, fps = 12)
plt.show()
