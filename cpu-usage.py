from bcc import BPF
import os
import matplotlib.pyplot as plt

def main():
    bpf = BPF(src_file="cpu-usage.bpf.c")
    bpf.attach_kprobe(event="finish_task_switch.isra.0", fn_name="oncpu")
    # bpf.attach_tracepoint("sched_process_exit", "offcpu")

    print("eBPF program loaded and attached to Docker cgroup. Press Ctrl+C to exit.")

    while 1:
        try:
            items = bpf["counts"].items()

            for (k, v) in items:
                print(k.name, k.pid, v.value)


            fig = plt.figure(figsize = (5, 10))

            plt.barh([str(k.pid) for (k, v) in items], [v.value for (k, v) in items], tick_label = [k.name for (k, v) in items])

            plt.savefig('plot.png')

        except KeyboardInterrupt:
            print("Exiting...")
            exit()
        # (task, pid, cpu, flags, ts, msg) = bpf.trace_fields()
        # (pid, comm, cmd, us) = bpf.ksyms[msg[4:]].split()
        # print(f"{ts}: {comm} {pid} {us}")


if __name__ == "__main__":
    main()
