FROM python:3.12.1-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .



# Expose the port the app runs on
EXPOSE 80

# Command to run the application
CMD ["python", "run.py"]