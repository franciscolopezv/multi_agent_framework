#!/bin/bash

# tail_all_logs.sh — Tail logs from all core and agent services for debugging

services=(
  framework-core
  terraform-agent
  kafka-expert-agent
)

echo "🔍 Tailing logs for: ${services[*]}"
echo "Press Ctrl+C to exit"

docker compose logs -f "${services[@]}"
