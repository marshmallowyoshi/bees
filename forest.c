#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "forest.h"

#define _CRT_SECURE_NO_WARNINGS

#define MAX 100

int8_t read_depth(FILE* ptr);
branch_t read_branch(FILE* ptr);
leaf_t read_leaf(FILE* ptr);
void find_next_tree(FILE* ptr, int sz);
void print_list(node_t * head);

int main(int argc, char* argv[])
{
    FILE* fptr1;
    branch_t new_branch;
    leaf_t new_leaf;
    int8_t depth;
    float_t samples[4] = {0, 0, 0, 0};
    float_t temp_vals[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    long int sz;
    bool first = true;

    // nodes in linked list represent trees in forest
    node_t * head = NULL;
    head = (node_t *) malloc(sizeof(temp_vals));

    if (head == NULL) {
        return 1;
    }

    // memcpy(head->val, temp_vals, sizeof(temp_vals));
    head->next = NULL;
    node_t * current = head;

    // read forest from file
    fptr1 = fopen("linked_forest.bin", "rb");
    fseek(fptr1, 0L, SEEK_END);
    sz = ftell(fptr1);
    fseek(fptr1, 0L, SEEK_SET);
  
    if (fptr1 == NULL) { 
        return 1; 
    } 
    while (ftell(fptr1) < sz) {
        depth = read_depth(fptr1);
        if (depth < 0) {
            if (first == true) {
                first = false;
            }
            else {
                current->next = (node_t *) calloc(1, sizeof(node_t));
                current = current->next;
            }
            new_leaf = read_leaf(fptr1);
            memcpy(current->val, new_leaf.score, sizeof(new_leaf.score));
            current->next = NULL;
            find_next_tree(fptr1, sz);
        }
        else {
            new_branch = read_branch(fptr1);
            if (samples[new_branch.feature] < new_branch.threshold) {
                fseek(fptr1, new_branch.next_node, SEEK_CUR);
            }
            else {
                continue;
            }
        }
    }
    fclose(fptr1);
    print_list(head);
    return 0;
}

int8_t read_depth(FILE* ptr)
{
    int8_t d;
    fread(&d, sizeof(int8_t), 1, ptr);
    fseek(ptr, -1, SEEK_CUR);
    return d;
}

branch_t read_branch(FILE* ptr)
{
    branch_t b;
    fread(&b.depth, sizeof(int8_t), 1, ptr);
    fread(&b.threshold, sizeof(float_t), 1, ptr);
    fread(&b.feature, sizeof(int8_t), 1, ptr);
    fread(&b.next_node, sizeof(int16_t), 1, ptr);
    return b;
}

leaf_t read_leaf(FILE* ptr)
{
    leaf_t l;
    fread(&l.depth, sizeof(int8_t), 1, ptr);
    fread(&l.score, sizeof(int16_t), 10, ptr);
    return l;
}

void find_next_tree(FILE* ptr, int sz)
{
    int8_t d;
    d = read_depth(ptr);
    while (d != 1) {
        if (ftell(ptr) >= sz) {
            break;
        }
        if (d < 0) {
            fseek(ptr, 21, SEEK_CUR);
        }
        else {
            fseek(ptr, 8, SEEK_CUR);
        }
        d = read_depth(ptr);
    }
}

void print_list(node_t * head) 
{
    node_t * current = head;

    while (current != NULL) {
        for (int i = 0; i < 10; i++) {
            printf("%d ", current->val[i]);
        }
        current = current->next;
        printf("\n");
    }
}
