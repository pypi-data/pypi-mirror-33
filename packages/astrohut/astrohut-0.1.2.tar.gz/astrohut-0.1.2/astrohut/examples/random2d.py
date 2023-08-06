import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt

G = 1.0
m = 1.0

pos = np.random.normal(size=(100, 2))

speeds = ah.generateSpeeds(pos, G, m)
system = ah.createArray(pos, speeds)

sim = ah.Simulation(system, dim = 2, dt = 1e-4, G = G, mass_unit = m)

sim.start(1000, save_to_array_every = 25)

# if boxes are wanted: boxed = True, else: boxed = False
ani = sim.makeAnimation(boxed = True)

# ani.save("random2d.gif", writer="imagemagick", dpi = 72, fps = 12)
plt.show()
