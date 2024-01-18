#include <stdint.h>

typedef struct { 
    int8_t depth;
    float threshold;
    int8_t feature;
    int16_t next_node;
} branch_t;

typedef struct {
    int8_t depth;
    int16_t score[10];
} leaf_t;

typedef struct node {
    int16_t val[10];
    struct node * next;
} node_t;
