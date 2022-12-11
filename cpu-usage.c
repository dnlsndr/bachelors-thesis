#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf.h>
#include <linux/sched.h>
#include <linux/perf_event.h>
// struct data_t
// {
//     u32 pid;
//     u64 usage;
//     char comm[TASK_COMM_LEN];
// };

BPF_HASH(usage, int, int);
BPF_HASH(last_usage, int, int);

int measure_cpu_usage(struct bpf_perf_event_data *ctx)
{
    int pid = bpf_get_current_pid_tgid();

    bpf_perf_prog_read_value(ctx, struct bpf_perf_event_value * buf, u32 buf_size)

        int cpu_usage = 1000;

    usage.update(&pid, &cpu_usage);

    return 0;
}