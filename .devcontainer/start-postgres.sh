#!/usr/bin/env bash
set -uo pipefail

compose_file="docker-compose.yml"
service_name="db"

for i in {1..30}; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker info >/dev/null 2>&1; then
  echo "Docker-in-Docker daemon is not ready yet. You can start PostgreSQL later with: docker compose up -d db"
  exit 0
fi

if ! docker compose -f "$compose_file" up -d "$service_name"; then
  echo "PostgreSQL compose startup did not finish cleanly. You can retry with: docker compose up -d db"
  exit 0
fi

for i in {1..60}; do
  if docker compose -f "$compose_file" exec -T "$service_name" pg_isready -U postgres >/dev/null 2>&1; then
    echo "PostgreSQL is ready in Docker-in-Docker."
    exit 0
  fi
  sleep 1
done

echo "PostgreSQL container started, but readiness check timed out. Check it with: docker compose ps"
exit 0
