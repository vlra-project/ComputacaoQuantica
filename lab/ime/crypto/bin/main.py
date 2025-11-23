from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback

# Importa nossa classe especialista que criamos na pasta crypto/
# Certifique-se de que o arquivo crypto/encryptor.py existe.
from crypto.encryptor import HybridEncryptor

app = FastAPI(title="PQC Hybrid Server")

# Modelo de dados para validação automática (Pydantic)
# Garante que o JSON de entrada tenha o campo "data"
class PlaintextRequest(BaseModel):
    data: str

@app.post("/encrypt")
async def encrypt_endpoint(payload: PlaintextRequest):
    """
    Endpoint principal que recebe texto plano e retorna
    o JSON com a criptografia híbrida (PQC + Clássica).
    """
    try:
        # 1. Instancia o motor de criptografia
        # (Isso vai ler a policy_pqc.json e preparar o wrapper do OpenSSL)
        encryptor = HybridEncryptor()
        
        # 2. Executa o fluxo completo
        # (Geração de chaves -> Encapsulamento -> Derivação -> Cifragem)
        result = encryptor.run_hybrid_encryption(payload.data)
        
        # 3. Retorna o resultado estruturado
        return result
        
    except Exception as e:
        # Em caso de erro, imprime o stack trace no terminal do servidor (útil para debug)
        print("Erro no processamento:")
        traceback.print_exc()
        
        # Retorna erro 500 para o cliente
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor na porta 3030, acessível por qualquer IP (0.0.0.0)
    # Conforme especificado no comando cURL do desafio
    uvicorn.run(app, host="0.0.0.0", port=3030)
