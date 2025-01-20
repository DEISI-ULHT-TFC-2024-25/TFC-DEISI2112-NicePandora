FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
	redis-tools \
    && rm -rf /var/lib/apt/lists/*

	

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install pip==23.0.1 && pip install -r requirements.txt

#RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . .

# Copy the start script and ensure it is executable
COPY ./docker/start /start
RUN chmod +x /start

# Define the default command
ENTRYPOINT ["/start"]
