import bcc
import sys
import time
from tabulate import tabulate
import os
import matplotlib.pyplot as plt
from textwrap import wrap
# pid= int(sys.argv[1])

pid = os.getpid()


import subprocess
def get_pname(id):
    p = subprocess.Popen(["ps -o cmd= {}".format(id)], stdout=subprocess.PIPE, shell=True)
    return str(p.communicate()[0])
# Load the eBPF program into the kernel
bpf_text = open("./cpu-usage.bpf.c", "r").read()
b = bcc.BPF(text=bpf_text)

# Attach the eBPF function to the sched_switch tracepoint
b.attach_perf_event(
    ev_type=bcc.PerfType.HARDWARE,
    ev_config=bcc.PerfHWConfig.CPU_CYCLES,
    fn_name="measure_cpu_usage",
    sample_freq=10
)

# def print_event(cpu, data, size):
#     event = b["usage"].event(data)

#     print(event.pid, event.usage, event.comm)

# b['usage'].open_perf_buffer(print_event)

while 1:
    # result = b.trace_fields()

    usage = b.get_table("usage")

    # print(tabulate(usage.items()))


    data = list(map(lambda datapoint: (str(datapoint[0].value), datapoint[1].value), usage.items()))

    data.sort(key=lambda item: item[1])

    x, y = zip(*data)

    print(x, y)

    # print(data)
    # labels = list(map(lambda process: str(process[0].value), data))

    # [ '\n'.join(wrap(l, 20)) for l in labels ]

    # values = list(map(lambda process: process[1].value, data))
    # print(labels, values)
    plt.bar(x, y)
    plt.savefig('plot.png')
    plt.clf()

    # for k, v in sorted(usage.items(), key=lambda usage: usage[1].value):
    #     print("%10d \"%s\"" % (v.value, k.c.encode('string-escape')))
    # b.perf_buffer_poll()
    time.sleep(2)
    # print(b['usage'])

