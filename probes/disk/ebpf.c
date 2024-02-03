#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf.h>


struct io_data {
    u64 read_bytes;
    u64 read_iops;
    u64 write_bytes;
    u64 write_iops;
};

BPF_HASH(io_stats, u32, struct io_data);

int complete(struct tracepoint__block__block_rq_complete *args) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct io_data *data, zero = {};

    // Get the I/O data for the current process
    data = io_stats.lookup_or_init(&pid, &zero);
    // if (!data) {
    //     return 0; // Exit if data is not found or cannot be initialized
    // }

    // Check the operation type: Read (R), Write (W), Sync (S), etc.
    // 'rwbs' is an array of characters; you might need to check the first character or more depending on your requirements.
    char op = args->rwbs[0];

    // Update read or write metrics based on the operation type
    if (op == 'R') {
        data->read_iops += 1;
        // data->read_bytes += args->nr_sector * 512 ; // Assuming 512 bytes per sector
    } else if (op == 'W') {
        data->write_iops += 1;
        // data->write_bytes += args->nr_sector * 512 ; // Assuming 512 bytes per sector
    }

    // Update the hash map with the new data
    io_stats.update(&pid, data);

    return 0;
}

int issue(struct tracepoint__block__block_rq_issue *args) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct io_data *data, zero = {};

    if  (pid == 0) {
        return 0;
    }

    // Get the I/O data for the current process
    data = io_stats.lookup_or_init(&pid, &zero);
    // if (!data) {
    //     return 0; // Exit if data is not found or cannot be initialized
    // }

    // Check the operation type: Read (R), Write (W), Sync (S), etc.
    // 'rwbs' is an array of characters; you might need to check the first character or more depending on your requirements.
    char op = args->rwbs[0];

    // Update read or write metrics based on the operation type
    if (op == 'R') {
        data->read_bytes += args->nr_sector * 512 ; // Assuming 512 bytes per sector
    } else if (op == 'W') {
        data->write_bytes += args->nr_sector * 512 ; // Assuming 512 bytes per sector
    }

    // Update the hash map with the new data
    io_stats.update(&pid, data);

    return 0;
}