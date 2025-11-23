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
        
        # Simula segredo DH (para simplificar laboratório)
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
