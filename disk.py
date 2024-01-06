import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load BPF program
b = BPF(src_file="./probes/disk.c")  # Adjust the file name as needed
b.attach_kprobe(event="vfs_read", fn_name="vfs_read_probe")
b.attach_kprobe(event="vfs_write", fn_name="vfs_write_probe")

window_size = 10
inactive_threshold = 5

data_io = {}
fig, ax_io = plt.subplots(1, 1, figsize=(10, 8))


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update(frame):
    bar_data_io_read = {}
    bar_data_io_write = {}

    # I/O Data Collection
    for k, v in b["io_stats"].items():
        pid = k.value
        read_count, write_count = v.read_iops, v.write_iops
        if pid not in data_io:
            data_io[pid] = [(read_count, write_count)]
        else:
            if len(data_io[pid]) >= window_size:
                data_io[pid].pop(0)
            data_io[pid].append((read_count, write_count))

        bar_data_io_read[pid] = read_count
        bar_data_io_write[pid] = write_count

    b["io_stats"].clear()

    # Sorting Data
    sorted_io_data_read = sorted(
        bar_data_io_read.items(), key=lambda x: x[1], reverse=True)[:20]
    sorted_io_data_write = sorted(
        bar_data_io_write.items(), key=lambda x: x[1], reverse=True)[:20]

    # I/O Chart for Read and Write
    ax_io.clear()
    y_pos_read = range(len(sorted_io_data_read))
    y_pos_write = [y + 0.4 for y in y_pos_read]  # Offset write bars

    read_counts = [count for _, count in sorted_io_data_read]
    write_counts = [bar_data_io_write[pid] for pid, _ in sorted_io_data_read]

    ax_io.barh(y_pos_read, read_counts, height=0.4,
               color='blue', label='Read IOPS')
    ax_io.barh(y_pos_write, write_counts, height=0.4,
               color='green', label='Write IOPS')

    # Labels
    pids_io = [pid for pid, _ in sorted_io_data_read]
    ax_io.set_yticks([y + 0.2 for y in y_pos_read])
    ax_io.set_yticklabels(
        [f"{get_process_name(pid)} (PID {pid})" for pid in pids_io])
    ax_io.set_xlabel("I/O Operations (Read/Write)")
    ax_io.set_ylabel("Processes")
    ax_io.set_title("Top 20 Processes by I/O Operations (Read/Write)")
    ax_io.legend()

    plt.tight_layout()


ani = FuncAnimation(fig, update, interval=1000)  # Update every second
plt.show()
