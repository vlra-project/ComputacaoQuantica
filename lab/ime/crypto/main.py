from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from crypto.encryptor import HybridEncryptor
import traceback

app = FastAPI(title="PQC Modular Server")

# --- Modelos de Dados ---
class KeyDetail(BaseModel):
    public_key: Optional[str] = None
    ciphertext: Optional[str] = None
    encapsulated_secret: Optional[str] = None
    ephemeral_share: Optional[str] = None

class AlgorithmKeys(BaseModel):
    Kyber: Optional[KeyDetail] = None
    X25519: Optional[KeyDetail] = None
    RSA: Optional[KeyDetail] = None

class EncryptionResponse(BaseModel):
    algorithm: str
    ciphertext: str
    iv: str
    tag: str
    keys: AlgorithmKeys

class PlaintextRequest(BaseModel):
    data: str
    # O usuário pode passar ["rsa"], ["kyber"], ou ["all"]
    modules: List[str] = Field(default=["kyber", "rsa"], description="Lista de módulos: 'rsa', 'kyber', 'x25519'")

# --- Endpoints ---

@app.post("/encrypt", response_model=EncryptionResponse)
async def encrypt_endpoint(payload: PlaintextRequest):
    try:
        encryptor = HybridEncryptor()
        # Passamos a lista de módulos escolhidos pelo usuário
        return encryptor.run_hybrid_encryption(payload.data, payload.modules)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt")
async def decrypt_endpoint(payload: EncryptionResponse):
    try:
        encryptor = HybridEncryptor()
        return encryptor.run_hybrid_decryption(payload.dict())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Decryption Failed: " + str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3030, timeout_keep_alive=30)
