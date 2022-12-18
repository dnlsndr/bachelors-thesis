#include <linux/kernel.h>
#include <linux/ptrace.h>
#include <uapi/linux/bpf.h>
#include <uapi/linux/bpf_perf_event.h>
#include <uapi/linux/perf_event.h>
// struct data_t
// {
//     u32 pid;
//     u64 usage;
//     char comm[TASK_COMM_LEN];
// };

BPF_HASH(usage, int, long);

// BPF_HASH(last_usage, int, int);

int measure_cpu_usage(struct bpf_perf_event_data *ctx)
{

    struct bpf_perf_event_value value_buf;

    long result = bpf_perf_prog_read_value(ctx, (void *)&value_buf, sizeof(struct bpf_perf_event_value));

    if (result < 0)
    {
        return 0;
    }

    int pid = bpf_get_current_pid_tgid();

    // bpf_trace_printk("%d", &data);

    // int time = bpf_ktime_get_ns();

    // if (time < 0)
    // {
    //     return 0;
    // }

    usage.update(&pid, &value_buf);

    // u64 ts, *tsp, delta;

    // // attempt to read stored timestamp
    // u64 tsp = last.lookup(&pid);
    // if (tsp != NULL)
    // {
    //     delta = bpf_ktime_get_ns() - *tsp;

    //     usage.update(&pid, &delta);

    //     if (delta < 1000000000)
    //     {
    //         // output if time is less than 1 second
    //         bpf_trace_printk("%d\\n", delta / 1000000);
    //     }
    //     last.delete(&key);
    // }

    // if ()
    // pid_hist.update(&pid, &time);

    // bpf_perf_prog_read_value(ctx, struct bpf_perf_event_value * buf, u32 buf_size);

    // int cpu_usage = 1000;

    return 0;
}