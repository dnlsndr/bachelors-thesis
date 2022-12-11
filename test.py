import bcc
import sys

# pid= int(sys.argv[1])

# Load the eBPF program into the kernel
# bpf_text = open("./cpu-usage.c", "r").read()
# b = bcc.BPF(text='int kprobe__sys_clone(void *ctx) { bpf_trace_printk("Hello, World!\\n"); return 0; }')
bcc.BPF(text='int kprobe__sys_clone(void *ctx) { bpf_trace_printk("Hello, World!\\n"); return 0; }').trace_print()
# Attach the eBPF function to the sched_switch tracepoint
# b.attach_perf_event(
#     ev_type=bcc.PerfType.SOFTWARE,
#     ev_config=bcc.PerfSWConfig.CPU_CLOCK,
#     pid=pid,
#     fn_name="measure_cpu_usage",
#     sample_freq=60
# )