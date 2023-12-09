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


def update(frame):
    current_time = time.time()
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

    # Remove inactive PIDs
    inactive_pids = [pid for pid, last_time in last_update.items(
    ) if current_time - last_time > inactive_threshold]
    for pid in inactive_pids:
        del data[pid]
        del last_update[pid]

    b["cpu_time"].clear()

    ax.clear()
    for pid, timings in data.items():
        ax.plot(timings, label=f"PID {pid}")

    plt.xlabel("Time (seconds)")
    plt.ylabel("CPU Time (nanoseconds)")
    plt.title("CPU Time per Process (Sliding Window)")
    plt.legend()


ani = FuncAnimation(fig, update, interval=100)  # Update every second

plt.show()
