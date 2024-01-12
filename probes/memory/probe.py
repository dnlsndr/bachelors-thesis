from prometheus_client import Gauge
import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import re
import ctypes

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

    for proc in psutil.process_iter():
        if proc.pid not in initial_memory_usage:
            initial_memory_usage[proc.pid] = read_initial_memory_usage(
                proc.pid)
            g.labels(pid=proc.pid, name=proc.name()).set(
                initial_memory_usage[proc.pid])


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
    data = b["usage"]
    b["usage"].clear()

    g.clear()

    for k, v in data.items():
        # try:
        #     process = psutil.Process(k.value)
        # except psutil.NoSuchProcess:
        #     g.remove(pid=k.value)
        #     continue
        # if not process.is_running():
        #     g.remove(pid=k.value)
        #     continue
        if k.value not in initial_memory_usage:
            initial_memory_usage[k.value] = read_initial_memory_usage(k.value)

    for pid, value in initial_memory_usage.items():
        # try catch
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            continue

        name = get_process_name(pid)

        # add data[pid].value if its not None
        final = value + \
            (data[ctypes.c_uint32(pid)].value if ctypes.c_uint32(pid) in data else 0)

        # if ctypes.c_uint32(pid) in data:
        #     print("data", pid, data[ctypes.c_uint32(pid)].value)
        g.labels(pid=pid, name=name).set(final)

    # loop through all processes and prefill the initial memory usage
