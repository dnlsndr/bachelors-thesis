from prometheus_client import Gauge
import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import re

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './ebpf.c')

print(filename)

# Load BPF program
b = None
initial_memory_usage = {}


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
            return sum(rss_values) * 1024  # Convert to bytes
    except FileNotFoundError:
        return 0


def update():
    data = b["usage"].items()
    b["usage"].clear()

    g.clear()

    for k, v in data:
        if k.value == 0:
            continue
        if k.value not in initial_memory_usage:
            initial_memory_usage[k.value] = read_initial_memory_usage(k.value)
        name = get_process_name(k.value)
        total_memory_usage = initial_memory_usage[k.value] + v.value
        g.labels(pid=k.value, name=name).set(total_memory_usage)
