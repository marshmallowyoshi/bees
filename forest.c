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
float_t* predict_proba(node_t * current, float_t args[NUM_CLASSES]);
float_t* predict_proba_forest(float_t args[FOREST_SIZE][NUM_CLASSES]);

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
    float_t total[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    int16_t tree_count = 0;
    // float_t total_raw[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    // float_t sample_sum = 0;
    // int16_t votes[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    // int16_t temp_max = 0;
    // int16_t temp_max_idx = 0;
    // float_t prob_temp[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    // float_t prob_sum[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    // float_t prob_max = 0;
    // int16_t vote_max = 0;
    // int16_t vote_max_idx = 0;

    while (current->next != NULL) {
        current = current->next;
        tree_count += 1;
    }

    float_t total_proba[tree_count];

    while (current != NULL) {
        // temp_max = 0;
        // temp_max_idx = 0;
        for (int i = 0; i < 10; i++) {
            printf("%d ", current->val[i]);
            total[i] += (current->val[i]);
            // if (temp_max < current->val[i]) {
            //         temp_max = current->val[i];
            //         temp_max_idx = i;
            //     } 
        }
    //     printf("| %d | " , temp_max_idx);
    //     sample_sum = current->val[0] + current->val[1] + current->val[2] + current->val[3] + current->val[4] + current->val[5] + current->val[6] + current->val[7] + current->val[8] + current->val[9];
    //     for (int i = 0; i < 10; i++) {
    //         prob_temp[i] = current->val[i] / sample_sum;
    //         prob_sum[i] = (prob_sum[i] + prob_temp[i]) / 10;
    //     }
    //     printf("%f", prob_temp[temp_max_idx]);
    //     votes[temp_max_idx] = votes[temp_max_idx] + 1;
        current = current->next;
        printf("\n");
    }
    // sample_sum = total[0] + total[1] + total[2] + total[3] + total[4] + total[5] + total[6] + total[7] + total[8] + total[9];
    // for (int i = 0; i < 10; i++) {
    //     total_raw[i] = total[i];
    //     total[i] = total[i];

    //     if (prob_max < prob_sum[i]) {
    //         prob_max = prob_sum[i];
    //         temp_max_idx = i;
    //     }
    //     if (vote_max < votes[i]) {
    //         vote_max = votes[i];
    //         vote_max_idx = i;
    //     }
    // }
    // printf("Raw: %f %f %f %f %f %f %f %f %f %f\n", total_raw[0], total_raw[1], total_raw[2], total_raw[3], total_raw[4], total_raw[5], total_raw[6], total_raw[7], total_raw[8], total_raw[9]);
    // printf( "Percentage: %f %f %f %f %f %f %f %f %f %f\n", total[0], total[1], total[2], total[3], total[4], total[5], total[6], total[7], total[8], total[9]);
    // printf("Votes: %d %d %d %d %d %d %d %d %d %d\n", votes[0], votes[1], votes[2], votes[3], votes[4], votes[5], votes[6], votes[7], votes[8], votes[9]);
    // printf("Probabilities: %f %f %f %f %f %f %f %f %f %f\n", prob_sum[0], prob_sum[1], prob_sum[2], prob_sum[3], prob_sum[4], prob_sum[5], prob_sum[6], prob_sum[7], prob_sum[8], prob_sum[9]);
    // printf("Weighted Vote: %d %s\n", temp_max_idx, classes[temp_max_idx]);
    // printf("Direct Vote: %d %s\n", vote_max_idx, classes[vote_max_idx]);
}

float_t* predict_proba(node_t * current, float_t args[NUM_CLASSES])
{
    int16_t sample_count = 0;
    for (int i = 0; i < NUM_CLASSES; i++) {
        sample_count += current->val[i];
    }
    for (int i = 0; i < NUM_CLASSES; i++) {
        args[i] = (float_t)current->val[i] / sample_count;
    }
    return args;
}

float_t* predict_proba_forest(float_t args[FOREST_SIZE][NUM_CLASSES])
{
    float_t probs[NUM_CLASSES];
    for (int i = 0; i < NUM_CLASSES; i++) {
        probs[i] = 0;
        for (int j = 0; j < FOREST_SIZE; j++) {
            probs[i] += args[j][i] / FOREST_SIZE;
        }
    }
    return probs;
}
