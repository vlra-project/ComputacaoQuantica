#!/bin/bash

# Garante que estamos no diretório correto
echo ">>> Configurando projeto no diretório atual: $(pwd)"

# 1. Criar a estrutura de pastas (O pacote Python se chamará 'crypto' também)
mkdir -p crypto
mkdir -p policy
mkdir -p keys

# 2. Requirements
echo ">>> Criando requirements.txt..."
cat <<EOF > requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
cryptography==42.0.0
pydantic
EOF

# 3. Policy JSON
echo ">>> Criando policy/policy_pqc.json..."
cat <<EOF > policy/policy_pqc.json
{
"kem": "kyber768",
"dh": "X25519",
"symmetric": "aes-256-gcm",
"provider": "oqsprovider"
}
EOF

# 4. Pacote Python (__init__.py)
touch crypto/__init__.py

# 5. openssl_utils.py (Com os caminhos fixos do AlmaLinux que descobrimos)
echo ">>> Criando crypto/openssl_utils.py..."
cat <<EOF > crypto/openssl_utils.py
import subprocess
import os
import base64
from typing import Tuple

class OpenSSLWrapper:
    def __init__(self, working_dir: str = "keys"):
        os.makedirs(working_dir, exist_ok=True)
        self.working_dir = working_dir

        # --- CONFIGURAÇÃO ALMALINUX (Hardcoded para garantir) ---
        self.env = os.environ.copy()
        
        # Caminhos que validamos manualmente anteriormente
        oqs_lib_path = "/opt/oqs/lib64" 
        current_ld = self.env.get("LD_LIBRARY_PATH", "")
        self.env["LD_LIBRARY_PATH"] = f"{oqs_lib_path}:{current_ld}"
        
        self.env["OPENSSL_MODULES"] = "/opt/oqs-provider/lib64/ossl-modules"
        # -------------------------------------------

    def _run_command(self, cmd: list) -> bytes:
        try:
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True,
                env=self.env 
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Erro no OpenSSL CLI: {error_msg}")

    def generate_keypair(self, algorithm: str, filename_base: str, provider: str = None):
        priv_path = os.path.join(self.working_dir, f"{filename_base}_priv.pem")
        pub_path = os.path.join(self.working_dir, f"{filename_base}_pub.pem")
        
        cmd_gen = ["openssl", "genpkey", "-algorithm", algorithm, "-out", priv_path]
        if provider:
            cmd_gen.extend(["-provider", provider])
            cmd_gen.extend(["-provider", "default"]) 
            
        self._run_command(cmd_gen)

        cmd_pub = ["openssl", "pkey", "-in", priv_path, "-pubout", "-out", pub_path]
        if provider:
            cmd_pub.extend(["-provider", provider])
            cmd_pub.extend(["-provider", "default"])
            
        self._run_command(cmd_pub)
        
        return priv_path, pub_path

    def kem_encapsulate(self, pub_key_path: str, provider: str = None) -> Tuple[bytes, bytes]:
        secret_path = os.path.join(self.working_dir, "temp_kem_secret.bin")
        cipher_path = os.path.join(self.working_dir, "temp_kem_cipher.bin")
        
        cmd = [
            "openssl", "pkeyutl", "-kem_enc",
            "-inkey", pub_key_path,
            "-pubin",
            "-out", cipher_path,
            "-secret", secret_path
        ]
        
        if provider:
            cmd.extend(["-provider", provider])
            cmd.extend(["-provider", "default"])
            
        self._run_command(cmd)
        
        with open(secret_path, "rb") as f:
            secret = f.read()
        with open(cipher_path, "rb") as f:
            ciphertext = f.read()
            
        return secret, ciphertext

    def symmetric_encrypt(self, plaintext: str, key_hex: str, alg: str = "aes-256-gcm") -> Tuple[bytes, bytes]:
        iv = os.urandom(12)
        iv_hex = iv.hex()
        
        cmd = [
            "openssl", "enc", f"-{alg}",
            "-K", key_hex,
            "-iv", iv_hex,
            "-base64"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.env 
            )
            out, err = process.communicate(input=plaintext.encode('utf-8'))
            
            if process.returncode != 0:
                raise RuntimeError(f"Erro Encryption: {err.decode()}")
                
            return out.strip(), iv
            
        except Exception as e:
            raise RuntimeError(f"Falha na cifragem simétrica: {str(e)}")

    def read_file_as_base64(self, filepath: str) -> str:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
EOF

# 6. encryptor.py
echo ">>> Criando crypto/encryptor.py..."
cat <<EOF > crypto/encryptor.py
import json
import os
import base64
from cryptography.hazmat.primitives import hashes, kdf
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from .openssl_utils import OpenSSLWrapper

class HybridEncryptor:
    def __init__(self, policy_path="policy/policy_pqc.json"):
        with open(policy_path, 'r') as f:
            self.policy = json.load(f)
        self.openssl = OpenSSLWrapper()

    def run_hybrid_encryption(self, plaintext_message: str):
        print("--- [1] Gerando Chaves PQC ---")
        pqc_priv, pqc_pub = self.openssl.generate_keypair(
            self.policy['kem'], "pqc", self.policy.get('provider')
        )
        
        print("--- [2] Gerando Chaves Clássicas (DH) ---")
        dh_priv, dh_pub = self.openssl.generate_keypair(
            self.policy['dh'], "dh"
        )

        print("--- [3] Executando Encapsulamento KEM ---")
        kem_shared_secret, kem_ciphertext = self.openssl.kem_encapsulate(
            pqc_pub, self.policy.get('provider')
        )
        
        dh_simulated_secret = os.urandom(32) 

        print("--- [4] Derivando Chave Simétrica (HKDF) ---")
        combined_secret = kem_shared_secret + dh_simulated_secret
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'hybrid-encryption-simulation',
        )
        symmetric_key = hkdf.derive(combined_secret)
        symmetric_key_hex = symmetric_key.hex()

        print("--- [5] Cifrando Mensagem ---")
        encrypted_data_b64, iv_bytes = self.openssl.symmetric_encrypt(
            plaintext_message, 
            symmetric_key_hex, 
            self.policy['symmetric']
        )

        return {
            "ciphertext": encrypted_data_b64.decode('utf-8'),
            "nonce": base64.b64encode(iv_bytes).decode('utf-8'),
            "kem_ciphertext": base64.b64encode(kem_ciphertext).decode('utf-8'),
            "public_keys": {
                "pqc_pub": self.openssl.read_file_as_base64(pqc_pub),
                "dh_pub": self.openssl.read_file_as_base64(dh_pub)
            }
        }
EOF

# 7. main.py (Na raiz)
echo ">>> Criando main.py na raiz..."
cat <<EOF > main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Importação relativa: como main.py está na raiz, ele enxerga a pasta 'crypto' como pacote
from crypto.encryptor import HybridEncryptor
import traceback

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
EOF

echo ">>> TUDO PRONTO! 🚀"
echo "Execute: pip install -r requirements.txt"
echo "Depois: python3 main.py"
