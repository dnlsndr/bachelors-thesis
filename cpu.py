import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Load BPF program
b = BPF(src_file="./probes/cpu.c")
b.attach_tracepoint(tp="sched:sched_switch", fn_name="oncpu")

window_size = 10
inactive_threshold = 5

data_cpu = {}
data_memory = {}
last_update = {}
fig, (ax_cpu) = plt.subplots(
    1, 1, figsize=(10, 8))  # Create two subplots


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update(frame):

    bar_data_cpu = {}

    # CPU Time Data Collection
    for k, v in b["cpu_time"].items():
        pid = k.value
        cpu_time = v.value
        if pid == 0:
            continue
        if pid not in data_cpu:
            data_cpu[pid] = [cpu_time]
        else:
            if len(data_cpu[pid]) >= window_size:
                data_cpu[pid].pop(0)
            data_cpu[pid].append(cpu_time)
        bar_data_cpu[pid] = data_cpu[pid][-1]

    b["cpu_time"].clear()

    # CPU Chart
    sorted_cpu_data = sorted(bar_data_cpu.items(),
                             key=lambda x: x[1], reverse=True)[:20]
    pids_cpu, cpu_times = zip(*sorted_cpu_data)
    ax_cpu.clear()
    y_pos_cpu = range(len(pids_cpu))
    ax_cpu.barh(y_pos_cpu, cpu_times, tick_label=[
                f"{get_process_name(pid)} (PID {pid})" for pid in pids_cpu])
    ax_cpu.set_xlabel("CPU Time (nanoseconds)")
    ax_cpu.set_ylabel("Processes")
    ax_cpu.set_title("Top 20 Processes by Current CPU Time")

    plt.tight_layout()


ani = FuncAnimation(fig, update, interval=1000)  # Update every second
plt.show()
