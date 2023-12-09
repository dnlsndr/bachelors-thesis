import psutil  # Import psutil

from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Load BPF program
b = BPF(src_file="./probes/oncpu.bpf.c")
b.attach_tracepoint(tp="sched:sched_switch", fn_name="oncpu")

window_size = 10  # Window size for sliding window
inactive_threshold = 5  # Time in seconds after which PID is considered inactive

data = {}
last_update = {}  # Dictionary to track last update time for each PID
fig, ax = plt.subplots()


def get_process_name(pid):
    """Get process name by PID."""
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update(frame):
    current_time = time.time()
    bar_data = {}  # Dictionary to store current data for bar chart

    for k, v in b["cpu_time"].items():
        pid = k.value
        cpu_time = v.value

        # Update data and last update time
        if pid not in data:
            data[pid] = [cpu_time]
            last_update[pid] = current_time
        else:
            # Maintain window size
            if len(data[pid]) >= window_size:
                data[pid].pop(0)
            data[pid].append(cpu_time)
            last_update[pid] = current_time

        # Store the most recent data for bar chart
        bar_data[pid] = data[pid][-1]

    # Remove inactive PIDs
    inactive_pids = [pid for pid, last_time in last_update.items(
    ) if current_time - last_time > inactive_threshold]
    for pid in inactive_pids:
        del data[pid]
        del last_update[pid]

    b["cpu_time"].clear()

    # Sort bar_data by CPU time and keep the top 20
    sorted_data = sorted(
        bar_data.items(), key=lambda x: x[1], reverse=True)[:20]
    pids, cpu_times = zip(*sorted_data)

    ax.clear()
    y_pos = range(len(pids))  # Create categorical bands for each PID
    ax.barh(y_pos, cpu_times, tick_label=[
            f"{get_process_name(pid)} (PID {pid})" for pid in pids])

    plt.xlabel("CPU Time (nanoseconds)")
    plt.ylabel("Processes")
    plt.title("Top 20 Processes by Current CPU Time")

    # Adjust legend position
    ax.legend(loc='upper center', bbox_to_anchor=(
        0.5, -0.05), shadow=True, ncol=2)

    # Adjust layout
    plt.tight_layout()


ani = FuncAnimation(fig, update, interval=10000)  # Update every second

plt.show()
