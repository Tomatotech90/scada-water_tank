# Use the official Python image as the base image
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app and dashboard files into the container
COPY app.py dashboard.html /app/

# Expose the port the app runs on
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]
