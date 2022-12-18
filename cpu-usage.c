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
BPF_HASH(last, int, int);

// BPF_HASH(last_usage, int, int);

int measure_cpu_usage(struct bpf_perf_event_data *ctx)
{

    struct bpf_perf_event_value data =
        {};

    bpf_perf_prog_read_value(ctx, &data, sizeof(data));

    int pid = bpf_get_current_pid_tgid() >> 32;

    bpf_trace_printk("%d", &data);

    int time = bpf_ktime_get_ns();

    // if (time < 0)
    // {
    //     return 0;
    // }

    usage.update(&pid, &data);

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