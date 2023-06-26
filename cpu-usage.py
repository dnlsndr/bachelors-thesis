from bcc import BPF
import os
import matplotlib.pyplot as plt
import time

def main():
    bpf = BPF(src_file="cpu-usage.bpf.c")
    bpf.attach_kprobe(event="finish_task_switch.isra.0", fn_name="oncpu")
    # bpf.attach_tracepoint("sched_process_exit", "oncpu")

    print("eBPF program loaded and attached probe. Press Ctrl+C to exit.")

    time.sleep(4)


    items = list(filter( lambda x: (x[1].value > 0) ,bpf["counts"].items()))


    pid_mapping = bpf["pid_mapping"].items()

    pid_dict = {}

    for (k, v) in pid_mapping:
        pid_dict[k.value] = v.comm

    result = {}

    for (k, v) in items:
        result[k.pid] = {
            "value": v.value,
            "pid": k.pid >> 32,
            "name": pid_dict[k.pid]
        }

    print(result.items())

    items = sorted(items, key=lambda x: x[1].value)

    fig = plt.figure(figsize = (6, 10))
    ax = fig.add_subplot(111)

    ax.barh([str(k) for k, v in result.items()], [v["value"] for k, v in result.items()], tick_label = [v["name"] for k, v in result.items()])

    plt.tight_layout()
    plt.savefig('plot.png')
    plt.close()




if __name__ == "__main__":
    main()