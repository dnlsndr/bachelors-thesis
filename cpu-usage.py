import bcc
import sys
import time
# pid= int(sys.argv[1])

# Load the eBPF program into the kernel
bpf_text = open("./cpu-usage.c", "r").read()
b = bcc.BPF(text=bpf_text)
# Attach the eBPF function to the sched_switch tracepoint
b.attach_perf_event(
    ev_type=bcc.PerfType.SOFTWARE,
    ev_config=bcc.PerfSWConfig.CPU_CLOCK,
    fn_name="measure_cpu_usage",
    sample_freq=10
)

# def print_event(cpu, data, size):
#     event = b["usage"].event(data)

#     print(event.pid, event.usage, event.comm)

# b['usage'].open_perf_buffer(print_event)

while 1:
    usage = b.get_table("usage")

    print(usage.items())
    # for k, v in sorted(usage.items(), key=lambda usage: usage[1].value):
    #     print("%10d \"%s\"" % (v.value, k.c.encode('string-escape')))
    # b.perf_buffer_poll()
    time.sleep(1)
    # print(b['usage'])