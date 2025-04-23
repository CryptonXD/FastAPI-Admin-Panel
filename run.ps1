# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Output "Virtual environment created."
}

# Activate virtual environment
./.venv/Scripts/Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
