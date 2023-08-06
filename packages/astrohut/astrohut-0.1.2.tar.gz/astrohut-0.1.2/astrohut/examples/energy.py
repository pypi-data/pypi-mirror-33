import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt

G = 1.0
m = 1.0

pos = np.random.normal(size=(100, 2))

speeds = ah.generateSpeeds(pos, G, m)
system = ah.createArray(pos, speeds)

sim = ah.Simulation(system, dim = 2, dt = 1e-4, G = G, mass_unit = m)

sim.start(10000, save_to_array_every = 250, print_progress = True)

plt.plot(sim.getEnergies())
plt.xlabel("Saved instants of time")
plt.ylabel("Energy")

# plt.savefig("energy.png")
plt.show()
