from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI(title="E-Commerce ML API")

class RunRequest(BaseModel):
    run_training: bool = True

@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/run")
def run_model(request: RunRequest):
    """
    Runs your existing main.py without modifying it
    """
    if request.run_training:
        result = subprocess.run(
            ["python", "main.py"],
            capture_output=True,
            text=True
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    return {"message": "Nothing executed"}

