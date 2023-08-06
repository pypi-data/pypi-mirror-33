#define DOUBLE float

typedef struct point3d_str
{
    DOUBLE x;
    DOUBLE y;
    DOUBLE z;
} point3d;

typedef struct body3d_str
{
    point3d p;
    point3d v;
    point3d a;

    DOUBLE E;
} body3d;

typedef struct node3d_str
{
    DOUBLE *xs;
    DOUBLE *ys;
    DOUBLE *zs;

    struct node3d_str *subnode1;
    struct node3d_str *subnode2;
    struct node3d_str *subnode3;
    struct node3d_str *subnode4;
    struct node3d_str *subnode5;
    struct node3d_str *subnode6;
    struct node3d_str *subnode7;
    struct node3d_str *subnode8;

    int Nbodies;
    DOUBLE mass;
    DOUBLE width;
    DOUBLE height;
    DOUBLE large;
    point3d cmass;
    point3d center;

} node3d;


// GENERAL PURPOSE
// point3d *randomPos(int Nbodies);
body3d *loadFile3d(const char *name, const char *delim, int N);

// PRINTING
void printNode3d(FILE *file, node3d *node);
void printInstantNode3d(node3d *node, int t);
void printInstantBodies3d(int N, int t, body3d *bodies);
void printInstant3d(node3d *node, body3d *bodies, int t);

// BOXES
node3d *calculateNode3d(node3d *mother_node);
node3d *initFirstNode3d(int Nbodies, body3d *bodies);
node3d *createNode3d(int Nbodies, node3d *node, DOUBLE *xs, DOUBLE *ys, DOUBLE *zs);
node3d *createSubNode3d(int Nbodies, node3d *node, DOUBLE *xs, DOUBLE *ys, DOUBLE *zs, int *pwhere);

// FREEING
void freeNodes3d(node3d *node);

// SWAPPING
void swapBody3d(body3d **b1, body3d **b2);

// FORCES
void resetAcceleration3d(int N, body3d *bodies);
void acceleration3d(node3d *node, body3d *object);
body3d *solveInstant3d(node3d **node, body3d *bodies);
body3d *solveInterval3d(int N, node3d **node, body3d *bodies);
