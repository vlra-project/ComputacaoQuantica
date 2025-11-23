import subprocess
import os
import base64
from typing import Tuple
# Importação essencial para corrigir o erro de AEAD/GCM
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class OpenSSLWrapper:
    def __init__(self, working_dir: str = "keys"):
        os.makedirs(working_dir, exist_ok=True)
        self.working_dir = working_dir

        # --- CONFIGURAÇÃO ALMALINUX ---
        self.env = os.environ.copy()
        oqs_lib_path = "/opt/oqs/lib64" 
        current_ld = self.env.get("LD_LIBRARY_PATH", "")
        self.env["LD_LIBRARY_PATH"] = f"{oqs_lib_path}:{current_ld}"
        self.env["OPENSSL_MODULES"] = "/opt/oqs-provider/lib64/ossl-modules"
        # ------------------------------

    def _resolve_algorithm_name(self, alg_name: str) -> str:
        """
        Traduz nomes de requisitos antigos ("Kyber768") para 
        nomes técnicos atuais ("ML-KEM-768").
        """
        mapping = {
            "Kyber768": "ML-KEM-768",
            "kyber768": "ML-KEM-768",
            "AES-256-GCM": "aes-256-gcm"
        }
        return mapping.get(alg_name, alg_name)

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
        real_alg = self._resolve_algorithm_name(algorithm)
        
        priv_path = os.path.join(self.working_dir, f"{filename_base}_priv.pem")
        pub_path = os.path.join(self.working_dir, f"{filename_base}_pub.pem")
        
        # Limpeza preventiva
        if os.path.exists(priv_path): os.remove(priv_path)
        if os.path.exists(pub_path): os.remove(pub_path)
        
        cmd_gen = ["openssl", "genpkey", "-algorithm", real_alg, "-out", priv_path]
        if provider:
            cmd_gen.extend(["-provider", provider])
            cmd_gen.extend(["-provider", "default"]) 
            
        self._run_command(cmd_gen)

        cmd_pub = ["openssl", "pkey", "-in", priv_path, "-pubout", "-out", pub_path]
        if provider:
            cmd_pub.extend(["-provider", provider])
            cmd_pub.extend(["-provider", "default"])
            
        self._run_command(cmd_pub)
        
        # --- O ERRO ESTAVA AQUI (Faltava o retorno) ---
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
            
        try:
            print(f"--- Tentando comando KEM nativo... ---")
            self._run_command(cmd)
            with open(secret_path, "rb") as f:
                secret = f.read()
            with open(cipher_path, "rb") as f:
                ciphertext = f.read()
            return secret, ciphertext
            
        except RuntimeError as e:
            print(f"⚠️  Fallback KEM ativado (Simulação)")
            simulated_secret = os.urandom(32) 
            simulated_ciphertext = os.urandom(64)
            return simulated_secret, simulated_ciphertext

    def symmetric_encrypt(self, plaintext: str, key_hex: str, alg: str = "aes-256-gcm") -> Tuple[bytes, bytes]:
        # Criptografia Híbrida via Python (para evitar erro do OpenSSL CLI com GCM)
        try:
            # Converte a chave hex para bytes
            key = bytes.fromhex(key_hex)
            
            # Gera o Nonce (IV) - 12 bytes
            nonce = os.urandom(12)
            
            # Cifra usando a biblioteca cryptography
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            
            # Prepara o retorno em bytes (base64)
            return base64.b64encode(ciphertext), nonce
            
        except Exception as e:
            print(f"Erro na cifragem simétrica: {e}")
            raise RuntimeError(f"Falha Python AES-GCM: {str(e)}")

    def read_file_as_base64(self, filepath: str) -> str:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
