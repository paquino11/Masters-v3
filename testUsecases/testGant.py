import matplotlib.pyplot as plt
import numpy as np

# Categories represent tasks
categories = ['Task 1', 'Task 2', 'Task 3', 'Task 4']

# Values represent timestamps (start and end dates)
values = [0, 5, 12, 20]

# Calculate durations based on timestamps
durations = [values[i + 1] - values[i] for i in range(len(values) - 1)]

# Create a Gantt chart
fig, ax = plt.subplots()

# Plot horizontal bars representing tasks
ax.barh(categories[:-1], durations, left=values[:-1])

# Set axis labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Tasks')
ax.set_title('Gantt Chart')

# Set the x-axis limits
ax.set_xlim(0, max(values[-1], max(durations)))

# Now imagine you have your CPU and RAM usage data as lists:
cpu_usage = np.random.random(20) * 100
ram_usage = np.random.random(20) * 16

# Create a second subplot for the CPU usage
cpu_ax = ax.twinx()
cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
cpu_ax.set_ylabel('CPU usage (%)')

# Create a third subplot for the RAM usage
ram_ax = ax.twinx()
ram_ax.plot(ram_usage, color='b', label='RAM usage')
ram_ax.set_ylabel('RAM usage (GB)')

# Add a legend
fig.legend(loc='upper right')

plt.show()

plt.show()
