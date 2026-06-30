import random
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Chandrayaan-2 Mission Telemetry API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated state to maintain continuity between polls
state = {
    "cpr": 1.24,
    "dop": 0.09,
    "temp": 40.0,
    "prob": 99.4
}

@app.get("/api/telemetry")
async def get_telemetry():
    """
    Returns real-time telemetry data simulating the continuous processing
    of DFSAR radar frames and Diviner thermal data.
    """
    # Simulate processing delay
    await asyncio.sleep(0.1)
    
    # Introduce random walk variance to simulate real data fluctuations
    state["cpr"] = max(0.5, min(2.0, state["cpr"] + (random.random() - 0.5) * 0.1))
    state["dop"] = max(0.01, min(0.25, state["dop"] + (random.random() - 0.5) * 0.02))
    state["temp"] = max(20.0, min(100.0, state["temp"] + (random.random() - 0.5) * 2.0))
    state["prob"] = max(85.0, min(100.0, state["prob"] + (random.random() - 0.5) * 0.5))
    
    # Check alert threshold based on 01_radar_polarimetry.py logic
    # CPR > 1.0 & DOP < 0.13 indicates ICE
    alert_triggered = state["cpr"] > 1.0 and state["dop"] < 0.13
    
    return {
        "status": "success",
        "data": {
            "cpr_value": state["cpr"],
            "dop_value": state["dop"],
            "temperature_k": state["temp"],
            "ice_probability": state["prob"],
            "alert_triggered": alert_triggered
        }
    }

if __name__ == "__main__":
    print("--- BOOTING FASTAPI TELEMETRY SERVER ---")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
