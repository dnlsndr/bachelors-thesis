from prometheus_client import start_http_server
import os
import importlib
import toml
import threading
import time
from collections import defaultdict
from threading import Lock


# Shared store with a lock
shared_store = defaultdict(dict)
store_lock = Lock()


def update_probe(module, config, probe_name):
    while True:
        result = module.update()
        with store_lock:
            shared_store[probe_name] = result
        time.sleep(int(config['aggregation_interval']) / 1000)


# List all folders in the ./probes directory, and import the probe.py
threads = []
for folder in os.listdir("./probes"):
    if not os.path.isdir(os.path.join("./probes", folder)):
        continue
    try:
        with open(os.path.join("./probes", folder, "setup.toml")) as f:
            config = toml.load(f)
            print(
                f"Loaded aggregation interval for probe {folder}: {config}")

        module = importlib.import_module(f"probes.{folder}.probe")
        module.init(config)

        # Create and start a thread for each probe
        thread = threading.Thread(target=update_probe, args=(
            module, config, folder))
        # Optional: make threads daemon if you want them to exit when the main program exits
        thread.daemon = True
        thread.start()
        threads.append(thread)

    except Exception as e:
        print(f"Unable to import probe from folder {folder}: {e}")


# Create a independent thread that loops forever and prints the shared store
def print_store():
    while True:
        # with store_lock:
        # print(shared_store)
        time.sleep(1)


thread = threading.Thread(target=print_store)
thread.daemon = True
thread.start()
threads.append(thread)

# Creae a separate thread in which a webserver runs that publishes the prometheus metrics
start_http_server(8000)


for thread in threads:
    thread.join()
