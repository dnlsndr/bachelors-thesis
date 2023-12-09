#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

BPF_HASH(start, u32);
BPF_HASH(cpu_time, u32, u64);

int oncpu(struct tracepoint__sched__sched_switch *args)
{

    u32 prev_pid = args->prev_pid;
    u32 next_pid = args->next_pid;

    u64 ts, *tsp, delta, *timep;

    // Check if process is switching out
    if (prev_pid != 0)
    {
        ts = bpf_ktime_get_ns();
        start.update(&prev_pid, &ts);
    }

    // Process switching in
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    tsp = start.lookup(&pid);
    if (tsp != 0)
    {
        delta = bpf_ktime_get_ns() - *tsp;
        timep = cpu_time.lookup(&pid);
        if (timep != 0)
        {
            *timep += delta;
        }
        else
        {
            cpu_time.update(&pid, &delta);
        }
        start.delete(&pid);
    }

    // ts = bpf_ktime_get_ns();
    // start.update(&pid, &ts);

    return 0;
}