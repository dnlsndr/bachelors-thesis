#include <uapi/linux/ptrace.h>

BPF_HASH(start, u32);
BPF_HASH(cpu_time, u32, u64);

int oncpu(struct tracepoint__sched__sched_switch *args)
{
    u32 prev_pid = args->prev_pid;
    u32 next_pid = args->next_pid;
    u64 *prev_start_time, curr_time, time_diff;

    // Get current time
    curr_time = bpf_ktime_get_ns();

    // Update time for previous process
    prev_start_time = start.lookup(&prev_pid);
    if (prev_start_time != 0)
    {
        time_diff = curr_time - *prev_start_time;
        u64 *prev_cpu_time = cpu_time.lookup_or_init(&prev_pid, &time_diff);
        if (prev_cpu_time)
        {
            *prev_cpu_time += time_diff;
        }
        start.delete(&prev_pid);
    }



    // Record start time for next process
    start.update(&next_pid, &curr_time);

    return 0;
}