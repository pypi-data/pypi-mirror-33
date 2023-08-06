import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

G = 1.0
m = 1.0

pos = np.zeros((25, 3))
pos[:, :2] = np.random.normal(size=(pos.shape[0], 2))
speeds = ah.generateSpeeds(pos, G, m)

system = ah.createArray(pos, speeds)

sim = ah.Simulation(system, dim = 3, dt = 1e-3, G = G, mass_unit = m)

sim.start(1000, save_to_array_every = 25)

# if boxes are wanted: boxed = True, else: boxed = False
ani = sim.makeAnimation(boxed = True)

# ani.save("disk3d.gif", writer="imagemagick", dpi = 72, fps = 12)
plt.show()
