# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV COMIC_SETTINGS_PATH=/mnt/settings/settings.json
ENV COMIC_USERS_DB_PATH=/mnt/db
ENV COMIC_VIEWER_PATH=/mnt/comics

# Run gunicorn when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "comic_web:app"]
