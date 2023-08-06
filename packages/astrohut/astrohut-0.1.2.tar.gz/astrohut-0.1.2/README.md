### Barnes - Hut implementation

#### Installation
Development version:
`python setup.py install`

From PyPi:
`pip install astrohut`

#### Compile shared library

`gcc common.c cons.c box2d.c box3d.c -O2 -lm -shared -fPIC -fopenmp -o astrohutc.cpython-34m.so`
