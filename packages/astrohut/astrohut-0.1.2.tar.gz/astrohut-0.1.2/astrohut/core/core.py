import os
import sys
import ctypes
import numpy as np
from .constants import DOUBLE, LIB
from .structs2d import body2d, node2d, point2d
from .structs3d import body3d, node3d, point3d

class DimensionError(Exception):
    def __init__(self, message = "Possible dimensions are 2 or 3."):
        super(Exception, self).__init__(message)

def fromBodiesToArray(bodies, N, dim = 2):
    array = np.zeros((N, dim*3 + 1))
    for i in range(N):
        array[i] = bodies[i].asList()

    return array

def fromArrayToBodies(array, dim = 2):
    rows, cols = array.shape[:2]
    dim = int(dim)

    if dim == 2:
        body = body2d
        point = point2d

    elif dim == 3:
        body = body3d
        point = point3d

    else:
        raise(DimensionError())

    bodies = LIB.malloc(rows * ctypes.sizeof(body))
    bodies = ctypes.cast(bodies, ctypes.POINTER(body))

    if cols//dim == 3:
        for i in range(rows):
            bodies[i] = body(point(*array[i, :dim]), point(*array[i, dim:dim*2]),
                                point(*array[i, dim*2:]))
    elif cols//dim == 2:
        for i in range(rows):
            bodies[i] = body(point(*array[i, :dim]), point(*array[i, dim:dim*2]))
    else:
        raise(Exception("Input file has wrong data format."))

    return rows, bodies

def internalNode2d(node):
    try:
        if node.contents.Nbodies == 1:
            c1 = point2d()
            c2 = point2d()
            c3 = point2d()
            c4 = point2d()

            c1.x = node.contents.center.x - node.contents.width*0.5
            c1.y = node.contents.center.y + node.contents.height*0.5

            c2.x = node.contents.center.x + node.contents.width*0.5
            c2.y = node.contents.center.y + node.contents.height*0.5

            c3.x = node.contents.center.x + node.contents.width*0.5
            c3.y = node.contents.center.y - node.contents.height*0.5

            c4.x = node.contents.center.x - node.contents.width*0.5
            c4.y = node.contents.center.y - node.contents.height*0.5

            return [node.contents.xs[0], node.contents.ys[0], c1.x, c2.x, c3.x, c4.x, c1.x,
                    c1.y, c2.y, c3.y, c4.y, c1.y]

    except ValueError:
        return None

    else:
        answer = []
        nodes = [node.contents.subnode1, node.contents.subnode2, node.contents.subnode3, node.contents.subnode4]
        for item in nodes:
            ans = internalNode2d(item)
            if ans != None:
                answer += ans

        return answer

def internalNode3d(node):
    try:
        if node.contents.Nbodies == 1:
            c1 = point3d()
            c2 = point3d()
            c3 = point3d()
            c4 = point3d()
            c5 = point3d()
            c6 = point3d()
            c7 = point3d()
            c8 = point3d()

            c1.x = node.contents.center.x - node.contents.width*0.5
            c1.y = node.contents.center.y + node.contents.height*0.5
            c1.z = node.contents.center.z - node.contents.large*0.5

            c2.x = node.contents.center.x + node.contents.width*0.5
            c2.y = node.contents.center.y + node.contents.height*0.5
            c2.z = node.contents.center.z - node.contents.large*0.5

            c3.x = node.contents.center.x + node.contents.width*0.5
            c3.y = node.contents.center.y - node.contents.height*0.5
            c3.z = node.contents.center.z - node.contents.large*0.5

            c4.x = node.contents.center.x - node.contents.width*0.5
            c4.y = node.contents.center.y - node.contents.height*0.5
            c4.z = node.contents.center.z - node.contents.large*0.5

            c5.x = node.contents.center.x - node.contents.width*0.5
            c5.y = node.contents.center.y + node.contents.height*0.5
            c5.z = node.contents.center.z + node.contents.large*0.5

            c6.x = node.contents.center.x + node.contents.width*0.5
            c6.y = node.contents.center.y + node.contents.height*0.5
            c6.z = node.contents.center.z + node.contents.large*0.5

            c7.x = node.contents.center.x + node.contents.width*0.5
            c7.y = node.contents.center.y - node.contents.height*0.5
            c7.z = node.contents.center.z + node.contents.large*0.5

            c8.x = node.contents.center.x - node.contents.width*0.5
            c8.y = node.contents.center.y - node.contents.height*0.5
            c8.z = node.contents.center.z + node.contents.large*0.5

            steps = [c1, c2, c3, c4, c1,
                    c5, c6, c2, c1, c5,
                    c8, c4, c1, c5, c8,
                    c7, c3, c4, c8, c7,
                    c6, c2, c3, c7, c6,
                    c5, c8, c7, c6, c5]

            coor = [c.x for c in steps] + [c.y for c in steps] + [c.z for c in steps]

            return [node.contents.xs[0], node.contents.ys[0], node.contents.zs[0]] + coor

    except ValueError:
        return None

    else:
        answer = []
        nodes = [node.contents.subnode1, node.contents.subnode2, node.contents.subnode3, node.contents.subnode4,
                node.contents.subnode5, node.contents.subnode6, node.contents.subnode7, node.contents.subnode8]
        for item in nodes:
            ans = internalNode3d(item)
            if ans != None:
                answer += ans

        return answer

def fromNodeToArray(node, dim = 2):
    if dim == 2:
        answer = internalNode2d(node)
    elif dim == 3:
        answer = internalNode3d(node)
    else:
        raise(DimensionError())

    answer = np.array(answer).reshape(node.contents.Nbodies, len(answer)//node.contents.Nbodies)

    return answer

def generateSpeeds(positions, G, mass_unit):
    """
        Generates rotation speeds based on positions, G constants and mass_unit value.

        Returns:
            np.ndarray: array like positions.
    """
    N, dim = positions.shape

    xs = positions[:, 0]
    ys = positions[:, 1]

    x0 = xs.mean()
    y0 = ys.mean()

    xs = xs - x0
    ys = ys - y0

    if dim == 3:
        zs = positions[:, 2]
        z0 = zs.mean()
        zs = zs - z0

    speeds = np.zeros_like(positions)

    if dim == 2:
        d = np.sqrt(xs**2 + ys**2)
    elif dim == 3:
        d = np.sqrt(xs**2 + ys**2 + zs **2)

    else:
        raise(DimensionError())

    for i in range(N):
        n = sum(d < d[i])
        mag = 0.9*np.sqrt(G*n*mass_unit/d[i])
        speeds[i, 0] = -ys[i]*mag/d[i]
        speeds[i, 1] = xs[i]*mag/d[i]

    return speeds

def createArray(pos, speeds, acc = None):
    """
        Creates and array containing the whole properties of the system.

        np.ndarray: appends pos, speeds and acc if any.
    """
    N, dim = pos.shape
    array = np.zeros((N, dim*3))

    array[:, :dim] = pos
    array[:, dim:2*dim] = speeds

    if type(acc) != type(None):
        array[:, 2*dim:] = acc

    return array
