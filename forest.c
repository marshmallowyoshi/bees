#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "forest.h"

#define _CRT_SECURE_NO_WARNINGS

#define MAX 100

int read_branch(FILE *fptr1);

int main(int argc, char* argv[])
{
    FILE* fptr1;
    char c;

    char str[MAX];
    int i = 0, j, from, to;

    fptr1 = fopen(argv[1], "r"); 
  
    if (fptr1 == NULL) { 
        return 1; 
    } 
    for (j = 0; j < 10; j++){
        read_branch(fptr1);
    }
    return 0;
}

int read_branch(FILE *fptr1)
{
    struct branch b;
    fread(&b.depth, sizeof(int8_t), 1, fptr1);
    fread(&b.threshold, sizeof(float), 1, fptr1);
    fread(&b.feature, sizeof(int8_t), 1, fptr1);
    fread(&b.next_node, sizeof(int16_t), 1, fptr1);

    printf("%d %f %d %d\n", b.depth, b.threshold, b.feature, b.next_node);
    return 0;
}