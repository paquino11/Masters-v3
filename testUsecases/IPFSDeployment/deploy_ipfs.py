import subprocess

def run_ipfs():
    try:
        subprocess.run(["ipfs-desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("IPFS Desktop executable not found. Make sure it is installed and in your system's PATH.")

def main():
    run_ipfs()


if __name__ == "__main__":
    main()
