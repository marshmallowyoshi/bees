#include <stdio.h>
#include <stdlib.h>

#define _CRT_SECURE_NO_WARNINGS

#define MAX 100

int read_braanch(FILE *fptr1, char str[]);

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

    
}

int read_branch(FILE *fptr1, char str[])
{
    
    return 0;
}