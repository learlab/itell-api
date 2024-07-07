#!/bin/bash

# Make the script executable with
# chmod +x tests/performance/start_swarm.sh

URL="http://127.0.0.1:8001"
RETRIES=60
count=0

# Function to clean up background process
cleanup() {
    echo "Cleaning up..."
    kill $ITELL_AI_PID 2>/dev/null
    wait $ITELL_AI_PID 2>/dev/null
}

# Ensure cleanup on script exit
trap cleanup EXIT

# Start the Uvicorn server
python -m src.app &
ITELL_AI_PID=$!

# Wait for the Uvicorn serer to start up
until $(curl --output /dev/null --silent --fail $URL); do
    count=$((count+1))
    if [ $count -eq 1 ]; then
        echo "Waiting for server to start at $URL..."
    fi
    if [ $count -ge $RETRIES ]; then
        echo "Server did not start within $RETRIES seconds. Exiting."
        cleanup
        exit 1
    fi
    sleep 1
done

# Start Locust
echo "Uvicorn server is up and running. Starting Locust..."
locust -f tests/performance/swarm.py

# Wait for Uvicorn server to finish before exiting script
wait $ITELL_AI_PID