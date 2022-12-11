#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf.h>
#include <linux/sched.h>

struct data_t
{
    u32 pid;
    u64 usage;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(usage);

int measure_cpu_usage(struct pt_regs *ctx)
{
    struct data_t data = {};

    data.pid = bpf_get_current_pid_tgid();
    data.usage = 50;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    usage.perf_submit(ctx, &data, sizeof(data));

    return 0;
}