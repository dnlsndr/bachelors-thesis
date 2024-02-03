# eBPF benchmarking system sample implementation

This was created for my bachelors thesis. It utilizes eBPF to measure the performance of a system.

## Metrics

- CPU usage: The amount of time the CPU spends executing a specific task, the sched_switch tracepoint is utilized
- Memory usage: The amount of memory used by the system, the kmalloc and kfree kprobes are used
- Disk I/O: The amount of data read from or written to the disk, the block_rq_issue and block_rq_complete tracepoints are used
