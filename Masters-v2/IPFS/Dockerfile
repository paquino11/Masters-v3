# Use nginx as the base image
FROM nginx:latest

# Install Python 3, python3-venv, and other necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip curl

RUN curl -fsSL https://github.com/ipfs/go-ipfs/releases/download/v0.10.0/go-ipfs_v0.10.0_linux-amd64.tar.gz | tar xz

RUN mv go-ipfs/ipfs /usr/local/bin
RUN rm -rf go-ipfs

# Copy the application files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Create a virtual environment and activate it
RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install ipfshttpclient inside the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir ipfshttpclient

# Install the required Python packages from requirements.txt inside the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Expose port 5001
EXPOSE 5001

# Command to run your application
CMD ["/bin/bash", "-c", "source .env && ipfs daemon --init"]
