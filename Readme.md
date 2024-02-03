# A Symphony of Metrics: Assessing the Advantages of eBPF over conventional Benchmarking Tools

This is an eBPF benchmarking system reference implementation and was created for my [bachelors thesis](https://github.com/dnlsndr/bachelors-ebpf/blob/main/assets/bachelors_thesis_daniel_schneider_final.pdf). It utilizes eBPF to measure the utilization of system resources.

## Metrics

- CPU usage: The amount of time the CPU spends executing a specific task, the sched_switch tracepoint is utilized
- Memory usage: The amount of memory used by the system, the kmalloc and kfree kprobes are used
- Disk I/O: The amount of data read from or written to the disk, the block_rq_issue and block_rq_complete tracepoints are used

## Requirements

- Python 3.x
- bcc (follow [installation](https://github.com/iovisor/bcc/blob/master/INSTALL.md) instructions)
- Linux kernel 4.1 or newer with BPF support
- root access

## Usage

To run this reference-implementation, you will need to execute the main.py in superuser mode:

```bash
sudo python main.py
```

## Functionality

Most of the functionality can be found in my [bachelors thesis](https://github.com/dnlsndr/bachelors-ebpf/blob/main/assets/bachelors_thesis_daniel_schneider_final.pdf). The main.py file is the entry point of the program.
It schedules the probes and starts the main aggregator. Each probe is responsible of collecting a specific metric and the aggregator is responsible to correctly aggregate these metrics, which are then published via the data advertisement API. This API is based on the Prometheus API and can be accessed via the [http://localhost:8000/metrics](http://localhost:8000/metrics) endpoint.
