#!/bin/bash

# This script pre-creates required Kafka topics for local development using Bitnami Kafka + Docker

KAFKA_CONTAINER_NAME="kafka"
BROKER="localhost:9092"

TOPICS=(
  workflow.request
  workflow.step.app_designer.request
  workflow.step.terraform.request
  workflow.step.kafka.request
  workflow.step.response
  workflow.output
)

echo "🔧 Creating Kafka topics..."

for TOPIC in "${TOPICS[@]}"; do
  echo "🔹 Creating topic: $TOPIC"
  docker exec -it $KAFKA_CONTAINER_NAME kafka-topics.sh \
    --create --if-not-exists \
    --topic "$TOPIC" \
    --bootstrap-server $BROKER \
    --replication-factor 1 \
    --partitions 1

done

echo "✅ All topics created or already exist."
