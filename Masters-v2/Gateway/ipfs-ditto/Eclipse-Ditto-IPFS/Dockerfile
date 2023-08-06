# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file first to leverage Docker cache
COPY . .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py and helper.py files into the container
COPY app.py .
COPY helper.py .

# Run the app.py file
CMD ["python", "app.py"]
