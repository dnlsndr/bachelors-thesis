import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import os
from prometheus_client import Gauge

# Load BPF program
b = None
last_run_time = 0  # Global variable to store last run time


def init(inputConfig):
    global config
    config = inputConfig
    print("init cpu probe")
    global b
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ebpf.c')
    b = BPF(src_file=filename)
    b.attach_tracepoint(tp="sched:sched_switch", fn_name="oncpu")
    global g, last_run_time
    g = Gauge('ebpf_cpu_utilization', 'cpu utilization', ['pid', 'name'])
    last_run_time = time.time()  # Initialize last run time


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update():
    try:
        global last_run_time
        current_time = time.time()
        time_diff = current_time - last_run_time  # Calculate time difference
        last_run_time = current_time  # Update last run time
        data = b["cpu_time"].items()
        b["cpu_time"].clear()

        print("time diff", time_diff)
        g.clear()

        # CPU Time Data Collection
        for k, v in data:
            if k.value == 0:
                continue
            name = get_process_name(k.value)
            # Use time_diff for high precision calculation
            g.labels(pid=k.value, name=name).set(
                v.value / (time_diff * 1000000000))

    except Exception as e:
        print(e)
    # Loop  through all gauge value and see if that pid still exists in the system
