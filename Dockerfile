# Use an official Python base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y nano && \
    pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of your project's source code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5005

# Define environment variable
ENV FLASK_APP=app.py

# Run your application when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5005"]



