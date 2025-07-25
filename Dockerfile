FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY python/ .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Using uvicorn to serve the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 