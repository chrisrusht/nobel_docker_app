# Use the official Python image
FROM python:latest

# Expose port 8000 for the Python application
EXPOSE 8000

# Copy the app directory into the container
COPY app /app

# Set the working directory to /app
WORKDIR /app

# Install the dependencies
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "app.py"]