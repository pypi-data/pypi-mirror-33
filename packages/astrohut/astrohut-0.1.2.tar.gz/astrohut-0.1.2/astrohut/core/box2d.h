#define DOUBLE float

typedef struct point2d_str
{
    DOUBLE x;
    DOUBLE y;
} point2d;

typedef struct body2d_str
{
    point2d p;
    point2d v;
    point2d a;

    DOUBLE E;
} body2d;

typedef struct node2d_str
{
    DOUBLE *xs;
    DOUBLE *ys;

    struct node2d_str *subnode1;
    struct node2d_str *subnode2;
    struct node2d_str *subnode3;
    struct node2d_str *subnode4;

    int Nbodies;
    DOUBLE mass;
    DOUBLE width;
    DOUBLE height;
    point2d cmass;
    point2d center;

} node2d;


// GENERAL PURPOSE
// point2d *randomPos(int Nbodies);
body2d *loadFile2d(const char *name, const char *delim, int N);

// PRINTING
void printNode2d(FILE *file, node2d *node);
void printInstantNode2d(node2d *node, int t);
void printInstantBodies2d(int N, int t, body2d *bodies);
void printInstant2d(node2d *node, body2d *bodies, int t);

// BOXES
node2d *calculateNode2d(node2d *mother_node);
node2d *initFirstNode2d(int Nbodies, body2d *bodies);
node2d *createNode2d(int Nbodies, node2d *node, DOUBLE *xs, DOUBLE *ys);
node2d *createSubNode2d(int Nbodies, node2d *node, DOUBLE *xs, DOUBLE *ys, int *pwhere);

// FREEING
void freeNodes2d(node2d *node);

// SWAPPING
void swapBody2d(body2d **b1, body2d **b2);

// FORCES
void resetAcceleration2d(int N, body2d *bodies);
void acceleration2d(node2d *node, body2d *object);
body2d *solveInstant2d(node2d **node, body2d *bodies);
body2d *solveInterval2d(int N, node2d **node, body2d *bodies);
