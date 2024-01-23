#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "forest.h"
#include "forest_data.c"


#define _CRT_SECURE_NO_WARNINGS

#define MAX 100

int8_t read_depth(uint8_t* ptr);
branch_t read_branch(uint8_t* ptr);
leaf_t read_leaf(uint8_t* ptr);
uint32_t find_next_tree(uint8_t* ptr, uint32_t sz, uint32_t index);
void print_list(node_t * head);

int main(void)
{
    uint8_t* fptr1;
    uint32_t index = 0;
    branch_t new_branch;
    leaf_t new_leaf;
    int8_t depth;
    float_t samples[4] = {0.22044,  0.440961,         -0.96901,         0.247022};
    float_t temp_vals[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    uint32_t sz;
    bool first = true;
    

    // nodes in linked list represent trees in forest
    node_t * head = NULL;
    head = (node_t *) malloc(sizeof(temp_vals));

    if (head == NULL) {
        return 1;
    }

    head->next = NULL;
    node_t * current = head;

    // read forest from file
    fptr1 = forest_structure;
    sz = sizeof(forest_structure);
  
    if (fptr1 == NULL) { 
        return 1; 
    } 
    while (index < sz) {
        depth = read_depth(&fptr1[index]);
        if (depth < 0) {
            if (first == true) {
                first = false;
            }
            else {
                current->next = (node_t *) calloc(1, sizeof(node_t));
                current = current->next;
            }
            new_leaf = read_leaf(&fptr1[index]);
            index += 21;
            memcpy(current->val, new_leaf.score, sizeof(new_leaf.score));
            current->next = NULL;
            index = find_next_tree(fptr1, sz, index);
        }
        else {
            new_branch = read_branch(&fptr1[index]);
            index += 8;
            if (samples[new_branch.feature] > new_branch.threshold) {
                index += new_branch.next_node;
            }
            else {
                continue;
            }
        }
    }
    print_list(head);
    return 0;
}

int8_t read_depth(uint8_t* ptr)
{
    int8_t d;
    d = (int8_t)*ptr;
    // fread(&d, sizeof(int8_t), 1, ptr);
    // fseek(ptr, -1, SEEK_CUR);
    return d;
}

branch_t read_branch(uint8_t* ptr)
{
    union {
        float_t f;
        uint8_t t[4];
    } u;
    branch_t b;
    b.depth = *ptr++;

    u.t[0] = (*ptr++);
    u.t[1] = (*ptr++);
    u.t[2] = (*ptr++);
    u.t[3] = (*ptr++);
    b.threshold = u.f;
    b.feature = *ptr++;
    b.next_node = (int16_t)((*ptr++));
    b.next_node |= (int16_t)(*ptr++) << 8;
    return b;
}

leaf_t read_leaf(uint8_t* ptr)
{
    leaf_t l;
    l.depth = *ptr++;
    for (int i = 0; i < 10; i++) {
        l.score[i] = (int16_t)((*ptr++));
        l.score[i] |= (int16_t)(*ptr++) << 8;
    }
    // fread(&l.depth, sizeof(int8_t), 1, ptr);
    // fread(&l.score, sizeof(int16_t), 10, ptr);
    return l;
}

uint32_t find_next_tree(uint8_t* ptr, uint32_t sz, uint32_t index)
{
    int8_t d;
    d = read_depth(&ptr[index]);
    while (d != 1) {
        if (index >= sz) {
            break;
        }
        if (d < 0) {
            index += 21;
        }
        else {
            index += 8;
        }
        d = read_depth(&ptr[index]);
    }
    return index;
}

void print_list(node_t * head) 
{
    node_t * current = head;
    int16_t sample_count[NUM_CLASSES];
    int16_t total = 0;
    int16_t tree_index = 0;
    float_t total_proba[FOREST_SIZE][NUM_CLASSES];
    float_t probs[NUM_CLASSES];

    while (current != NULL) {
        for (int i = 0; i < NUM_CLASSES; i++) {
            printf("%d ", current->val[i]);
            sample_count[i] = (current->val[i]);
            total += current->val[i];
        }
        current = current->next;
        printf("\n");
        for (int i = 0; i < NUM_CLASSES; i++) {
            total_proba[tree_index][i] = (float_t)sample_count[i] / total;
            printf("%f ", total_proba[tree_index][i]);
        }
        printf("\n\n");
        tree_index++;
        total = 0;
    }

    for (int i = 0; i < NUM_CLASSES; i++) {
        probs[i] = 0;
        for (int j = 0; j < FOREST_SIZE; j++) {
            probs[i] += total_proba[j][i] / FOREST_SIZE;
        }
    }
    printf("\n probabilities: %f %f %f %f %f %f %f %f %f %f\n", probs[0], probs[1], probs[2], probs[3], probs[4], probs[5], probs[6], probs[7], probs[8], probs[9]);
}
