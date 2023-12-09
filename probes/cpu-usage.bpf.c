#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define MINBLOCK_US 1000000

struct key_t
{
    u64 tid;
};
struct cmd_t
{
    char comm[TASK_COMM_LEN];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u64);
BPF_HASH(pid_mapping, u64, struct cmd_t);

int oncpu(struct pt_regs *ctx)
{
    u64 tid;
    u64 ts, *tsp;

    // calculate current thread's delta time
    tid = bpf_get_current_pid_tgid();
    tsp = start.lookup(&tid);
    if (tsp != 0)
    {
        u64 delta = bpf_ktime_get_ns() - *tsp;
        start.delete(&tid);
        delta = delta / 1000;

        if (delta >= MINBLOCK_US)
        {
            // create map key
            u64 zero = 0, *val;
            struct key_t key = {};
            key.tid = tid;

            struct cmd_t cmd = {};
            bpf_get_current_comm(&cmd.comm, sizeof(cmd.comm));

            pid_mapping.update(&tid, &cmd);

            val = counts.lookup_or_try_init(&key, &zero);
            if (val)
            {
                (*val) += delta;
            }
        }
    }

    // record current thread's start time
    ts = bpf_ktime_get_ns();
    start.update(&tid, &ts);

    return 0;
}
