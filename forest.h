#include <stdint.h>
struct branch {
    int depth;
    float threshold;
    unsigned char feature;
    int next_node;
};

struct leaf {
    int depth;
    int16_t score[10];
};