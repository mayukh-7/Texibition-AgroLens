FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose the Flask port
EXPOSE 7860

# Start the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]