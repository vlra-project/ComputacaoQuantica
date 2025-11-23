from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crypto.encryptor import HybridEncryptor
import traceback
import os

app = FastAPI(title="PQC Hybrid Server")

class PlaintextRequest(BaseModel):
    data: str

@app.post("/encrypt")
async def encrypt_endpoint(payload: PlaintextRequest):
    try:
        encryptor = HybridEncryptor()
        result = encryptor.run_hybrid_encryption(payload.data)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3030)
