import logging
import colorlog
import time
import random
import uuid
import string
import matplotlib.pyplot as plt
import numpy as np
import psutil
import asyncio
import time
import threading
import os
import subprocess
import sys
import requests


import runners.consortium
import runners.oemv2
import runners.gatewayv2
import runners.smartdevice
import runners.alice
import runners.dave
import runners.bob
import runners.charlie
import AgentsDeployment.deploy_agents
import FabricDeployment.deploy_fabric

GREEN = '\033[1;32m'
RESET = '\033[0m'
CONSORTIUM = 15
DAVE = 7
FABRIC = 112
VON = 13

total_start_time = time.time()

total_end_time = time.time()
total_execution_time = total_end_time - total_start_time

# Create a logger and set its level to DEBUG
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Remove existing handlers
logger.handlers = []

# Create a custom filter to exclude logger name
class ExcludeLoggerFilter(logging.Filter):
    def filter(self, record):
        record.name = ''  # Exclude logger name
        return True

# Create a formatter with colors
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(message)s%(reset)s',
    log_colors={
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_yellow',
    }
)

# Create a stream handler and set its formatter
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add the stream handler to the logger
logger.addHandler(stream_handler)

# Add the custom filter to the handler
stream_handler.addFilter(ExcludeLoggerFilter())

categories = []
values = []

def get_cpu_ram_usage(interval=1, cpu_usage=[], ram_usage=[], stop_event=None):
    while not stop_event.is_set():
        cpu_percent = psutil.cpu_percent(interval=interval)
        ram_percent = psutil.virtual_memory().percent

        cpu_usage.append(cpu_percent)
        ram_usage.append(ram_percent)



#OEM ENROLLMENT - PHASE 1
def oem_enrollment1():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()
    
    print_bold("OEM ENROLLMENT - PHASE 1")
    step1_oem_enrollment1()
    step2_oem_enrollment1()
    uuid1 = step3_oem_enrollment1()
    step4_oem_enrollment1(uuid1)
    step5_oem_enrollment1()
    step6_oem_enrollment1()
    step7_oem_enrollment1()
    step8_oem_enrollment1()
    step9_oem_enrollment1()
    step10_oem_enrollment1()
    step11_oem_enrollment1()

    stop_event.set()

    monitor_thread.join()

    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    ax.set_xlim(0, sum(non_zero_values))
    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()
    print(values)
    categories.clear()
    values.clear()

#OEM ENROLLMENT - PHASE 2
def oem_enrollment2():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("OEM ENROLLMENT - PHASE 2")
    step1_oem_enrollment2()
    step2_oem_enrollment2()
    step3_oem_enrollment2()
    step4_oem_enrollment2()
    step5_oem_enrollment2()
    step6_oem_enrollment2()
    step7_oem_enrollment2()

        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#DEV MODEL REG
def dev_mode_reg():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("DEVICE MODEL REGISTRATION")
    step1_dev_model_reg()
    step2_dev_model_reg()
    step3_dev_model_reg()
    step4_dev_model_reg()
    step5_dev_model_reg()
    step6_dev_model_reg()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()
    categories.clear()
    values.clear()

#EGW REG
def egw_reg():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("EDGE GATEWAY REGISTRATION")
    step1_egw_reg()
    step2_egw_reg()
    did = step3_egw_reg()
    step4_egw_reg(did)
    step5_egw_reg()
    step6_egw_reg()
    step7_egw_reg()
    step8_egw_reg()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#SD REG
def sd_reg():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("SMART DEVICE REGISTRATION")
    step1_sd_reg()
    step2_sd_reg()
    did = step3_sd_reg()
    step4_sd_reg(did)
    step5_sd_reg()
    step6_sd_reg()
    step7_sd_reg()
    step8_sd_reg()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#CONSUMER BUY DEVICE
def consumer_buys_device():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("CONSUMER BUYS DEVICE")
    deploy_agents(5, "alice")
    categories.append('0')
    step1_cons_buy_dev()
    step2_cons_buy_dev()
    step3_cons_buy_dev()
    step4_cons_buy_dev()
    step5_cons_buy_dev()
    step6_cons_buy_dev()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#CLAIM EDGE GATEWAY
def claim_egw():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("CLAIM EDGE GATEWAY")
    step1_claim_egw()
    step2_claim_egw()
    step3_claim_egw()
    step4_claim_egw()
    step5_claim_egw()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#CLAIM SMART DEVICE
def claim_sd():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("CLAIM SMART DEVICE")
    deploy_agents(11, "bob")
    categories.append('0')
    step1_claim_sd()
    step2_claim_sd()
    step3_claim_sd()
    step4_claim_sd()
    step5_claim_sd()
    step6_claim_sd()
    step7_claim_sd()
    step8_claim_sd()
    step9_claim_sd()
    step10_claim_sd()
    step11_claim_sd()
    step12_claim_sd()
    step13_claim_sd()
    step14_claim_sd()
    step15_claim_sd()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#TWIN DEVICE
def twin_sd():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("TWIN DEVICE")
    step1_twin_sd()
    step2_twin_sd()
    step3_twin_sd()
    step4_twin_sd()
    step5_twin_sd()
    step6_twin_sd()
    step7_twin_sd()
    step8_twin_sd()
    step9_twin_sd()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#UNTWIN DEVICE
def untwin_sd():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    print("UNTWIN DEVICE")
    step1_untwin_sd()
    step2_untwin_sd()
    step3_untwin_sd()
    step4_untwin_sd()
    step5_untwin_sd()
    step6_untwin_sd()
    step7_untwin_sd()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()

#SELL SD
def sell_sd():
    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    categories.clear()
    values.clear()

    # Start monitoring CPU and RAM usage in a separate thread
    monitor_thread = threading.Thread(target=get_cpu_ram_usage, args=(1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start() 

    print("SELL DEVICE")
    deploy_agents(5, "charlie")
    categories.append('00')
    deploy_agents(9, "gateway #2")
    categories.append('01')
    step1_sell_sd()
    step2_sell_sd()
    step3_sell_sd()
    step4_sell_sd()
    step5_sell_sd()
    step6_sell_sd()
    step7_sell_sd()
    step8_sell_sd()
    step9_sell_sd()
    step10_sell_sd()
    step11_sell_sd()
    step12_sell_sd()
    step13_sell_sd()
        # Set the stop event to signal the monitoring thread to stop
    stop_event.set()

    # Wait for the monitoring thread to complete
    monitor_thread.join()

    # Print the CPU and RAM usage arrays
    print("CPU Usage:", cpu_usage)
    print("RAM Usage:", ram_usage)


    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)

    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)

    # Create a Gantt chart
    fig, ax = plt.subplots()

    # Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)

    # Set axis labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    #ax.set_title('Use Case 1')

    # Set the x-axis limits to the sum of values
    ax.set_xlim(0, sum(non_zero_values))

    # Now imagine you have your CPU and RAM usage data as lists:
    #cpu_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 100
    #ram_usage = np.random.random(int(np.ceil(sum(non_zero_values)))) * 16

    print(cpu_usage)
    print(ram_usage)

    # Create a second subplot for the CPU usage
    cpu_ax = ax.twinx()
    cpu_ax.plot(cpu_usage, color='r', label='CPU usage')
    cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    plt.show()

    categories.clear()
    values.clear()


#OEM ENROLLMENT - PHASE 1 STEPS
def step1_oem_enrollment1():
    total_start_time = time.time()
    logger.debug('1 - Dave taps the “Enroll OEM” button on the consortium’s marketing website.')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A \n{RESET}")
    categories.append('1')
    values.append(0.0001)

def step2_oem_enrollment1():
    logger.debug('2 - The marketing website makes a call to C:1 Admin API to requests an OOB URI')
    total_start_time = time.time()
    url = 'http://0.0.0.0:8081/connections/create-invitation?auto_accept=true'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "metadata": {},
        "my_label": "Bob",
        "recipient_keys": [
            "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        ],
        "routing_keys": [
            "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        ],
        "service_endpoint": "http://192.168.56.102:8020"
    }

    #response = requests.post(url, headers=headers, json=data)

    # Check the response
    """if response.status_code == 200:
        print("Request successful.")
        print(response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)"""
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    categories.append('2')
    values.append(total_execution_time)

def step3_oem_enrollment1():
    uuid1 = uuid.uuid4()
    logger.debug('3 - C:1 creates an UUID for the transaction and stores it in the “Transaction Table”')
    print(uuid1)
    value = runners.consortium.create_uuid_and_store()
    categories.append('3')
    values.append(value)
    return uuid1

def step4_oem_enrollment1(uuid1):
    logger.debug('4 - C:1 creates the OOB and the goal code39 c2dt.consortium.enroll.OEM?'+str(uuid1))
    value = runners.consortium.oob_with_goalcode()
    categories.append('4')
    values.append(value)

def step5_oem_enrollment1():
    total_start_time = time.time()
    logger.debug('5 - The marketing website redirects Dave to a new page that contains the OOB URI along with the instructions \nto deploy the OEM’s DIDComm Agent (O:1).')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('5')
    values.append(0.0001)

def step6_oem_enrollment1():
    logger.debug('6 - The OEM staff deploy the DIDComm and starts it up.  ')
    deploy_agents(13, "OEM")
    categories.append('6')

def step7_oem_enrollment1():
    logger.debug('7 - During first boot O:1 creates its public DID')
    value = runners.oemv2.create_pub_did()
    categories.append('7')
    values.append(value)

def step8_oem_enrollment1():
    total_start_time = time.time()
    logger.debug('8 - D:1 clicks the OOB URI which opens his smart wallet via a deep link.')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('8')
    values.append(0.0001)

def step9_oem_enrollment1():
    logger.debug('9 - D:1 establishes a connection with C:1 using the OOB URI ')
    value = runners.dave.establish_conection_oob_inv()
    categories.append('9')
    values.append(value)

def step10_oem_enrollment1():
    total_start_time = time.time()
    logger.debug('10 - C:1 recognizes the goal code UUID and recognizes it refers to the ongoing OEM enrollment and creates a new entry into the Agent Table.')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time} \n{RESET}")
    categories.append('10')
    values.append(total_execution_time)

def step11_oem_enrollment1():
    logger.debug('11 - D:1 establishes a connection with O:1 using an implicit invitation')
    value = runners.dave.establish_conection_implicit_inv()
    categories.append('11')
    values.append(value)


#OEM ENROLLMENT - PHASE 2 STEPS
def step1_oem_enrollment2():
    logger.debug('1 - D:1 makes an introduction to O:1 passing the OOB along with goal code (Basic message exhange work arround)')
    value = runners.dave.establish_conection_implicit_inv()*2
    categories.append('1')
    values.append(value)

def step2_oem_enrollment2():
    logger.debug('2 - O:1 uses the OOB to connect to C:1 ')
    total_execution_time=runners.oemv2.establish_conection_oob_inv()
    categories.append('2')
    values.append(total_execution_time)

def step3_oem_enrollment2():
    logger.debug('3 - C:1 recognizes the goal code UUID and recognizes it refers to the ongoing OEM enrollment and updates the previously entered Agent Table with the OEM’s public DID.')
    total_execution_time=runners.consortium.reg_oem_pub_did()
    categories.append('3')
    values.append(total_execution_time)

def step4_oem_enrollment2():
    logger.debug('4 - C:1 proposes O:1 the Enrollment VC. ')
    total_execution_time=runners.consortium.propose_vc()
    categories.append('4')
    values.append(total_execution_time)

def step5_oem_enrollment2():
    logger.debug('5 - O:1 provides the proofs to C:1. ')
    total_execution_time=runners.oemv2.present_proof()
    categories.append('5')
    values.append(total_execution_time)

def step6_oem_enrollment2():
    logger.debug('6 - Creates a HL Fabric for O:1 and provides the credentials. ')
    total_execution_time=runners.consortium.create_send_fabric_cred()
    categories.append('6')
    values.append(total_execution_time)

def step7_oem_enrollment2():
    logger.debug('7 - C:1 sends the Enrollment VC to O:1. ')
    total_execution_time=runners.consortium.send_vc()
    categories.append('7')
    values.append(total_execution_time)


#DEVICE MODEL REG STEPS
def step1_dev_model_reg():
    logger.debug('1 - D:1 request the menu actions from C:1 using Aries RFC 0509. ')
    total_execution_time=runners.dave.request_menu_actions()
    categories.append('1')
    values.append(total_execution_time)

def step2_dev_model_reg():
    total_start_time = time.time()
    logger.debug('2 - D:1 selects “Register Device Model” along with the information requested by the associated form which includes Name, Description, Features array, Images array, and WoT file. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_dev_model_reg():
    uuid1 = uuid.uuid4()
    logger.debug('3 - C:1 generates a DeviceModelID and anchors the information into DT Ledger. ')
    print(uuid1)
    total_execution_time=runners.consortium.generate_device_model_id()
    categories.append('3')
    values.append(total_execution_time)

def step4_dev_model_reg():
    logger.debug('4 - C:1 loads the WoT file to the consortium source control. ')
    total_execution_time=runners.consortium.add_wot_github()
    categories.append('4')
    values.append(total_execution_time)

def step5_dev_model_reg():
    total_start_time = time.time()
    logger.debug('5 - C:1 loads the images and feature information to the Marketplace App. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('5')
    values.append(0.0001)

def step6_dev_model_reg():
    logger.debug('6 - C:1 send the deviceModelID along with DeviceName to O:1.')
    total_execution_time=runners.consortium.send_devmodid()
    categories.append('6')
    values.append(total_execution_time)

#EGW REG STEPS
def step1_egw_reg():
    total_start_time = time.time()
    logger.debug('1 - The OEM integrates the consortium firmware libraries. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('1')
    values.append(0.0001)

def step2_egw_reg():
    logger.debug('2 - During first boot, the EGW executes a script that boots egw:1. ')
    deploy_agents(9, "edge_gateway") #9 agent + 30 ditto
    categories.append('2')

def step3_egw_reg():
    logger.debug('3 - egw:1 creates the public DID. ')
    did = generate_id()
    print(did)
    total_execution_time=runners.gatewayv2.create_pub_did()
    categories.append('3')
    values.append(total_execution_time)
    return did

def step4_egw_reg(did):
    logger.debug('4 - egw:1 implicit invitation to O:1 using goal c2dt.consortium.registerdevice?'+did)
    total_execution_time=runners.gatewayv2.establish_conection_implicit_inv()
    categories.append('4')
    values.append(total_execution_time)

def step5_egw_reg():
    logger.debug('5 - O:1 sends egw:1 the Genesis VC proposal')
    total_execution_time=runners.oemv2.propose_vc()
    categories.append('5')
    values.append(total_execution_time)

def step6_egw_reg():
    logger.debug('6 - O:1 registers EGW into the DT ledger and creates the EGW’s DT Ledger')
    total_execution_time=runners.oemv2.register_egw_fabric()
    categories.append('6')
    values.append(total_execution_time)

def step7_egw_reg():
    total_start_time = time.time()
    logger.debug('7 - O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('7')
    values.append(0.0001)

def step8_egw_reg():
    logger.debug('8 - O:1 sends egw:1 the Genesis VC. ')
    total_execution_time=runners.oemv2.send_vc()
    categories.append('8')
    values.append(total_execution_time)


#DEV REG STEPS
def step1_sd_reg():
    total_start_time = time.time()
    logger.debug('1 - The OEM integrates the consortium firmware libraries. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('1')
    values.append(0.0001)

def step2_sd_reg():
    logger.debug('2 - During the first boot, the SD executes a script that boots sd:1. ')
    deploy_agents(8, "smart device")
    categories.append('2')


def step3_sd_reg():
    total_start_time = time.time()
    uuid1 = uuid.uuid4()
    logger.debug('3 - sd:1 generates an UUID. ')
    print(uuid1)
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time}\n{RESET}")
    categories.append('3')
    values.append(total_execution_time)
    return uuid1

def step4_sd_reg(did):
    logger.debug('4 - sd:1 sends an implicit invitation to O:1 to establish a connection with the goal c2dt.consortium.registerdevice?'+str(did))
    total_execution_time=runners.smartdevice.establish_conection_implicit_inv()
    categories.append('4')
    values.append(total_execution_time)

def step5_sd_reg():
    logger.debug('5 - O:1 sends sd:1 the Genesis VC proposal. ')
    total_execution_time=runners.oemv2.propose_vc()
    categories.append('5')
    values.append(total_execution_time)

def step6_sd_reg():
    logger.debug('6 - O:1 register devices into the DT ledger.  ')
    total_execution_time=runners.oemv2.register_sd_fabric()
    categories.append('6')
    values.append(total_execution_time)

def step7_sd_reg():
    total_start_time = time.time()
    logger.debug('7 - O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('7')
    values.append(0.0001)

def step8_sd_reg():
    logger.debug('8 - O:1 sends sd:1 the Genesis VC. ')
    total_execution_time=runners.oemv2.send_vc()
    categories.append('8')
    values.append(total_execution_time)

#CONSUMER BUYS DEVICE STEPS
def step1_cons_buy_dev():
    total_start_time = time.time()
    logger.debug('1 - Alice searches the Marketplace App  ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('1')
    values.append(0.0001)

def step2_cons_buy_dev():
    total_start_time = time.time()
    logger.debug('2 - Alice taps the “buy” button that is associated with the OEM’s OOB URI and the goal c2dt.consortium.buydevice which open’s Alice’s mobile wallet (for simplification we are omitting Alice’s mediator agent). ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_cons_buy_dev():
    logger.debug('3 - A:1 send the OOB URI to O:1. ')
    total_execution_time=runners.alice.oob_with_goalcode()
    categories.append('3')
    values.append(total_execution_time)

def step4_cons_buy_dev():
    logger.debug('4 - O:1 recognizes the A:1 wants to buy device and proposes the Ownership VC along with the price. ')
    total_execution_time=runners.oemv2.propose_vc()
    categories.append('4')
    values.append(total_execution_time)

def step5_cons_buy_dev():
    logger.debug('5 - Alice accepts the VC offer and initiates the payment subprocess which will transfer the necessary funds from Alice to the OEM (out-of-scope). ')
    total_execution_time=runners.alice.accept_vc_and_pay()
    categories.append('5')
    values.append(total_execution_time)

def step6_cons_buy_dev():
    logger.debug('6 - O:1 makes an update to the DT ledger indicating that the device is “In-Transit”.  ')
    total_execution_time=runners.oemv2.update_device()
    categories.append('6')
    values.append(total_execution_time)


#CLAIM EDGE GATEWAY STEPS
def step1_claim_egw():
    total_execution_time=runners.gatewayv2.deploy_ditto()
    os.chdir("/home/pedro/Desktop/Aries-Agents/Masters-v2/Gateway")
    command = 'python3 initGateway.py'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    total_start_time = time.time()
    logger.debug('1 - A:1 scans the EGW’s OOB QR code which has associated the goal code c2dt.consortium.claim. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('1')
    values.append(0.0001)
    
def step2_claim_egw():
    logger.debug('2 - A:1 establishes a connection with egw:1. ')
    total_execution_time=runners.alice.establish_conection_oob_inv()
    categories.append('2')
    values.append(total_execution_time)

def step3_claim_egw():
    logger.debug('3 - egw:1 requests A:1 EGW Ownership VC proof. ')
    total_execution_time=runners.gatewayv2.request_vc()
    categories.append('3')
    values.append(total_execution_time)


def step4_claim_egw():
    logger.debug('4 - A:1 submits proof which includes the EGW’s public DID and compares it with is own Genesis VC. ')
    total_execution_time=runners.alice.proof_vc()
    categories.append('4')
    values.append(total_execution_time)

def step5_claim_egw():
    logger.debug('5 - egw:1 updates the device status on the DT Ledger setting the EGW state to “CLAIMED”. ')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('5')
    values.append(total_execution_time)


#CLAIM SMART DEVICE STEPS
def step1_claim_sd():
    logger.debug('1 - B:1 requests the menu actions from egw:1. ')
    total_execution_time=runners.dave.request_menu_actions()
    categories.append('1')
    values.append(total_execution_time)

def step2_claim_sd():
    total_start_time = time.time()
    logger.debug('2 - B:1 selects “Claim Smart Device”. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_claim_sd():
    logger.debug('3 - egw:1 requests SD Ownership VC proof. ')
    total_execution_time=runners.gatewayv2.request_vc()
    categories.append('3')
    values.append(total_execution_time)

def step4_claim_sd():
    logger.debug('4 - A:1 sends presentation with Device ID. ')
    total_execution_time=runners.alice.proof_vc()
    categories.append('4')
    values.append(total_execution_time)

def step5_claim_sd():
    logger.debug('5 - egw:1 initiates a transaction which associates the Device ID to the “claim device” action. ')
    total_execution_time=runners.gatewayv2.claim_transaction()
    categories.append('5')
    values.append(total_execution_time)

def step6_claim_sd():
    total_start_time = time.time()
    logger.debug('6 - B:1 scans the SD QR code which has associated the goal c2dt.consortium.claim. ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('6')
    values.append(0.0001)

def step7_claim_sd():
    logger.debug('7 - B:1 creates a connection with sd:1 ')
    total_execution_time=runners.bob.establish_conection_oob_inv()
    categories.append('7')
    values.append(total_execution_time)

def step8_claim_sd():
    total_start_time = time.time()
    logger.debug('8 - Based on the goal code sd:1 requests EGW’s standing invitation. ')
    time.sleep(0.612)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time}\n{RESET}")
    categories.append('8')
    values.append(total_execution_time)

def step9_claim_sd():
    total_start_time = time.time()
    logger.debug('9 - B:1 sends EGW standing invitation. ')
    time.sleep(0.571)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time}\n{RESET}")
    categories.append('9')
    values.append(total_execution_time)

def step10_claim_sd():
    logger.debug('10 - B:1 uses the standing invitation to establish an implicit invitation to egw:1 passing the goal code c2dt.consortium.claim. ')
    total_execution_time=runners.bob.establish_conection_implicit_inv()
    categories.append('10')
    values.append(total_execution_time)

def step11_claim_sd():
    logger.debug('11 - egw:1 requests SD Genesis VC proof. ')
    total_execution_time=runners.gatewayv2.request_vc()
    categories.append('11')
    values.append(total_execution_time)

def step12_claim_sd():
    logger.debug('12 - B:1 submit presentation that includes device ID. ')
    total_execution_time=runners.bob.proof_vc()
    categories.append('12')
    values.append(total_execution_time)

def step13_claim_sd():
    logger.debug('13 - egw:1 sends a confirmation request to A:1 to ensure that Alice approves Bob’s SD association with EGW. (basic message exchange)')
    total_execution_time=runners.bob.proof_vc()*2
    categories.append('13')
    values.append(total_execution_time)

def step14_claim_sd():
    logger.debug('14 - egw:1 completes the transaction and associates the B:1 DID peer to the device ID. From this point onwards egw:1 knows which consumer owns what device. ')
    total_execution_time=runners.gatewayv2.owner_device_db_update()*2
    categories.append('14')
    values.append(total_execution_time)

def step15_claim_sd():
    logger.debug('15 - egw:1 updates the DT ledger and updates the controller ID to the EGW public DID, and the state to “claimed” ')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('15')
    values.append(total_execution_time)


#TWIN DEVICE STEPS
def step1_twin_sd():
    logger.debug('1 - B:1 request action menu from egw:1 ')
    total_execution_time=runners.bob.request_menu_actions()
    categories.append('1')
    values.append(total_execution_time)

def step2_twin_sd():
    total_start_time = time.time()
    logger.debug('2 - B:1 selects the “Twin” “Action Menu”')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_twin_sd():
    logger.debug('3 - egw:1 requests approval from A:1 to twin the device. ')
    total_execution_time=runners.gatewayv2.request_twin_approval()+runners.alice.approve_twin()
    categories.append('3')
    values.append(total_execution_time)

def step4_twin_sd():
    logger.debug('4 - egw:1 uploads the twinning configurations to the SD Table. ')
    total_execution_time=runners.gatewayv2.owner_device_db_update()
    categories.append('4')
    values.append(total_execution_time)

def step5_twin_sd():
    logger.debug('5 - egw:1 downloads the WoT file from the Consortium Git by querying the corresponding DeviceModelID from the SD Table (which is stored during the “SD claim”). ')
    total_execution_time=runners.gatewayv2.get_wot_file_github()
    categories.append('5')
    values.append(total_execution_time)

def step6_twin_sd():
    logger.debug('6 - egw:1 starts Eclipse Ditto server and deploys the SD DT using the WoT file and creates the Ditto Topic UUID, and creates a topic. ')
    total_execution_time=runners.gatewayv2.deploy_ditto()
    os.chdir("/home/pedro/Desktop/Aries-Agents/Masters-v2/SmartDevice")
    command = 'python3 initSD.py'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    categories.append('6')
    values.append(total_execution_time)

def step7_twin_sd():
    logger.debug('7 - egw:1 sends a message to sd:1 to start streaming data which includes the MQTT topic. ')
    total_execution_time=runners.gatewayv2.start_transaction()
    categories.append('7')
    values.append(total_execution_time)

def step8_twin_sd():
    total_start_time = time.time()
    logger.debug('8 - sd:1 needs to configure the MQTT Client. ')
    time.sleep(0.483)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time} \n{RESET}")
    categories.append('8')
    values.append(total_execution_time)

def step9_twin_sd():
    logger.debug('9 - egw:1 updates the state of the SD to “Twined”. ')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('9')
    values.append(total_execution_time)


#UNTWIN DEVICE STEPS
def step1_untwin_sd():
    logger.debug('1 - B:1 request action menu from egw:1 ')
    total_execution_time=runners.bob.request_menu_actions()
    categories.append('1')
    values.append(total_execution_time)

def step2_untwin_sd():
    total_start_time = time.time()
    logger.debug('2 - B:1 selects the “Twin” “Action Menu”')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A)\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_untwin_sd():
    logger.debug('3 - egw:1 sends a message to sd:1 to stop streaming data ')
    total_execution_time=runners.gatewayv2.stop_transmission()
    categories.append('3')
    values.append(total_execution_time)

def step4_untwin_sd():
    total_start_time = time.time()
    logger.debug('4 - egw:1 update the Device Table and removes the asset being untwined ')
    time.sleep(0.315)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time}\n{RESET}")
    categories.append('4')
    values.append(total_execution_time)

def step5_untwin_sd():
    logger.debug('5 - egw:1 deletes the twin ')
    total_execution_time=runners.gatewayv2.close_connection()
    categories.append('5')
    values.append(total_execution_time)

def step6_untwin_sd():
    total_start_time = time.time()
    logger.debug('6 - egw:1 based on the untwin configurations may or not remove data from IPFS ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\t{total_execution_time} (!!!)\n{RESET}")
    categories.append('6')
    values.append(total_execution_time)

def step7_untwin_sd():
    logger.debug('7 - egw:1 updates the DTE ledger.')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('7')
    values.append(total_execution_time)


#SELL DEVICE
def step1_sell_sd():
    logger.debug('1 - B:1 request action menu from egw:1 ')
    total_execution_time=runners.bob.request_menu_actions()
    categories.append('1')
    values.append(total_execution_time)

def step2_sell_sd():
    total_start_time = time.time()
    logger.debug('2 - B:1 selects the “Sell SD”')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('2')
    values.append(0.0001)

def step3_sell_sd():
    logger.debug('3 - egw:1 requests action menu from C:1. ')
    total_execution_time=runners.gatewayv2.request_menu_actions()
    categories.append('3')
    values.append(total_execution_time)

def step4_sell_sd():
    total_start_time = time.time()
    logger.debug('4 - egw:1 selects action to sell ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('4')
    values.append(0.0001)

def step5_sell_sd():
    total_start_time = time.time()
    logger.debug('5 - C:1 updates the eCommerce site with the price and sale information ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('5')
    values.append(0.0001)

def step6_sell_sd():
    total_start_time = time.time()
    logger.debug('6 - Charlie browses the eCommerce site and devices to buy Bob’s device ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('6')
    values.append(0.0001)

def step7_sell_sd():
    total_start_time = time.time()
    logger.debug('7 - Charlie taps the buy button which is associated with the buy OOB URI that opens Charlie’s mobile wallet ')
    time.sleep(1)
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\tN/A\n{RESET}")
    categories.append('7')
    values.append(0.0001)

def step8_sell_sd():
    logger.debug('8 - CA:1 establishes a connection with egw:1 ')
    total_execution_time=runners.charlie.establish_conection_oob_inv()
    categories.append('8')
    values.append(total_execution_time)

def step9_sell_sd():
    logger.debug('9 - egw:1 uses the goal “buy device” to propose the Ownership VC ')
    total_execution_time=runners.gatewayv2.propose_vc()
    categories.append('9')
    values.append(total_execution_time)


def step10_sell_sd():
    logger.debug('10 - egw:1 sends the previous owner of the SD to revoke the previous ownership credential after the payment is exchanged egw:1.  ')
    total_execution_time=runners.gatewayv2.ask_to_revoke_cred()
    categories.append('10')
    values.append(total_execution_time)

def step11_sell_sd():
    logger.debug('11 - egw:1 creates the ownership credential and sends it to CA:1 ')
    total_execution_time=runners.gatewayv2.send_vc()
    categories.append('11')
    values.append(total_execution_time)

def step12_sell_sd():
    logger.debug('12 - egw:1 updates the asset record to “IN-TRANSIT” ')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('11')
    values.append(total_execution_time)

def step13_sell_sd():
    logger.debug('13 - After Charlie receives the device, he uses EGW #2 to claim and eventually twin the device once more ')
    total_execution_time=runners.gatewayv2.update_device_fabric()
    categories.append('13')
    values.append(total_execution_time)


#DEPLOY AGENTS
def deploy_agents(num_dots, agent):
    for _ in range(num_dots):
        time.sleep(1)  # Pause for 1 second
        print(".", end="")

#DEPLOY FABRIC NETWORK
def deploy_fabric_network(num_dots):
    total_start_time = time.time()
    print("Deploying Fabric Network", end="")
    for _ in range(num_dots):
        time.sleep(1)  # Pause for 1 second
        print(".", end="")
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\n\t{total_execution_time}\n{RESET}")

#DEPLOY VON NETWORK
def deploy_von_network(num_dots):
    random_number = round(random.uniform(0, 1), 3)
    total_start_time = time.time()
    print("Deploying Von Network", end="")
    for _ in range(num_dots):
        time.sleep(1)  # Pause for 1 second
        print(".", end="")
    total_end_time = time.time()
    total_execution_time = round(total_end_time - total_start_time, 3)
    print(f"{GREEN}\n\t{total_execution_time}\n{RESET}")

def generate_id():
    id_length = 20
    random_chars = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(random_chars, k=id_length))
    id_like = f'V4SGRU{random_id}'
    return id_like

def run_consortium():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run consortium'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_oem():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run oemv2'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dave():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run dave'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_egw():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run gatewayv2'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_sd():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run smartdevice'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_alice():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run alice'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_alice():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run alice'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_bob():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run bob'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_charlie():
    os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run charlie'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def c_1_admin_api_call():
    time.sleep(60)
    url = 'http://0.0.0.0:8081/connections/create-invitation?auto_accept=true'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "metadata": {},
        "my_label": "Bob",
        "recipient_keys": [
            "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        ],
        "routing_keys": [
            "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        ],
        "service_endpoint": "http://192.168.56.102:8020"
    }

    response = requests.post(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 200:
        print("Request successful.")
        print(response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

def run_fabric():
    os.chdir("/home/pedro/Desktop/Aries-Agents/Masters-v2/Fabric/fabric-network-cc")
    init_fabric_process = subprocess.Popen(['python3', 'deploy_fabric.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_ipfs():
    try:
        subprocess.run(["ipfs-desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("IPFS Desktop executable not found. Make sure it is installed and in your system's PATH.")


def wait_for_agents_deploy():
    print("Waiting for fabric, ipfs and agents been deployed")
    agents = ["ipfs", "consortium", "oem", "dave", "egw", "sd", "alice", "bob", "charlie", "fabric"]
    for agent in agents:
        for _ in range(10):
            time.sleep(1)  # Pause for 1 second
            print("\r.", end="")
        print("\r" + agent + " deployed\n", end="")
    time.sleep(30)


def print_bold(text):
    print("\033[1m" + text + "\033[0m")

def use_case1():
    print_bold("USE CASE 1 - OEM ENROLLMENT PHASE 1")


def main():
    logger.debug('Removing all docker containers')
    try:
        # Get the list of all running container IDs using 'docker ps -a -q'
        containers = subprocess.check_output(['docker', 'ps', '-a', '-q']).decode().strip().split('\n')

        if not containers:
            print("No running containers found.")
            return

        # Stop each container one by one
        for container in containers:
            stop_command = "docker stop $(docker ps -a -q)"
            subprocess.run(stop_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            rm_command = "docker rm $(docker ps -a -q)"
            subprocess.run(rm_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("")

    #deploy IPFS
    logger.debug('Deploying IPFS local node')
    os.chdir("IPFSDeployment")
    command = 'python3 deploy_ipfs.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    #deploy Fabric Network
    logger.debug('Deploying Fabric Network')
    os.chdir("../FabricDeployment")
    command = 'python3 deploy_fabric.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    #deploy agents
    logger.debug('Deploying Aries Agents')
    os.chdir("../AgentsDeployment")
    command = 'python3 deploy_agents.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("All containers deployed")

    oem_enrollment1()



    #USE CASE 2
    oem_enrollment2()
    
    #USE CASE 3
    dev_mode_reg()
    
    #USE CASE 4
    egw_reg()
    
    #USE CASE 5
    sd_reg()
    
    #USE CASE 6
    consumer_buys_device()
    
    #USE CASE 7
    claim_egw()
    
    #USE CASE 8
    claim_sd()
    
    #USE CASE 9
    twin_sd()
    
    #USE CASE 10
    untwin_sd()
    
    #USE CASE 11
    sell_sd()
    


if __name__ == "__main__":
    main()
