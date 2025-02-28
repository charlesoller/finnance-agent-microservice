FROM python:3.9-slim

WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY requirements-eb.txt .
RUN pip install --no-cache-dir -r requirements-eb.txt

# Copy application code
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]