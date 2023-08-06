#ifndef CDECOR_BITMASK_H_
#define CDECOR_BITMASK_H_ 1

#include <stdint.h>

typedef struct {
    char *array;
    int len;
} bitmask;

bitmask *alloc_bitmask(int size, char *array);
void destroy_bitmask(bitmask *mask);

#endif /* CDECOR_BITMASK_H_ */
