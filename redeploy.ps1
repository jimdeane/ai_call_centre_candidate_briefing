Write-Host "Stopping and removing old container..."
docker compose down

Write-Host "Rebuilding and starting fresh..."
docker compose up --build -d

Write-Host "✅ Questionnaire app deployed and running on http://localhost:5000"
