#!/bin/sh
set -e

# Load OPENAI_API_KEY from AWS SSM Parameter Store
if aws ssm get-parameter --name "/claims/env/OPENAI_API_KEY" --with-decryption --query "Parameter.Value" --output text > /dev/null 2>&1; then
  export OPENAI_API_KEY="$(aws ssm get-parameter --name "/claims/env/OPENAI_API_KEY" --with-decryption --query "Parameter.Value" --output text)"
  echo "Loaded OPENAI_API_KEY from SSM"
else
  echo "Warning: OPENAI_API_KEY not found in SSM!"
fi

echo "Starting Claims Demo backend application..."
cd /app/backend
exec uv run uvicorn app:app --host 0.0.0.0 --port 8080