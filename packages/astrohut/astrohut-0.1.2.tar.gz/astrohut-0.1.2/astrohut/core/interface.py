import os
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from ctypes import POINTER, c_char_p, c_int, pointer

from .constants import DOUBLE, LIB
from .structs2d import body2d, node2d
from .structs3d import body3d, node3d
from .core import fromArrayToBodies, fromBodiesToArray, fromNodeToArray, DimensionError

LIB.malloc.restype = ctypes.c_void_p
LIB.calloc.restype = ctypes.c_void_p

LIB.setConstants.argtypes = DOUBLE, DOUBLE, DOUBLE, DOUBLE, DOUBLE

LIB.setPrint.argtypes = c_char_p, c_int

LIB.omp_set_num_threads.argtypes = c_int,

"""
    2d config
"""
LIB.loadFile2d.argtypes = c_char_p, c_char_p, c_int
LIB.loadFile2d.restype = POINTER(body2d)

LIB.initFirstNode2d.argtypes = c_int, POINTER(body2d)
LIB.initFirstNode2d.restype = POINTER(node2d)

LIB.solveInterval2d.argtypes = c_int, POINTER(POINTER(node2d)), POINTER(body2d)
LIB.solveInterval2d.restype = POINTER(body2d)

LIB.solveInstant2d.argtypes = POINTER(POINTER(node2d)), POINTER(body2d)
LIB.solveInstant2d.restype = POINTER(body2d)

"""
    3d config
"""
LIB.loadFile3d.argtypes = c_char_p, c_char_p, c_int
LIB.loadFile3d.restype = POINTER(body3d)

LIB.initFirstNode3d.argtypes = c_int, POINTER(body3d)
LIB.initFirstNode3d.restype = POINTER(node3d)

LIB.solveInterval3d.argtypes = c_int, POINTER(POINTER(node3d)), POINTER(body3d)
LIB.solveInterval3d.restype = POINTER(body3d)

LIB.solveInstant3d.argtypes = POINTER(POINTER(node3d)), POINTER(body3d)
LIB.solveInstant3d.restype = POINTER(body3d)

def __setPrint__(prefix = "", frames_every = 0):
    LIB.setPrint(prefix.encode(), frames_every)

def __setConstants__(mass_unit, G, tau, dt, epsilon):
    LIB.setConstants(mass_unit, G, tau, dt, epsilon)

class Simulation():
    """
    Main class of astrohut. In order to evolve a system and study them a simulation instance
    must be launch.
    """
    def __init__(self, data, dim, mass_unit = 1.0, G = 1.0, tau = 0.5, dt = 1e-4, epsilon = 1e-4,
                read_kwargs = {}):
        self.data = data
        self.dim = dim
        self.mass_unit = mass_unit
        self.G = G
        self.tau = tau
        self.dt = dt
        self.epsilon = epsilon

        if type(self.data) is str:
            self.data = np.genfromtxt(data, **read_kwargs)

        self.Nbodies, self.bodies = fromArrayToBodies(self.data, self.dim)
        self.node = None
        self.results_nodes = None
        self.results_bodies = None
        self.setConstants()
        self.setFilePrefix()

        self.ax = None
        self.fig = None

        self.file_number = 0

        if self.dim == 2:
            self.initFirstNode = LIB.initFirstNode2d
            self.solveInstant = LIB.solveInstant2d
            self.printInstant = LIB.printInstant2d
            self.swapBody = LIB.swapBody2d

        elif self.dim == 3:
            self.initFirstNode = LIB.initFirstNode3d
            self.solveInstant = LIB.solveInstant3d
            self.printInstant = LIB.printInstant3d
            self.swapBody = LIB.swapBody3d

        else:
            raise(DimensionError())

    def setConstants(self):
        """
            Sets the current constants at the C shared library.
        """
        __setConstants__(self.mass_unit, self.G, self.tau, self.dt, self.epsilon)

    def setFilePrefix(self, prefix = ""):
        """
            Sets the file prefix at the C shared library.
        """
        __setPrint__(os.path.join(os.getcwd(), prefix))

    def start(self, Ninstants, threads = 0, save_to_file_every = 0, save_to_array_every = 1, print_progress = False):
        """
            Starts a simulation, evolves the system N Ninstants of time.

            Returns:
                np.ndarray: 3d array of the form (instants, Nbodies, properties).
                        Properties are positions, speeds, accelerations and energy.
                        Non scalar properties are arranged as components.
                np.ndarray: 3d array of the form (instants, Nboxes, (center, box)).
                        For every instant there are Nboxes rows, describing each box.
                        First two or three columns are the coordinates of the center
                        of the box. Next columns describe the corners of the box,
                        first the x components, then y, and finally z if dim is 3.

        """
        if type(self.node) == type(None):
            self.node = self.initFirstNode(self.Nbodies, self.bodies)

        if threads > 0:
            LIB.omp_set_num_threads(threads)

        Ninstants = int(Ninstants)

        new = self.solveInstant(ctypes.byref(self.node), self.bodies)
        array_number = 0

        if save_to_array_every != 0:
            instant_points = np.zeros((Ninstants//save_to_array_every + 1, self.Nbodies, 3*self.dim + 1))

            if self.dim == 2:
                instant_nodes = np.zeros((Ninstants//save_to_array_every + 1, self.Nbodies, 12))
            else:
                instant_nodes =  np.zeros((Ninstants//save_to_array_every + 1, self.Nbodies, 93))

        for i in range(Ninstants + 1):
            new2 = self.solveInstant(ctypes.byref(self.node), new)

            if save_to_file_every > 0:
                if i%save_to_file_every == 0:
                    self.printInstant(self.node, new, self.file_number)
                    self.file_number += 1
                    if print_progress:
                        print("File %d saved"%self.file_number)

            if save_to_array_every > 0:
                if i%save_to_array_every == 0:
                    instant_points[array_number] = fromBodiesToArray(new, self.Nbodies, self.dim)
                    instant_nodes[array_number] = fromNodeToArray(self.node, self.dim)
                    array_number += 1
                    if print_progress:
                        print("Array %d/%d"%(array_number, Ninstants//save_to_array_every + 1))

            self.swapBody(ctypes.byref(new2), ctypes.byref(new))
            LIB.free(new2)

        if save_to_array_every != 0:
            if type(self.results_bodies) == type(None):
                self.results_bodies = instant_points
            if type(self.results_nodes) == type(None):
                self.results_nodes = instant_nodes
            else:
                self.results_bodies = np.vstack((self.results_bodies, instant_points))
                self.results_nodes = np.vstack((self.results_nodes, instant_nodes))
            return self.results_bodies, self.results_nodes
        else:
            return fromBodiesToArray(new, self.Nbodies, self.dim), fromNodeToArray(self.node)

    def animate2d(self, i, values, points, boxes):
        """
            Method to be used with matplotlib FuncAnimation.
        """
        nboxes = len(boxes)
        npoints = len(points)
        if len(boxes) > 0:
            for j in range(nboxes):
                box = values[i, j, 2:]
                boxes[j].set_data(box[:5], box[5:])

        for j in range(npoints):
            body = values[i, j]
            points[j].set_data(body[0], body[1])

        if nboxes > 0:
            return points, boxes
        else:
            return points,

    def animate3d(self, i, values, points, boxes):
        """
            Method to be used with matplotlib FuncAnimation.
        """
        nboxes = len(boxes)
        npoints = len(points)
        if len(boxes) > 0:
            step = (values.shape[-1] - 3)//3

            for j in range(nboxes):
                box = values[i, j, 3:]
                boxes[j].set_data(box[:step], box[step:2*step])
                boxes[j].set_3d_properties(box[2*step:])

        for j in range(npoints):
            body = values[i, j]
            points[j].set_data(body[0], body[1])
            points[j].set_3d_properties(body[2])

        if nboxes > 0:
            return points, boxes
        else:
            return points,

    def configPlot(self, figsize=(6, 4.5), xlabel = None, ylabel = None, zlabel = None):
        """
            Configures the plot.

            Returns:
                matplotlib.figure: figure containing the main plot.
                matplotlib.axes: axes containing all the dots and boxes frames (if boxed).
        """

        if self.dim == 2:
            self.fig, self.ax = plt.subplots(figsize = figsize)

        elif self.dim == 3:
            self.fig = plt.figure(figsize = figsize)
            self.ax = self.fig.add_subplot(111, projection='3d')

            if zlabel == None:
                self.ax.set_zlabel("$z$")
            else:
                self.ax.set_zlabel(zlabel)

        if xlabel == None:
            self.ax.set_xlabel("$x$")
        else:
            self.ax.set_xlabel(xlabel)

        if ylabel == None:
            self.ax.set_ylabel("$y$")
        else:
            self.ax.set_ylabel(ylabel)

        return self.fig, self.ax

    def makeAnimation(self, boxed = False, color = None, alpha = 0.5):
        """
            Makes an animation of `data`.

            Args:
                boxed (bool): If True draws the boxes frames.

                color (string):If None, multiplecolors are used. If string is passed a monochrome color is used.

                alpha (float): Alpha channel argument.

            Returns:
                matplotlib.animation.FuncAnimation: animation of the data.
        """
        if boxed:
            data_to_use = self.results_nodes
        else:
            data_to_use = self.results_bodies

        if type(data_to_use) == type(None):
            self.start(100)

        data = data_to_use

        Ninstants = data.shape[0]

        if self.ax == None or self.fig == None:
            self.configPlot()

        if self.dim == 2:
            if color == None:
                points = [self.ax.plot([], [], "o", alpha = alpha)[0] for i in range(self.Nbodies)]
            else:
                points = [self.ax.plot([], [], "o", color = color, alpha = alpha)[0] for i in range(self.Nbodies)]
            boxes = []

            if boxed:
                boxes = [self.ax.plot([], [], c = points[i].get_color(), alpha = alpha)[0] for i in range(self.Nbodies)]

            animation = self.animate2d

        elif self.dim == 3:
            if color == None:
                points = [self.ax.plot([], [], [], "o", alpha = alpha)[0] for i in range(self.Nbodies)]
            else:
                points = [self.ax.plot([], [], [], "o", color = color, alpha = alpha)[0] for i in range(self.Nbodies)]
            boxes = []

            if boxed:
                boxes = [self.ax.plot([], [], [], c = points[i].get_color(), alpha = alpha)[0] for i in range(self.Nbodies)]

            min_ = data[:, :, 2].min()
            max_ = data[:, :, 2].max()
            if min_ != max_:
                self.ax.set_zlim(min_, max_)
            animation = self.animate3d

        self.ax.set_xlim(data[:, :, 0].min(), data[:, :, 0].max())
        self.ax.set_ylim(data[:, :, 1].min(), data[:, :, 1].max())

        ani = FuncAnimation(self.fig, animation, frames = Ninstants,
                            interval = 25, fargs=(data, points, boxes))

        return ani

    def getEnergies(self):
        """
            Returns:
                np.ndarray: contains the energy of the system at every saved instant of time.
        """
        if type(self.results_bodies) != type(None):
            return self.results_bodies[:, :, -1].sum(axis=1)
        else:
            raise(Exception("No simulation has been started."))

    def calcRelaxationTime(self):
        """
            Calculates the relaxation time required for the simulation to reach equilibrium.

            Returns:
                float: relaxation time of the system.
        """
        if self.dim == 2:
            r = ((self.data[:, 0] - self.data[:, 0].mean())**2 + \
                (self.data[:, 1] - self.data[:, 1].mean())**2)**0.5

        elif self.dim == 3:
            r = ((self.data[:, 0] - self.data[:, 0].mean())**2 + \
                (self.data[:, 1] - self.data[:, 1].mean())**2 + \
                (self.data[:, 2] - self.data[:, 2].mean())**2)**0.5

        n = self.Nbodies/(r.max() - r.min())**3
        tcr = 1/np.sqrt(self.G*self.mass_unit*n)

        return self.Nbodies/(10*np.log10(self.Nbodies)) * tcr
