#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define MINBLOCK_US 1

struct key_t
{
    char name[TASK_COMM_LEN];
    int pid;
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
BPF_STACK_TRACE(stack_traces, 10240);

int oncpu(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid;
    u64 ts, *tsp;

    // record previous thread sleep time
    if (!(prev->flags & PF_KTHREAD))
    {
        pid = prev->pid;
        ts = bpf_ktime_get_ns();
        start.update(&pid, &ts);
    }

    // calculate current thread's delta time
    pid = bpf_get_current_pid_tgid();
    tsp = start.lookup(&pid);
    if (tsp == 0)
        return 0; // missed start or filtered
    u64 delta = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    delta = delta / 1000;
    if (delta < MINBLOCK_US)
        return 0;

    // create map key
    u64 zero = 0, *val;
    struct key_t key = {};
    int stack_flags = 0;

    /*
    if (!(prev->flags & PF_KTHREAD))
      stack_flags |= BPF_F_USER_STACK;
    */

    bpf_get_current_comm(&key.name, sizeof(key.name));
    // key.stack_id = stack_traces.get_stackid(ctx, stack_flags);
    key.pid = prev->pid;

    val = counts.lookup_or_try_init(&key, &zero);
    if (val)
    {
        (*val) += delta;
    }
    return 0;
}