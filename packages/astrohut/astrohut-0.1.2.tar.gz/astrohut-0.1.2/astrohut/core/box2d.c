#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "math.h"
#include "omp.h"
#include "box2d.h"
#include "common.h"
#include "cons.h"

void printInstantNode2d(node2d *node, int t)
{
    char filename[200]; // to store the filename
    char number[20];

    FILE *file;
    sprintf(number, "%d", t);
    strcpy(filename, FILE_PREFIX);
    strcat(filename, "_node_");
    strcat(filename, number);
    strcat(filename, ".dat");
    file = fopen(filename, "w");

    if (file == NULL)
    {
        printf("Error Reading File\n");
        exit(0);
    }
    printNode2d(file, node);
    fclose(file);
}

void printInstantBodies2d(int N, int t, body2d *bodies)
{
    int i;

    char filename[200]; // to store the filename
    char number[20];

    FILE *file;
    sprintf(number, "%d", t);
    strcpy(filename, FILE_PREFIX);
    strcat(filename, "_bodies_");
    strcat(filename, number);
    strcat(filename, ".dat");
    file = fopen(filename, "w");

    if (file == NULL)
    {
        printf("Error Reading File\n");
        exit(0);
    }

    for(i = 0; i < N; i++)
    {
        fprintf(file, "%f %f %f %f %f %f\n", bodies[i].p.x, bodies[i].p.y, bodies[i].v.x,
                                    bodies[i].v.y, bodies[i].a.x, bodies[i].a.y);
    }

    fclose(file);
}

void printInstant2d(node2d *node, body2d *bodies, int t)
{
    printInstantNode2d(node, t);
    printInstantBodies2d(node->Nbodies, t, bodies);
}

body2d *solveInterval2d(int N, node2d **node, body2d *bodies)
{
    int i, j = 0;

    body2d *new = solveInstant2d(node, bodies);

    for(i = 0; i<=N; i++)
    {
        if(FRAMES_EVERY > 0)
        {
            if(i%FRAMES_EVERY == 0)
            {
                printInstant2d(*node, new, j);
                j += 1;
            }
        }

        body2d *new2 = solveInstant2d(node, new);

        swapBody2d(&new2, &new);
        free(new2);
    }
    return new;
}

void swapBody2d(body2d **b1, body2d **b2)
{
    body2d *temp = *b1;
    *b1 = *b2;
    *b2 = temp;
}

void resetAcceleration2d(int N, body2d *bodies)
{
    int i;
    # pragma omp parallel for
    for(i = 0; i < N; i ++)
    {
        bodies[i].a.x = 0;
        bodies[i].a.y = 0;
        bodies[i].E = 0;
    }
}

body2d *solveInstant2d(node2d **node, body2d *bodies)
{
    int i, N = (*node)->Nbodies;
    DOUBLE dth = dt*0.5;

    body2d *new = calloc(N, sizeof(body2d));

    DOUBLE *vxh, *vyh;
    vxh = calloc(N, sizeof(DOUBLE));
    vyh = calloc(N, sizeof(DOUBLE));

    resetAcceleration2d(N, bodies);

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        acceleration2d(*node, &(bodies[i]));
        bodies[i].a.x *= G;
        bodies[i].a.y *= G;
        bodies[i].E *= G;
    }

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        vxh[i] = bodies[i].v.x + dth*bodies[i].a.x;
        vyh[i] = bodies[i].v.y + dth*bodies[i].a.y;

        new[i].p.x = bodies[i].p.x + dt*vxh[i];
        new[i].p.y = bodies[i].p.y + dt*vyh[i];
    }

    //swapping
    node2d *temp = *node;
    node2d *new_node = initFirstNode2d(N, new);
    *node = new_node;
    new_node = temp;

    freeNodes2d(new_node);
    free(new_node);

    resetAcceleration2d(N, new);
    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        acceleration2d(*node, &(new[i]));
        new[i].a.x *= G;
        new[i].a.y *= G;
        new[i].E *= G;
    }

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        new[i].v.x = vxh[i] + dth*new[i].a.x;
        new[i].v.y = vyh[i] + dth*new[i].a.y;
        new[i].E += 0.5*MASS_UNIT*(new[i].v.x*new[i].v.x + new[i].v.y*new[i].v.y);
    }

    free(vxh);
    free(vyh);

    return new;
}

node2d *calculateNode2d(node2d *mother_node)
{
    if(mother_node->Nbodies > 1)
    {
        int *xg, *xl, *yg, *yl;
        xg = whereGreater(mother_node->Nbodies, mother_node->xs, mother_node->center.x);
        yg = whereGreater(mother_node->Nbodies, mother_node->ys, mother_node->center.y);
        xl = whereLess(mother_node->Nbodies, mother_node->xs, mother_node->center.x);
        yl = whereLess(mother_node->Nbodies, mother_node->ys, mother_node->center.y);

        int *c1, *c2, *c3, *c4;
        c1 = whereAnd(mother_node->Nbodies, xl, yg);
        c2 = whereAnd(mother_node->Nbodies, xg, yg);
        c3 = whereAnd(mother_node->Nbodies, xg, yl);
        c4 = whereAnd(mother_node->Nbodies, xl, yl);

        free(xg);
        free(xl);
        free(yg);
        free(yl);

        createSubNode2d(mother_node->Nbodies, mother_node->subnode1,
                            mother_node->xs, mother_node->ys, c1);
        createSubNode2d(mother_node->Nbodies, mother_node->subnode2,
                            mother_node->xs, mother_node->ys, c2);
        createSubNode2d(mother_node->Nbodies, mother_node->subnode3,
                            mother_node->xs, mother_node->ys, c3);
        createSubNode2d(mother_node->Nbodies, mother_node->subnode4,
                            mother_node->xs, mother_node->ys, c4);
        free(c1);
        free(c2);
        free(c3);
        free(c4);

        DOUBLE width, height;
        width = 0.5*mother_node->width;
        height = 0.5*mother_node->height;

        mother_node->subnode1->width = width;
        mother_node->subnode2->width = width;
        mother_node->subnode3->width = width;
        mother_node->subnode4->width = width;
        mother_node->subnode1->height = height;
        mother_node->subnode2->height = height;
        mother_node->subnode3->height = height;
        mother_node->subnode4->height = height;

        mother_node->subnode1->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode1->center.y = mother_node->center.y + 0.5*height;

        mother_node->subnode2->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode2->center.y = mother_node->center.y + 0.5*height;

        mother_node->subnode3->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode3->center.y = mother_node->center.y - 0.5*height;

        mother_node->subnode4->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode4->center.y = mother_node->center.y - 0.5*height;

        int n1, n2, n3, n4;
        n1 = mother_node->subnode1->Nbodies;
        n2 = mother_node->subnode2->Nbodies;
        n3 = mother_node->subnode3->Nbodies;
        n4 = mother_node->subnode4->Nbodies;

        if(n1 > 0)
        {
            calculateNode2d(mother_node->subnode1);
        }
        if(n2 > 0)
        {
            calculateNode2d(mother_node->subnode2);
        }
        if(n3 > 0)
        {
            calculateNode2d(mother_node->subnode3);
        }
        if(n4 > 0)
        {
            calculateNode2d(mother_node->subnode4);
        }
    }

    return mother_node;
}

node2d *createNode2d(int Nbodies, node2d *node, DOUBLE *xs, DOUBLE *ys)
{
    if(Nbodies > 0)
    {
        int i;
        if(node == NULL)
        {
            node = calloc(1, sizeof(node2d));
        }

        node->Nbodies = Nbodies;
        node->mass = Nbodies*MASS_UNIT;
        node->subnode1 = calloc(1, sizeof(node2d));
        node->subnode2 = calloc(1, sizeof(node2d));
        node->subnode3 = calloc(1, sizeof(node2d));
        node->subnode4 = calloc(1, sizeof(node2d));

        node->xs = calloc(Nbodies, sizeof(DOUBLE));
        node->ys = calloc(Nbodies, sizeof(DOUBLE));
        for(i = 0; i < Nbodies; i++)
        {
            node->xs[i] = xs[i];
            node->ys[i] = ys[i];
            node->cmass.x += xs[i];
            node->cmass.y += ys[i];
        }

        node->cmass.x *= 1.0/node->Nbodies;
        node->cmass.y *= 1.0/node->Nbodies;
    }
    return node;
}

node2d *createSubNode2d(int Nbodies, node2d *node, DOUBLE *xs, DOUBLE *ys, int *pwhere)
{
    int i, n = Nbodies, *index;

    if(n > 1)
    {
        index = indexWhereTrue(&n, pwhere);
        DOUBLE *indexedXs = calloc(n, sizeof(DOUBLE));
        DOUBLE *indexedYs = calloc(n, sizeof(DOUBLE));

        for(i = 0; i < n; i++)
        {
            indexedXs[i] = xs[index[i]];
            indexedYs[i] = ys[index[i]];
        }

        if(n > 0)
        {
            createNode2d(n, node, indexedXs, indexedYs);
        }

        free(index);
        free(indexedXs);
        free(indexedYs);
    }
    node -> Nbodies = n;
    return node;
}

// point2d *randomPos(int Nbodies)
// {
//     int i;
//     DOUBLE max = RAND_MAX;
//     point2d *pos = malloc(Nbodies*sizeof(point2d));
//
//     for(i = 0; i < Nbodies; i++)
//     {
//         pos[i].x = 2*(0.5 - rand()/max);
//         pos[i].y = 2*(0.5 - rand()/max);
//     }
//     return pos;
// }

node2d *initFirstNode2d(int Nbodies, body2d *bodies)
{
    int i;

    DOUBLE *xs, *ys;
    xs = calloc(Nbodies, sizeof(DOUBLE));
    ys = calloc(Nbodies, sizeof(DOUBLE));

    for(i = 0; i < Nbodies; i++)
    {
        xs[i] = bodies[i].p.x;
        ys[i] = bodies[i].p.y;
    }

    node2d *node = createNode2d(Nbodies, NULL, xs, ys);
    DOUBLE xmin, ymin, xmax, ymax;

    xmin = min(node->Nbodies, node->xs);
    xmax = max(node->Nbodies, node->xs);
    ymin = min(node->Nbodies, node->ys);
    ymax = max(node->Nbodies, node->ys);

    node->width = xmax - xmin;
    node->height = ymax - ymin;
    node->center.x = 0.5*(xmin + xmax);
    node->center.y = 0.5*(ymin + ymax);

    calculateNode2d(node);

    free(xs);
    free(ys);
    return node;
}

void printNode2d(FILE *file, node2d *node)
{   if(node->Nbodies == 1)
    {
        point2d c1, c2, c3, c4;
        c1.x = node->center.x - node->width*0.5;
        c1.y = node->center.y + node->height*0.5;

        c2.x = node->center.x + node->width*0.5;
        c2.y = node->center.y + node->height*0.5;

        c3.x = node->center.x + node->width*0.5;
        c3.y = node->center.y - node->height*0.5;

        c4.x = node->center.x - node->width*0.5;
        c4.y = node->center.y - node->height*0.5;

        fprintf(file, "%f %f %f %f %f %f %f %f %f %f %f %f\n", node->xs[0], node->ys[0],
            c1.x, c2.x, c3.x, c4.x, c1.x,
            c1.y, c2.y, c3.y, c4.y, c1.y);
    }
    if(node->Nbodies > 1)
    {
        printNode2d(file, node->subnode1);
        printNode2d(file, node->subnode2);
        printNode2d(file, node->subnode3);
        printNode2d(file, node->subnode4);
    }
}

void freeNodes2d(node2d *node)
{
    if(node->Nbodies > 0)
    {
        free(node->xs);
        free(node->ys);
    }
    if(node->Nbodies > 1)
    {
        freeNodes2d(node->subnode1);
        freeNodes2d(node->subnode2);
        freeNodes2d(node->subnode3);
        freeNodes2d(node->subnode4);
    }
    free(node->subnode1);
    free(node->subnode2);
    free(node->subnode3);
    free(node->subnode4);

}

body2d *loadFile2d(const char *name, const char *delim, int N)
{
    int i = 0, j = 0;
    int length = 250;

    char line_buffer[length];
    char *split_buffer;

    body2d *bodies = calloc(N, sizeof(body2d));

    FILE *dataFile;
    dataFile = fopen(name, "r");

    if (dataFile == NULL)
    {
        printf("Error Reading File\n");
        exit(0);
    }

    while(fgets(line_buffer, length, dataFile) != NULL)
    {
        j = 0;
        split_buffer = strtok(line_buffer, delim);

        while (split_buffer != NULL)
        {
            if(j == 0){bodies[i].p.x = atof(split_buffer);}
            else if(j == 1){bodies[i].p.y = atof(split_buffer);}
            else if(j == 2){bodies[i].v.x = atof(split_buffer);}
            else if(j == 3){bodies[i].v.y = atof(split_buffer);}
            split_buffer = strtok(NULL, delim);
            j += 1;
        }
        i += 1;
    }

    fclose(dataFile);

    return bodies;
}

void acceleration2d(node2d *node, body2d *object)
{
    if(node->Nbodies > 0)
    {
        DOUBLE dx, dy, r2, prime;
        dx = node->cmass.x - object->p.x;
        dy = node->cmass.y - object->p.y;
        r2 = dx*dx + dy*dy;
        prime = sqrt((pow(node->height, 2.0) + pow(node->width, 2.0))/r2);
        if((node->Nbodies == 1) && (r2 != 0))
        {
            r2 += EPSILON;
            object->a.x += node->mass*dx/pow(r2, 1.5);
            object->a.y += node->mass*dy/pow(r2, 1.5);
            object->E += node->mass*MASS_UNIT/sqrt(r2);
        }
        else if(prime >= TAU)
        {
            acceleration2d(node->subnode1, object);
            acceleration2d(node->subnode2, object);
            acceleration2d(node->subnode3, object);
            acceleration2d(node->subnode4, object);
        }
        else
        {
            r2 += EPSILON;
            object->a.x += node->mass*dx/pow(r2, 1.5);
            object->a.y += node->mass*dy/pow(r2, 1.5);
            object->E += node->mass*MASS_UNIT/sqrt(r2);
        }
    }
}
