# Use an official Python3 runtime as a parent image
FROM python:3-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install this program's pacakge
RUN python setup.py install

# Run the program when the container launches
CMD ["aliyunoss2-autoupload"]
