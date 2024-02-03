#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

BPF_HASH(usage, u32, u64);
BPF_HASH(address_to_size, u64, u64);
BPF_HASH(allocs, u32, u64);
BPF_HASH(frees, u32, u64);

int alloc(struct pt_regs *ctx, size_t size, gfp_t gfp) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;

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
        *current_size += size;
        usage.update(&pid, current_size);
    } else {
        usage.update(&pid, &size);
    }

    return 0;
}

int retalloc(struct pt_regs *ctx) {
    u64 addr = PT_REGS_RC(ctx);
    if (addr == 0) return 0;

    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 *size = usage.lookup(&pid);
    if (size) {
        address_to_size.update(&addr, size);
    }

    return 0;
}

int dealloc(struct pt_regs *ctx, void *addr) {
    u64 address = (u64)addr;
    u64 *size = address_to_size.lookup(&address);
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    u64 *current_frees = frees.lookup(&pid);
    if (current_frees) {
        *current_frees += 1;
        frees.update(&pid, current_frees);
    } else {
        u64 one = 1;
        frees.update(&pid, &one);
    }

    if (size) {

        u64 *current_total = usage.lookup(&pid);
        if (current_total && *current_total >= *size) {
            *current_total -= *size;
            usage.update(&pid, current_total);
        }

        address_to_size.delete(&address);
    }
    return 0;
}