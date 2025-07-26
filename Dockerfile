# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers for web scraping
RUN playwright install --with-deps chromium

# Copy the rest of the application's code to the working directory
COPY . .

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Command to run the application
# Uvicorn is a lightning-fast ASGI server, recommended for FastAPI
# Remove --reload for production deployment
# Use PORT environment variable for Cloud Run compatibility
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
