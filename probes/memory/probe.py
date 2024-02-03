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
    b.attach_kprobe(event="__kmalloc", fn_name="alloc")
    b.attach_kretprobe(event="__kmalloc", fn_name="retalloc")
    b.attach_kprobe(event="kfree", fn_name="dealloc")
    global g
    g = Gauge('ebpf_memory_utilization', 'memory utilization', ['pid', 'name'])
    global allocs_counter
    allocs_counter = Counter('ebpf_memory_allocs',
                             'memory allocs', ['pid', 'name'])
    global frees_counter
    frees_counter = Counter('ebpf_memory_frees',
                            'memory frees', ['pid', 'name'])

    get_all_processes()


def get_all_processes():
    for proc in psutil.process_iter():
        if proc.pid not in pid_map:
            pid_map[proc.pid] = read_initial_memory_usage(
                proc.pid)
            g.labels(pid=proc.pid, name=proc.name()).set(
                pid_map[proc.pid])


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
    usage = copy.deepcopy(b["usage"])
    allocs = copy.deepcopy(b["allocs"])
    frees = copy.deepcopy(b["frees"])

    g.clear()

    for k, v in usage.items():
        if k.value not in pid_map:
            pid_map[k.value] = read_initial_memory_usage(k.value)

    for pid, value in pid_map.items():
        name = get_process_name(pid)

        final = value + \
            (usage[ctypes.c_uint32(pid)].value if ctypes.c_uint32(
                pid) in usage else 0)

        g.labels(pid=pid, name=name).set(final)

        allocs_counter.labels(pid=pid, name=name).inc(
            allocs[ctypes.c_uint32(pid)].value if ctypes.c_uint32(pid) in allocs else 0)

        frees_counter.labels(pid=pid, name=name).inc(
            frees[ctypes.c_uint32(pid)].value if ctypes.c_uint32(pid) in frees else 0)

    b["usage"].clear()
    b["allocs"].clear()
    b["frees"].clear()
