import docker
import matplotlib.pyplot as plt
import time

# Initialize the Docker client
client = docker.from_env()

# Specify the names or IDs of the containers you want to monitor
#container_names_or_ids = ["ditto-ipfs-fabric", "mosquitto", "docker_nginx_1", "docker_connectivity_1", "docker_gateway_1"]
container_names_or_ids = ["ditto-ipfs-fabric", "mosquitto"]

# Initialize empty lists to store data
cpu_usage = [[] for _ in container_names_or_ids]
mem_usage = [[] for _ in container_names_or_ids]

# Create a function to fetch and store container stats
def get_container_stats():
    for i, name_or_id in enumerate(container_names_or_ids):
        container = client.containers.get(name_or_id)
        stats = container.stats(stream=False)
        cpu_percentage = stats['cpu_stats']['cpu_usage']['total_usage'] / stats['cpu_stats']['system_cpu_usage'] * 100.0
        mem_usage_bytes = stats['memory_stats']['usage']
        cpu_usage[i].append(cpu_percentage)
        mem_usage[i].append(mem_usage_bytes / (1024 * 1024))  # Convert to MB

# Create a live plot
plt.ion()  # Turn on interactive mode
fig, axs = plt.subplots(2, 1, figsize=(10, 8))

# Initialize the plot lines
lines = []
for i, name_or_id in enumerate(container_names_or_ids):
    line, = axs[0].plot([], [], label=f'CPU Container {i + 1}')
    lines.append(line)
    line, = axs[1].plot([], [], label=f'Mem Container {i + 1}')
    lines.append(line)

# Set axis labels and legends
axs[0].set_ylabel('CPU Usage (%)')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Memory Usage (MB)')
axs[1].legend()

# Start monitoring and plotting
try:
    while True:
        get_container_stats()
        for i in range(len(container_names_or_ids)):
            lines[i * 2].set_data(range(len(cpu_usage[i])), cpu_usage[i])
            lines[i * 2 + 1].set_data(range(len(mem_usage[i])), mem_usage[i])
        axs[0].relim()
        axs[0].autoscale_view()
        axs[1].relim()
        axs[1].autoscale_view()
        plt.pause(1)
except KeyboardInterrupt:
    pass

# Clean up and close the plot
client.close()
plt.ioff()
plt.show()
