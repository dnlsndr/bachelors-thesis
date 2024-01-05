import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load BPF program
b = BPF(src_file="./probes/memory.c")
b.attach_kprobe(event="__kmalloc", fn_name="alloc")
b.attach_kretprobe(event="__kmalloc", fn_name="retalloc")
b.attach_kprobe(event="kfree", fn_name="dealloc")

window_size = 10

data_memory = {}
fig, (ax_mem) = plt.subplots(1, 1, figsize=(10, 8))


def bytes_to_readable(num_bytes):
    """Converts a size in bytes to a more readable format."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:3.1f} {unit}"


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update(frame):
    bar_data_memory = {}

    # Memory Allocation Data Collection
    for k, v in b["allocs"].items():
        pid = k.value
        memory_allocation = v.value
        if pid not in data_memory:
            data_memory[pid] = [memory_allocation]
        else:
            if len(data_memory[pid]) >= window_size:
                data_memory[pid].pop(0)
            data_memory[pid].append(memory_allocation)
        bar_data_memory[pid] = data_memory[pid][-1]

    sorted_mem_data = sorted(bar_data_memory.items(),
                             key=lambda x: x[1], reverse=True)[:20]
    pids_mem, mem_allocations = zip(*sorted_mem_data)
    mem_allocations_readable = [
        bytes_to_readable(mem) for mem in mem_allocations]

    ax_mem.clear()
    y_pos_mem = range(len(pids_mem))
    ax_mem.barh(y_pos_mem, mem_allocations, tick_label=[
                f"{get_process_name(pid)} (PID {pid}) - {mem_allocations_readable[i]}" for i, pid in enumerate(pids_mem)])
    ax_mem.set_xlabel("Memory Allocation")
    ax_mem.set_ylabel("Processes")
    ax_mem.set_title("Top 20 Processes by Memory Allocation")

    plt.tight_layout()


ani = FuncAnimation(fig, update, interval=1000)  # Update every second
plt.show()
