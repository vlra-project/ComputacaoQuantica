import json
import os
import base64
from typing import List
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from .openssl_utils import OpenSSLWrapper

class HybridEncryptor:
    def __init__(self, policy_path="policy/policy_pqc.json"):
        with open(policy_path, 'r') as f:
            self.policy = json.load(f)
        self.openssl = OpenSSLWrapper()

    # --- ENCRIPTAÇÃO MODULAR ---
    def run_hybrid_encryption(self, plaintext_message: str, modules: List[str]):
        """
        modules: lista de strings, ex: ["rsa"], ["kyber", "rsa"], ["all"]
        """
        
        # Normaliza a entrada (lowercase)
        active_modules = [m.lower() for m in modules]
        if "all" in active_modules:
            active_modules = ["kyber", "x25519", "rsa"]

        # Estruturas para acumular os segredos e as chaves públicas
        collected_secrets = b""
        keys_output = {
            "Kyber": {"public_key": None, "ciphertext": None},
            "X25519": {"public_key": None, "ephemeral_share": None},
            "RSA": {"public_key": None, "encapsulated_secret": None}
        }

        print(f"--- Iniciando Criptografia Modular: {active_modules} ---")

        # 1. Módulo Kyber (ML-KEM)
        if "kyber" in active_modules:
            print(">>> Ativando Kyber")
            pqc_priv, pqc_pub = self.openssl.generate_keypair(self.policy['kem'], "pqc", self.policy.get('provider'))
            pqc_secret, pqc_ciphertext = self.openssl.kem_encapsulate(pqc_pub, self.policy.get('provider'))
            
            collected_secrets += pqc_secret
            keys_output["Kyber"] = {
                "public_key": self.openssl.read_file_as_base64(pqc_pub),
                "ciphertext": base64.b64encode(pqc_ciphertext).decode('utf-8')
            }

        # 2. Módulo X25519 (Só ativamos se houver RSA para transportar o segredo nesta demo)
        # Nota: Em produção real, usariamos ECIES, mas aqui dependemos do RSA como envelope.
        dh_secret = b""
        if "x25519" in active_modules:
            print(">>> Ativando X25519")
            dh_priv, dh_pub = self.openssl.generate_keypair(self.policy['dh'], "dh")
            dh_secret = os.urandom(32) # Segredo simulado
            
            # Não adicionamos ao collected_secrets agora, pois ele será somado dentro do envelope RSA
            # Se não tiver RSA, o X25519 fica "órfão" nesta arquitetura de mensagem única.
            keys_output["X25519"]["public_key"] = self.openssl.read_file_as_base64(dh_pub)
            keys_output["X25519"]["ephemeral_share"] = "protected-inside-rsa"

        # 3. Módulo RSA
        if "rsa" in active_modules:
            print(f">>> Ativando RSA-{self.policy.get('rsa_bits', '3072')}")
            rsa_priv, rsa_pub = self.openssl.generate_rsa_keypair(self.policy.get('rsa_bits', '3072'), "rsa")
            rsa_secret = os.urandom(32)
            
            # Payload a ser cifrado pelo RSA: Segredo RSA + Segredo DH (se existir)
            payload_to_wrap = rsa_secret + dh_secret
            rsa_ciphertext = self.openssl.rsa_encrypt_secret(rsa_pub, payload_to_wrap)

            collected_secrets += payload_to_wrap # Adiciona ambos ao segredo mestre
            
            keys_output["RSA"] = {
                "public_key": self.openssl.read_file_as_base64(rsa_pub),
                "encapsulated_secret": base64.b64encode(rsa_ciphertext).decode('utf-8')
            }
        
        # Validação de Segurança
        if not collected_secrets:
            raise ValueError("Nenhum módulo de criptografia foi selecionado ou válido!")

        # 4. Derivação da Chave Mestra (HKDF)
        # O HKDF aceita qualquer tamanho de input, então funciona com 1, 2 ou 3 segredos somados.
        print("--- Derivando Chave Mestra Variável ---")
        symmetric_key_hex = self._derive_key(collected_secrets)

        # 5. Cifragem Simétrica
        encrypted_data_b64, iv_bytes = self.openssl.symmetric_encrypt(plaintext_message, symmetric_key_hex)

        return {
            "algorithm": f"Modular-Hybrid ({'+'.join(active_modules).upper()})",
            "ciphertext": encrypted_data_b64.decode('utf-8'),
            "iv": base64.b64encode(iv_bytes).decode('utf-8'),
            "tag": "embedded",
            "keys": keys_output
        }

    # --- DECRIPTAÇÃO INTELIGENTE ---
    def run_hybrid_decryption(self, payload: dict):
        keys_data = payload.get("keys", {})
        collected_secrets = b""

        # 1. Tenta recuperar Kyber
        if keys_data.get("Kyber") and keys_data["Kyber"].get("ciphertext"):
            print(">>> Decifrando camada Kyber")
            pqc_ct = base64.b64decode(keys_data["Kyber"]["ciphertext"])
            pqc_secret = self.openssl.kem_decapsulate(pqc_ct, "pqc_priv.pem", self.policy.get('provider'))
            collected_secrets += pqc_secret

        # 2. Tenta recuperar RSA (e X25519 carona)
        if keys_data.get("RSA") and keys_data["RSA"].get("encapsulated_secret"):
            print(">>> Decifrando camada RSA")
            rsa_ct = base64.b64decode(keys_data["RSA"]["encapsulated_secret"])
            decrypted_blob = self.openssl.rsa_decrypt_secret("rsa_priv.pem", rsa_ct)
            # O blob contém RSA_SECRET + DH_SECRET (se houver)
            # Como só concatenamos na ida, na volta adicionamos o blob inteiro ao segredo mestre
            collected_secrets += decrypted_blob

        if not collected_secrets:
            raise ValueError("Não foi possível recuperar nenhuma chave válida do payload.")

        # 3. Reconstrói a chave
        symmetric_key_hex = self._derive_key(collected_secrets)

        # 4. Decifra
        plaintext = self.openssl.symmetric_decrypt(
            payload["ciphertext"], 
            symmetric_key_hex, 
            payload["iv"]
        )
        
        return {"decrypted_message": plaintext, "status": "Success"}

    def _derive_key(self, secret: bytes) -> str:
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'hybrid-modular-v1')
        return hkdf.derive(secret).hex()
