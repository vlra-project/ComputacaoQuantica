import subprocess
import os
import base64
from typing import Tuple

class OpenSSLWrapper:
    def __init__(self, working_dir: str = "keys"):
        os.makedirs(working_dir, exist_ok=True)
        self.working_dir = working_dir

        # --- CONFIGURAÇÃO MANUAL (ALMALINUX FIX) ---
        self.env = os.environ.copy()
        
        # Caminhos fixos baseados na nossa instalação manual
        # Garante que o Python ache a liboqs e o provider
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
                env=self.env # Injeta o ambiente corrigido
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
        
        # Nota: OpenSSL enc para GCM via pipe requer cuidado, mas segue a spec do projeto
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
