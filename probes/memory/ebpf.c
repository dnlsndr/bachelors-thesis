#include <uapi/linux/ptrace.h>

BPF_HASH(usage, u32, u64);
BPF_HASH(address_to_size, u64, u64);
BPF_HASH(allocs, u32, u64);
BPF_HASH(frees, u32, u64);

int trace_alloc(struct tracepoint__kmem__kmalloc *args) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    u64 address = (u64)args->ptr;
    u64 allocated = args->bytes_alloc;
    address_to_size.update(&address, &allocated);

    u64 *current_allocs = allocs.lookup(&pid);
    if (current_allocs) {
        *current_allocs += 1;
        allocs.update(&pid, current_allocs);
    } else {
        u64 one = 1;
        allocs.update(&pid, &one);
    }

    u64 *current_size = usage.lookup(&pid);
    if (current_size) {
        *current_size += args->bytes_alloc;
        usage.update(&pid, current_size);
    } else {
        u64 one = 0;
        usage.update(&pid, &one);
    }



    return 0;
}


int trace_free(struct tracepoint__kmem__kfree *args) {
    u64 address = (u64)args->ptr;
    u64 *size = address_to_size.lookup(&address);

    if (size) {
        u32 pid = bpf_get_current_pid_tgid() >> 32;

        // Updating deallocation count
        u64 *current_frees = frees.lookup(&pid);
        if (current_frees) {
            *current_frees += 1;
            frees.update(&pid, current_frees);
        } else {
            u64 one = 1;
            frees.update(&pid, &one);
        }

        // Updating deallocated size
        u64 *current_size = usage.lookup(&pid);
        if (current_size) {
            if (*current_size >= *size) { // Prevent underflow
                *current_size -= *size;
            }
            usage.update(&pid, current_size);
        }

        // Remove the address entry from address_to_size
        address_to_size.delete(&address);
    }

    return 0;
}