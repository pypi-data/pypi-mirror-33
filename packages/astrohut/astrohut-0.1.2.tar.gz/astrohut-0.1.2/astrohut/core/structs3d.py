import ctypes
from .constants import DOUBLE

class point3d(ctypes.Structure):
    """
        Defines a point3d structure.
    """
    _fields_ = [('x', DOUBLE),
                ('y', DOUBLE),
                ('z', DOUBLE)]

    def __str__(self):
        return "x = %f, y = %f, z = %f"%(self.x, self.y, self.z)

class body3d(ctypes.Structure):
    """
        Defines a body3d structure.
    """
    _fields_ = [('p', point3d),
                ('v', point3d),
                ('a', point3d),
                ('E', DOUBLE)]

    def __str__(self):
        values = ["%s: %s"%(item, str(getattr(self, item))) for item, _ in self._fields_]
        return "\n".join(values)

    def asList(self):
        return [self.p.x, self.p.y, self.p.z, self.v.x, self.v.y, self.v.z, self.a.x, self.a.y, self.a.z, self.E]

    def asarray(self):
        return np.array(self.asList())

class node3d(ctypes.Structure):
    """
        Defines a node3d structure.
    """
    def __str__(self):
        toprint = ["Nbodies", "mass", "width", "height", "center", "cmass"]
        values = ["%s: %s"%(item, str(getattr(self, item))) for item in toprint]
        return "\n".join(values)

node3d._fields_ = [('xs', ctypes.POINTER(DOUBLE)),
        ('ys', ctypes.POINTER(DOUBLE)),
        ('zs', ctypes.POINTER(DOUBLE)),

        ('subnode1', ctypes.POINTER(node3d)),
        ('subnode2', ctypes.POINTER(node3d)),
        ('subnode3', ctypes.POINTER(node3d)),
        ('subnode4', ctypes.POINTER(node3d)),
        ('subnode5', ctypes.POINTER(node3d)),
        ('subnode6', ctypes.POINTER(node3d)),
        ('subnode7', ctypes.POINTER(node3d)),
        ('subnode8', ctypes.POINTER(node3d)),

        ('Nbodies', ctypes.c_int),
        ('mass', DOUBLE),
        ('width', DOUBLE),
        ('height', DOUBLE),
        ('large', DOUBLE),
        ('cmass', point3d),
        ('center', point3d)]
