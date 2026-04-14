# Use a lightweight Python image as the base environment
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /apps

# Copy dependency list first so Docker can cache this layer
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the container
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Start the application when the container runs
CMD ["python", "-m", "app.main"]