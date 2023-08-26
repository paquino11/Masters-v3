import psutil
import time
import functools

def get_ram_cpu(func, *args, **kwargs):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Start measuring resource usage before executing the function
        start_cpu = psutil.cpu_percent()
        start_ram = psutil.virtual_memory().used

        # Execute the provided function
        result = func(*args, **kwargs)

        # Measure resource usage after executing the function
        end_cpu = psutil.cpu_percent()
        end_ram = psutil.virtual_memory().used

        cpu_usage = end_cpu - start_cpu
        ram_usage = end_ram - start_ram

        print(f"CPU Usage: {cpu_usage}%")
        print(f"RAM Usage: {ram_usage / (1024 ** 2):.2f} MB")

        return result

    return wrapper

# Example usage
@get_ram_cpu
def example_function(n):
    total = 0
    for i in range(n):
        total += i
    time.sleep(2)  # Simulating some work
    return total

example_function(1000000)