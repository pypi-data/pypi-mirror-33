#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "common.h"
#include "cons.h"

void setConstants(DOUBLE mass_unit, DOUBLE g, DOUBLE tau, DOUBLE dt_, DOUBLE epsilon)
{
    MASS_UNIT = mass_unit;
    G = g;
    TAU = tau;
    dt = dt_;
    EPSILON = epsilon;
}

void setPrint(const char *prefix, int frames_every)
{
    strcpy(FILE_PREFIX, prefix);
    FRAMES_EVERY = frames_every;
}

DOUBLE min(int n, DOUBLE *values)
{
    int i;
    DOUBLE minV = values[0];
    for(i = 1; i < n; i++)
    {
        if(values[i] < minV)
        {
            minV = values[i];
        }
    }
    return minV;
}

DOUBLE max(int n, DOUBLE *values)
{
    int i;
    DOUBLE maxV = values[0];
    for(i = 1; i < n; i++)
    {
        if(values[i] > maxV)
        {
            maxV = values[i];
        }
    }
    return maxV;
}

int *whereGreater(int n, DOUBLE *data, DOUBLE value)
{
    int i;
    int *pos = malloc(n*sizeof(int));
    for(i = 0; i < n; i++)
    {
        if (data[i] >= value)
        {
            pos[i] = 1;
        }
        else
        {
            pos[i] = 0.0;
        }
    }
    return pos;
}

int *whereLess(int n, DOUBLE *data, DOUBLE value)
{
    int i;
    int *pos = malloc(n*sizeof(int));
    for(i = 0; i < n; i++)
    {
        if (data[i] < value)
        {
            pos[i] = 1;
        }
        else
        {
            pos[i] = 0.0;
        }
    }
    return pos;
}

int *whereAnd(int n, int *data1, int *data2)
{
    int i, *pos = malloc(n*sizeof(int));
    for(i = 0; i < n; i++)
    {
        pos[i] = data1[i] * data2[i];
    }
    return pos;
}

int *indexWhereTrue(int *n, int *data)
{
    int i, j = 0, *pos = malloc(*n*sizeof(int));
    for(i = 0; i < *n; i++)
    {
        if(data[i] > 0)
        {
            pos[j] = i;
            j += 1;
        }
    }

    *n = j;
    pos = realloc(pos, j*sizeof(int));

    return pos;
}
