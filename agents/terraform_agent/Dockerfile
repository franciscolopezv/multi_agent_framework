# Dockerfile.kafka_agents
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set default entrypoint (overridden per service)
CMD ["python", "terraform_agent_service.py"]
