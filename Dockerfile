FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY framework/ ./framework
COPY workflow/ ./workflow
COPY telemetry.py .

# Ensure Python sees the root project folder
ENV PYTHONPATH=/app

CMD ["python", "framework/runner/event_runner.py"]
