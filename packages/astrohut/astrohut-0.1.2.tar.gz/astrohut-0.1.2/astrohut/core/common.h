#define DOUBLE float

DOUBLE min(int n, DOUBLE *values);
DOUBLE max(int n, DOUBLE *values);

int *whereGreater(int n, DOUBLE *data, DOUBLE value);
int *whereLess(int n, DOUBLE *data, DOUBLE value);
int *whereAnd(int n, int *data1, int *data2);
int *indexWhereTrue(int *n, int *data);

void setConstants(DOUBLE mass_unit, DOUBLE g, DOUBLE tau, DOUBLE dt_, DOUBLE epsilon);
void setPrint(const char *prefix, int frames_every);
