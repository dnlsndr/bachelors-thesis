import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from prometheus_client import Gauge


b = None
# Load BPF program
data_io = {}


def init(inputConfig):
    global config
    config = inputConfig
    print("init cpu probe")
    global b
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ebpf.c')
    b = BPF(src_file=filename)
    b.attach_kprobe(event="vfs_read", fn_name="vfs_read_probe")
    b.attach_kprobe(event="vfs_write", fn_name="vfs_write_probe")
    global throughput
    global iops
    throughput = Gauge('ebpf_disk_throughput',
                       'disk throughput', ['pid', 'name', 'type'])
    iops = Gauge('ebpf_disk_iops', 'disk iops', ['pid', 'name', 'type'])


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update():
    data = b["io_stats"].items()
    b["io_stats"].clear()

    throughput.clear()
    iops.clear()

    for k, v in data:
        name = get_process_name(k.value)

        throughput.labels(pid=k.value, name=name,
                          type='read').set(v.read_bytes)
        throughput.labels(pid=k.value, name=name,
                          type='write').set(v.write_bytes)
        iops.labels(pid=k.value, name=name, type='read').set(v.read_iops)
        iops.labels(pid=k.value, name=name, type='write').set(v.write_iops)
