#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "math.h"
#include "omp.h"
#include "box3d.h"
#include "common.h"
#include "cons.h"

void printInstantNode3d(node3d *node, int t)
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
    printNode3d(file, node);
    fclose(file);
}

void printInstantBodies3d(int N, int t, body3d *bodies)
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
        fprintf(file, "%f %f %f %f %f %f %f %f %f\n", bodies[i].p.x, bodies[i].p.y, bodies[i].p.z,
                    bodies[i].v.x, bodies[i].v.y, bodies[i].v.z,
                    bodies[i].a.x, bodies[i].a.y, bodies[i].a.z);
    }

    fclose(file);
}

void printInstant3d(node3d *node, body3d *bodies, int t)
{
    printInstantNode3d(node, t);
    printInstantBodies3d(node->Nbodies, t, bodies);
}

body3d *solveInterval3d(int N, node3d **node, body3d *bodies)
{
    int i, j = 0;

    body3d *new = solveInstant3d(node, bodies);

    for(i = 0; i<=N; i++)
    {
        if(FRAMES_EVERY > 0)
        {
            if(i%FRAMES_EVERY == 0)
            {
                printInstant3d(*node, new, j);
                j += 1;
            }
        }

        body3d *new2 = solveInstant3d(node, new);

        swapBody3d(&new2, &new);
        free(new2);
    }
    return new;
}

void swapBody3d(body3d **b1, body3d **b2)
{
    body3d *temp = *b1;
    *b1 = *b2;
    *b2 = temp;
}

void resetAcceleration3d(int N, body3d *bodies)
{
    int i;
    # pragma omp parallel for
    for(i = 0; i < N; i ++)
    {
        bodies[i].a.x = 0;
        bodies[i].a.y = 0;
        bodies[i].a.z = 0;
        bodies[i].E = 0;
    }
}

body3d *solveInstant3d(node3d **node, body3d *bodies)
{
    int i, N = (*node)->Nbodies;
    DOUBLE dth = dt*0.5;

    body3d *new = calloc(N, sizeof(body3d));

    DOUBLE *vxh, *vyh, *vzh;
    vxh = calloc(N, sizeof(DOUBLE));
    vyh = calloc(N, sizeof(DOUBLE));
    vzh = calloc(N, sizeof(DOUBLE));

    resetAcceleration3d(N, bodies);

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        acceleration3d(*node, &(bodies[i]));
        bodies[i].a.x *= G;
        bodies[i].a.y *= G;
        bodies[i].a.z *= G;
        bodies[i].E *= G;
    }

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        vxh[i] = bodies[i].v.x + dth*bodies[i].a.x;
        vyh[i] = bodies[i].v.y + dth*bodies[i].a.y;
        vzh[i] = bodies[i].v.z + dth*bodies[i].a.z;

        new[i].p.x = bodies[i].p.x + dt*vxh[i];
        new[i].p.y = bodies[i].p.y + dt*vyh[i];
        new[i].p.z = bodies[i].p.z + dt*vzh[i];
    }

    //swapping
    node3d *temp = *node;
    node3d *new_node = initFirstNode3d(N, new);
    *node = new_node;
    new_node = temp;

    freeNodes3d(new_node);
    free(new_node);

    resetAcceleration3d(N, new);
    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        acceleration3d(*node, &(new[i]));
        new[i].a.x *= G;
        new[i].a.y *= G;
        new[i].a.z *= G;
        new[i].E *= G;
    }

    # pragma omp parallel for
    for(i = 0; i < N; i++)
    {
        new[i].v.x = vxh[i] + dth*new[i].a.x;
        new[i].v.y = vyh[i] + dth*new[i].a.y;
        new[i].v.z = vzh[i] + dth*new[i].a.z;
        new[i].E += 0.5*MASS_UNIT*(new[i].v.x*new[i].v.x + new[i].v.y*new[i].v.y + new[i].v.z*new[i].v.z);
    }

    free(vxh);
    free(vyh);
    free(vzh);

    return new;
}

node3d *calculateNode3d(node3d *mother_node)
{
    if(mother_node->Nbodies > 1)
    {
        int *xg, *xl, *yg, *yl, *zg, *zl;
        xg = whereGreater(mother_node->Nbodies, mother_node->xs, mother_node->center.x);
        yg = whereGreater(mother_node->Nbodies, mother_node->ys, mother_node->center.y);
        zg = whereGreater(mother_node->Nbodies, mother_node->zs, mother_node->center.z);

        xl = whereLess(mother_node->Nbodies, mother_node->xs, mother_node->center.x);
        yl = whereLess(mother_node->Nbodies, mother_node->ys, mother_node->center.y);
        zl = whereLess(mother_node->Nbodies, mother_node->zs, mother_node->center.z);

        int *c1, *c2, *c3, *c4;
        c1 = whereAnd(mother_node->Nbodies, xl, yg);
        c2 = whereAnd(mother_node->Nbodies, xg, yg);
        c3 = whereAnd(mother_node->Nbodies, xg, yl);
        c4 = whereAnd(mother_node->Nbodies, xl, yl);

        int *cc1, *cc2, *cc3, *cc4, *cc5, *cc6, *cc7, *cc8;
        cc1 = whereAnd(mother_node->Nbodies, c1, zl);
        cc2 = whereAnd(mother_node->Nbodies, c2, zl);
        cc3 = whereAnd(mother_node->Nbodies, c3, zl);
        cc4 = whereAnd(mother_node->Nbodies, c4, zl);
        cc5 = whereAnd(mother_node->Nbodies, c1, zg);
        cc6 = whereAnd(mother_node->Nbodies, c2, zg);
        cc7 = whereAnd(mother_node->Nbodies, c3, zg);
        cc8 = whereAnd(mother_node->Nbodies, c4, zg);

        free(xg);
        free(xl);
        free(yg);
        free(yl);
        free(zg);
        free(zl);

        createSubNode3d(mother_node->Nbodies, mother_node->subnode1,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc1);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode2,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc2);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode3,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc3);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode4,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc4);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode5,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc5);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode6,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc6);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode7,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc7);
        createSubNode3d(mother_node->Nbodies, mother_node->subnode8,
                            mother_node->xs, mother_node->ys, mother_node->zs, cc8);

        free(c1);
        free(c2);
        free(c3);
        free(c4);
        free(cc1);
        free(cc2);
        free(cc3);
        free(cc4);
        free(cc5);
        free(cc6);
        free(cc7);
        free(cc8);

        DOUBLE width, height, large;
        width = 0.5*mother_node->width;
        height = 0.5*mother_node->height;
        large = 0.5*mother_node->large;

        mother_node->subnode1->width = width;
        mother_node->subnode2->width = width;
        mother_node->subnode3->width = width;
        mother_node->subnode4->width = width;
        mother_node->subnode5->width = width;
        mother_node->subnode6->width = width;
        mother_node->subnode7->width = width;
        mother_node->subnode8->width = width;

        mother_node->subnode1->height = height;
        mother_node->subnode2->height = height;
        mother_node->subnode3->height = height;
        mother_node->subnode4->height = height;
        mother_node->subnode5->height = height;
        mother_node->subnode6->height = height;
        mother_node->subnode7->height = height;
        mother_node->subnode8->height = height;

        mother_node->subnode1->large = large;
        mother_node->subnode2->large = large;
        mother_node->subnode3->large = large;
        mother_node->subnode4->large = large;
        mother_node->subnode5->large = large;
        mother_node->subnode6->large = large;
        mother_node->subnode7->large = large;
        mother_node->subnode8->large = large;

        mother_node->subnode1->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode1->center.y = mother_node->center.y + 0.5*height;
        mother_node->subnode1->center.z = mother_node->center.z - 0.5*large;

        mother_node->subnode2->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode2->center.y = mother_node->center.y + 0.5*height;
        mother_node->subnode2->center.z = mother_node->center.z - 0.5*large;

        mother_node->subnode3->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode3->center.y = mother_node->center.y - 0.5*height;
        mother_node->subnode3->center.z = mother_node->center.z - 0.5*large;

        mother_node->subnode4->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode4->center.y = mother_node->center.y - 0.5*height;
        mother_node->subnode4->center.z = mother_node->center.z - 0.5*large;

        mother_node->subnode5->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode5->center.y = mother_node->center.y + 0.5*height;
        mother_node->subnode5->center.z = mother_node->center.z + 0.5*large;

        mother_node->subnode6->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode6->center.y = mother_node->center.y + 0.5*height;
        mother_node->subnode6->center.z = mother_node->center.z + 0.5*large;

        mother_node->subnode7->center.x = mother_node->center.x + 0.5*width;
        mother_node->subnode7->center.y = mother_node->center.y - 0.5*height;
        mother_node->subnode7->center.z = mother_node->center.z + 0.5*large;

        mother_node->subnode8->center.x = mother_node->center.x - 0.5*width;
        mother_node->subnode8->center.y = mother_node->center.y - 0.5*height;
        mother_node->subnode8->center.z = mother_node->center.z + 0.5*large;

        int n1, n2, n3, n4, n5, n6, n7, n8;
        n1 = mother_node->subnode1->Nbodies;
        n2 = mother_node->subnode2->Nbodies;
        n3 = mother_node->subnode3->Nbodies;
        n4 = mother_node->subnode4->Nbodies;
        n5 = mother_node->subnode5->Nbodies;
        n6 = mother_node->subnode6->Nbodies;
        n7 = mother_node->subnode7->Nbodies;
        n8 = mother_node->subnode8->Nbodies;

        if(n1 > 0)
        {
            calculateNode3d(mother_node->subnode1);
        }
        if(n2 > 0)
        {
            calculateNode3d(mother_node->subnode2);
        }
        if(n3 > 0)
        {
            calculateNode3d(mother_node->subnode3);
        }
        if(n4 > 0)
        {
            calculateNode3d(mother_node->subnode4);
        }
        if(n5 > 0)
        {
            calculateNode3d(mother_node->subnode5);
        }
        if(n6 > 0)
        {
            calculateNode3d(mother_node->subnode6);
        }
        if(n7 > 0)
        {
            calculateNode3d(mother_node->subnode7);
        }
        if(n8 > 0)
        {
            calculateNode3d(mother_node->subnode8);
        }
    }

    return mother_node;
}

node3d *createNode3d(int Nbodies, node3d *node, DOUBLE *xs, DOUBLE *ys, DOUBLE *zs)
{
    if(Nbodies > 0)
    {
        int i;
        if(node == NULL)
        {
            node = calloc(1, sizeof(node3d));
        }

        node->Nbodies = Nbodies;
        node->mass = Nbodies*MASS_UNIT;
        node->subnode1 = calloc(1, sizeof(node3d));
        node->subnode2 = calloc(1, sizeof(node3d));
        node->subnode3 = calloc(1, sizeof(node3d));
        node->subnode4 = calloc(1, sizeof(node3d));
        node->subnode5 = calloc(1, sizeof(node3d));
        node->subnode6 = calloc(1, sizeof(node3d));
        node->subnode7 = calloc(1, sizeof(node3d));
        node->subnode8 = calloc(1, sizeof(node3d));

        node->xs = calloc(Nbodies, sizeof(DOUBLE));
        node->ys = calloc(Nbodies, sizeof(DOUBLE));
        node->zs = calloc(Nbodies, sizeof(DOUBLE));

        for(i = 0; i < Nbodies; i++)
        {
            node->xs[i] = xs[i];
            node->ys[i] = ys[i];
            node->zs[i] = zs[i];

            node->cmass.x += xs[i];
            node->cmass.y += ys[i];
            node->cmass.z += zs[i];
        }

        node->cmass.x *= 1.0/node->Nbodies;
        node->cmass.y *= 1.0/node->Nbodies;
        node->cmass.z *= 1.0/node->Nbodies;
    }
    return node;
}

node3d *createSubNode3d(int Nbodies, node3d *node, DOUBLE *xs, DOUBLE *ys, DOUBLE *zs, int *pwhere)
{
    int i, n = Nbodies, *index;

    if(n > 1)
    {
        index = indexWhereTrue(&n, pwhere);
        DOUBLE *indexedXs = calloc(n, sizeof(DOUBLE));
        DOUBLE *indexedYs = calloc(n, sizeof(DOUBLE));
        DOUBLE *indexedZs = calloc(n, sizeof(DOUBLE));

        for(i = 0; i < n; i++)
        {
            indexedXs[i] = xs[index[i]];
            indexedYs[i] = ys[index[i]];
            indexedZs[i] = zs[index[i]];
        }

        if(n > 0)
        {
            createNode3d(n, node, indexedXs, indexedYs, indexedZs);
        }

        free(index);
        free(indexedXs);
        free(indexedYs);
        free(indexedZs);
    }
    node -> Nbodies = n;
    return node;
}

node3d *initFirstNode3d(int Nbodies, body3d *bodies)
{
    int i;

    DOUBLE *xs, *ys, *zs;
    xs = calloc(Nbodies, sizeof(DOUBLE));
    ys = calloc(Nbodies, sizeof(DOUBLE));
    zs = calloc(Nbodies, sizeof(DOUBLE));

    for(i = 0; i < Nbodies; i++)
    {
        xs[i] = bodies[i].p.x;
        ys[i] = bodies[i].p.y;
        zs[i] = bodies[i].p.z;
    }

    node3d *node = createNode3d(Nbodies, NULL, xs, ys, zs);
    DOUBLE xmin, ymin, zmin, xmax, ymax, zmax;

    xmin = min(node->Nbodies, node->xs);
    xmax = max(node->Nbodies, node->xs);
    ymin = min(node->Nbodies, node->ys);
    ymax = max(node->Nbodies, node->ys);
    zmin = min(node->Nbodies, node->zs);
    zmax = max(node->Nbodies, node->zs);

    node->width = xmax - xmin;
    node->height = ymax - ymin;
    node->large = zmax - zmin;

    node->center.x = 0.5*(xmin + xmax);
    node->center.y = 0.5*(ymin + ymax);
    node->center.z = 0.5*(zmin + zmax);

    calculateNode3d(node);

    free(xs);
    free(ys);
    free(zs);
    return node;
}

void printNode3d(FILE *file, node3d *node)
{   if(node->Nbodies == 1)
    {
        /*
        Solving printing for 3D is pending
        */
        point3d c1, c2, c3, c4;
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
        printNode3d(file, node->subnode1);
        printNode3d(file, node->subnode2);
        printNode3d(file, node->subnode3);
        printNode3d(file, node->subnode4);
        printNode3d(file, node->subnode5);
        printNode3d(file, node->subnode6);
        printNode3d(file, node->subnode7);
        printNode3d(file, node->subnode8);
    }
}

void freeNodes3d(node3d *node)
{
    if(node->Nbodies > 0)
    {
        free(node->xs);
        free(node->ys);
        free(node->zs);
    }
    if(node->Nbodies > 1)
    {
        freeNodes3d(node->subnode1);
        freeNodes3d(node->subnode2);
        freeNodes3d(node->subnode3);
        freeNodes3d(node->subnode4);
        freeNodes3d(node->subnode5);
        freeNodes3d(node->subnode6);
        freeNodes3d(node->subnode7);
        freeNodes3d(node->subnode8);
    }
    free(node->subnode1);
    free(node->subnode2);
    free(node->subnode3);
    free(node->subnode4);
    free(node->subnode5);
    free(node->subnode6);
    free(node->subnode7);
    free(node->subnode8);
}

body3d *loadFile3d(const char *name, const char *delim, int N)
{
    int i = 0, j = 0;
    int length = 250;

    char line_buffer[length];
    char *split_buffer;

    body3d *bodies = calloc(N, sizeof(body3d));

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
            else if(j == 2){bodies[i].p.z = atof(split_buffer);}
            else if(j == 3){bodies[i].v.x = atof(split_buffer);}
            else if(j == 4){bodies[i].v.y = atof(split_buffer);}
            else if(j == 5){bodies[i].v.z = atof(split_buffer);}
            else if(j == 6){bodies[i].a.x = atof(split_buffer);}
            else if(j == 7){bodies[i].a.y = atof(split_buffer);}
            else if(j == 8){bodies[i].a.z = atof(split_buffer);}
            split_buffer = strtok(NULL, delim);
            j += 1;
        }
        i += 1;
    }

    fclose(dataFile);

    return bodies;
}

void acceleration3d(node3d *node, body3d *object)
{
    if(node->Nbodies > 0)
    {
        DOUBLE dx, dy, dz, r2, prime;
        dx = node->cmass.x - object->p.x;
        dy = node->cmass.y - object->p.y;
        dz = node->cmass.z - object->p.z;
        r2 = dx*dx + dy*dy + dz*dz;
        prime = sqrt((pow(node->height, 2.0) + pow(node->width, 2.0) + pow(node->large, 2.0))/r2);
        if((node->Nbodies == 1) && (r2 != 0))
        {
            r2 += EPSILON;
            object->a.x += node->mass*dx/pow(r2, 1.5);
            object->a.y += node->mass*dy/pow(r2, 1.5);
            object->a.z += node->mass*dz/pow(r2, 1.5);
            object->E += node->mass*MASS_UNIT/sqrt(r2);
        }
        else if(prime >= TAU)
        {
            acceleration3d(node->subnode1, object);
            acceleration3d(node->subnode2, object);
            acceleration3d(node->subnode3, object);
            acceleration3d(node->subnode4, object);
            acceleration3d(node->subnode5, object);
            acceleration3d(node->subnode6, object);
            acceleration3d(node->subnode7, object);
            acceleration3d(node->subnode8, object);
        }
        else
        {
            r2 += EPSILON;
            object->a.x += node->mass*dx/pow(r2, 1.5);
            object->a.y += node->mass*dy/pow(r2, 1.5);
            object->a.z += node->mass*dz/pow(r2, 1.5);
            object->E += node->mass*MASS_UNIT/sqrt(r2);
        }
    }
}
