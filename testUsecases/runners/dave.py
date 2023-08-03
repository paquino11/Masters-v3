import time
import random


GREEN = '\033[1;32m'
RESET = '\033[0m'

def establish_conection_oob_inv():
    random_number = round(random.uniform(0.5, 0.99), 3)
    time.sleep(random_number)
    print(f"{GREEN}\t{random_number}\n{RESET}")
    return random_number

def establish_conection_implicit_inv():
    random_number = round(random.uniform(0.5, 0.99), 3)
    time.sleep(random_number)
    print(f"{GREEN}\t{random_number}\n{RESET}")
    return random_number

def request_menu_actions():
    random_number = round(random.uniform(0.1, 0.3), 3)
    time.sleep(random_number)
    print(f"{GREEN}\t{random_number}\n{RESET}")
    return random_number

