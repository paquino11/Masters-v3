import psutil
import time
import threading
import np

def get_cpu_ram_usage(interval=1):
    """
    Function to continuously monitor CPU and RAM usage.
    """
    cpu_usage = []
    ram_usage = []
    while True:
        cpu_percent = psutil.cpu_percent(interval=interval)
        ram_percent = psutil.virtual_memory().percent

        cpu_usage = np.append(cpu_usage, cpu_percent)
        ram_usage = np.append(ram_usage, ram_percent)

        time.sleep(interval)

def my_function():
    for i in range(1, 5):
        print(i)
        time.sleep(1)


# Start monitoring CPU and RAM usage in a separate thread
monitor_thread = threading.Thread(target=get_cpu_ram_usage)
monitor_thread.daemon = True  # This allows the thread to exit when the main program ends
monitor_thread.start()


# Call your main function
my_function()
moni