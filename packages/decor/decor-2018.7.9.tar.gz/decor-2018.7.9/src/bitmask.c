#include <stdlib.h>
#include <stdint.h>
#include "bitmask.h"


bitmask *alloc_bitmask(int size, char *array) {
    int i, s;
    bitmask *mask;
    
    s = ((size / 8) + 1) * sizeof(char);
    mask = malloc(sizeof(bitmask) + s);
    if (!mask)
        return NULL;
    mask->len = s;
    mask->array = (char *)(mask + 1);
    for (i=0; i<size; i++) {
        if (array[i] == 0) {
            mask->array[i/8] &= ~(1 << i%8);
        } else {
            mask->array[i/8] |= 1 << i%8;
        }
    }
    return mask;
}


void destroy_bitmask(bitmask *mask) {
    if (mask) {
        free(mask);
    }
}
