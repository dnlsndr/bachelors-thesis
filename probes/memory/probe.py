from prometheus_client import Gauge, Counter
import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import re
import ctypes
import copy

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './ebpf.c')

print(filename)

# Load BPF program
b = None
pid_map = {}


def init(inputConfig):
    global config
    config = inputConfig
    print("init memory probe")
    global b
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ebpf.c')
    b = BPF(src_file=filename)

    global g
    g = Gauge('ebpf_memory_utilization', 'memory utilization', ['pid', 'name'])
    global allocs_counter
    allocs_counter = Counter('ebpf_memory_allocs',
                             'memory allocs', ['pid', 'name'])
    global frees_counter
    frees_counter = Counter('ebpf_memory_frees',
                            'memory frees', ['pid', 'name'])

    for proc in psutil.process_iter():
        b['usage'][ctypes.c_int(proc.pid)] = ctypes.c_uint64(
            read_initial_memory_usage(proc.pid)
        )

    b.attach_tracepoint(tp="kmem:kmalloc", fn_name="trace_alloc")
    b.attach_tracepoint(tp="kmem:kmem_cache_alloc", fn_name="trace_alloc")
    b.attach_tracepoint(tp="kmem:kfree", fn_name="trace_free")
    b.attach_tracepoint(tp="kmem:kmem_cache_free", fn_name="trace_free")


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def read_initial_memory_usage(pid):
    try:
        with open(f'/proc/{pid}/status', 'r') as file:
            content = file.read()
            # Extract the RSS value `(Resident Set Size)
            rss_values = re.findall(r'VmSize:\s+(\d+)', content)
            rss_values = [int(val) for val in rss_values]
            return sum(rss_values) * 1024
    except FileNotFoundError:
        return 0


def update():
    usage = b["usage"]
    allocs = b["allocs"]
    frees = b["frees"]

    for pid, value in usage.items():
        name = get_process_name(pid.value)

        # print(name, pid, value.value)
        if name == "allocator":
            print("allocator size", pid, value.value)

        # g.labels(pid=pid, name=name).set(value)

        # allocs_counter.labels(pid=pid, name=name).inc(
        #     allocs[ctypes.c_uint32(pid)].value if ctypes.c_uint32(pid) in allocs else 0)

        # frees_counter.labels(pid=pid, name=name).inc(
        #     frees[ctypes.c_uint32(pid)].value if ctypes.c_uint32(pid) in frees else 0)

    for pid, value in allocs.items():
        name = get_process_name(pid.value)
        if name == "allocator":
            print("allocator allocs", pid, value.value)

    for pid, value in frees.items():
        name = get_process_name(pid.value)
        if name == "allocator":
            print("allocator frees", pid, value.value)

    # b["usage"].clear()
    # b["allocs"].clear()
    # b["frees"].clear()
