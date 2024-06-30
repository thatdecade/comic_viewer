# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV COMIC_SETTINGS_PATH=/mnt/settings
ENV COMIC_USERS_DB_PATH=/mnt/db
ENV COMIC_VIEWER_PATH=/mnt/comics

# Create necessary directories
RUN mkdir -p /mnt/settings /mnt/db /mnt/comics

# Run flask when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
