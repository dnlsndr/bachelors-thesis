#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

const size_t AllocSize = 1024 * 1024;        // 1 KB
const size_t Threshold = 20 * 1024* 1024; // 20 KB

int main() {
    size_t allocated = 0;
    size_t alloc_count = 0;
    size_t alloc_capacity = 10; // Initial capacity for array of pointers
    unsigned char **allocations = malloc(alloc_capacity * sizeof(unsigned char*));

    while (1) {
        if (allocated + AllocSize > Threshold) {
            // Free allocated memory
            for (size_t i = 0; i < alloc_count; i++) {
                free(allocations[i]);
            }
            allocated = 0;
            alloc_count = 0;
            printf("Memory cleared\n");
        }

        if (alloc_count >= alloc_capacity) {
            // Increase the capacity of the allocations array
            alloc_capacity *= 2;
            allocations = realloc(allocations, alloc_capacity * sizeof(unsigned char*));
        }

        // Allocate memory
        unsigned char *memory = malloc(AllocSize);
        allocations[alloc_count++] = memory;
        allocated += AllocSize;

        printf("Allocated: %lu MB\n", allocated / 1024 / 1024);
        sleep(1);
    }

    // Code to free the allocations array (not reached due to the loop)
    // free(allocations);

    return 0;
}
