#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define MINBLOCK_US 1000000

struct key_t
{
    u64 pid;
};
struct cmd_t
{
    char comm[TASK_COMM_LEN];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
BPF_HASH(pid_mapping, u64, struct cmd_t);
// BPF_STACK_TRACE(stack_traces, 10240);

int oncpu(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid;
    u64 ts, *tsp;

    // record previous thread sleep time
    // if (!(prev->flags & PF_KTHREAD))
    // {
    pid = prev->pid;
    ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    // }

    // calculate current thread's delta time
    pid = bpf_get_current_pid_tgid();
    tsp = start.lookup(&pid);
    if (tsp == 0)
        return 0; // missed start or filtered
    u64 delta = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    delta = delta / 1000;

    if (delta < MINBLOCK_US)
    {
        return 0;
    }

    // create map key
    u64 zero = 0, *val;
    struct key_t key = {};
    int stack_flags = 0;

    u64 user_space_pid = bpf_get_current_pid_tgid();
    // key.stack_id = stack_traces.get_stackid(ctx, stack_flags);
    key.pid = user_space_pid;

    struct cmd_t cmd = {};

    bpf_get_current_comm(&cmd.comm, sizeof(cmd.comm));

    pid_mapping.update(&user_space_pid, &cmd);

    val = counts.lookup_or_try_init(&key, &zero);
    if (val)
    {
        (*val) += delta;
    }
    return 0;
}