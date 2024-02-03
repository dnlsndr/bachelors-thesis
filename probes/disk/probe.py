import psutil
from bcc import BPF
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from prometheus_client import Gauge, Counter


b = None
# Load BPF program
data_io = {}


def init(inputConfig):
    global config
    config = inputConfig
    print("init disk probe")
    global b
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ebpf.c')
    b = BPF(src_file=filename)
    b.attach_tracepoint(tp="block:block_rq_complete",
                        fn_name="complete")
    b.attach_tracepoint(tp="block:block_rq_issue",
                        fn_name="issue")

    global read_bytes
    read_bytes = Gauge('ebpf_disk_reads_bytes',
                       'disk reads bytes', ['pid', 'name'])

    global write_bytes
    write_bytes = Gauge('ebpf_disk_writes_bytes',
                        'disk writes bytes', ['pid', 'name'])

    global reads
    reads = Gauge('ebpf_disk_reads', 'disk reads', ['pid', 'name'])

    global writes
    writes = Gauge('ebpf_disk_writes', 'disk writes', ['pid', 'name'])


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def update():
    data = b["io_stats"].items()

    # read_bytes.clear()
    # write_bytes.clear()
    # reads.clear()
    # writes.clear()

    for k, v in data:
        name = get_process_name(k.value)

        read_bytes.labels(pid=k.value, name=name).set(v.read_bytes)

        write_bytes.labels(pid=k.value, name=name).set(v.write_bytes)

        reads.labels(pid=k.value, name=name).set(v.read_iops)

        writes.labels(pid=k.value, name=name).set(v.write_iops)

    # b["io_stats"].clear()
