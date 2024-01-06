#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct io_data {
    u64 read_bytes;
    u64 read_iops;
    u64 write_bytes;
    u64 write_iops;
};

BPF_HASH(io_stats, u32, struct io_data);

int vfs_read_probe(struct pt_regs *ctx, struct file *file, char __user *buf, size_t size) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct io_data *data, zero = {};
    data = io_stats.lookup_or_try_init(&pid, &zero);
    if (data) {
        data->read_bytes += size;
        data->read_iops += 1;
        io_stats.update(&pid, data);
    }
    return 0;
}

int vfs_write_probe(struct pt_regs *ctx, struct file *file, const char __user *buf, size_t size) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct io_data *data, zero = {};
    data = io_stats.lookup_or_try_init(&pid, &zero);
    if (data) {
        data->write_bytes += size;
        data->write_iops += 1;
        io_stats.update(&pid, data);
    }
    return 0;
}
