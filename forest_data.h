#include <stdint.h>
#define FEATURE_COUNT 4
#define FOREST_SIZE 10
#define NUM_CLASSES 20

typedef int8_t depth_t;
typedef int8_t feature_t;
typedef int16_t next_node_t;
typedef int16_t score_t;

typedef struct {
    depth_t depth;
    float threshold;
    feature_t feature;
    next_node_t next_node;
} branch_t;

typedef struct {
    depth_t depth;
    score_t score[NUM_CLASSES];
} leaf_t;

typedef struct node {
    score_t val[NUM_CLASSES];
    struct node * next;
} node_t;

