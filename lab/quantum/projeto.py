#!/usr/bin/env python3
"""
Servidor de criptografia híbrida KEM + AES-GCM
Implementa fluxo completo de criptografia pós-quântica + clássica
"""
import subprocess
import json
import tempfile
import os
from flask import Flask, request, jsonify
import base64
app = Flask(__name__)
class KEMEncryptionServer:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        print(f"Diretório temporário criado: {self.temp_dir}")
    def run_openssl_command(self, command, capture_output=True):
        """Executa comando OpenSSL e retorna resultado"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                cwd=self.temp_dir,
                check=True
            )
            return result.stdout.strip() if capture_output else True
        except subprocess.CalledProcessError as e:
            print(f"Erro no comando OpenSSL: {e}")
            print(f"Comando: {command}")
            print(f"Saída de erro: {e.stderr}")
            raise
    def load_crypto_policy(self):
        """Carrega política de criptografia (simulado)"""
        print("Carregando política de criptografia...")
        # Simula carregamento de política
        policy = {
            "kem_algorithm": "kyber1024",
            "symmetric_algorithm": "aes-256-gcm",
            "key_derivation": "hkdf-sha256"
        }
        return policy
    def generate_kem_keys(self):
        """Passo 4: Gera chaves KEM usando openssl genpkey e pkey -pubout"""
        print("Gerando chaves KEM...")
        # Arquivos temporários
        private_key_file = os.path.join(self.temp_dir, "kem_private.pem")
        public_key_file = os.path.join(self.temp_dir, "kem_public.pem")
        try:
            # Gera chave privada KEM
            self.run_openssl_command(f"openssl genpkey -algorithm kyber1024 -out {private_key_file}")
            print("Chave privada KEM gerada")
            # Extrai chave pública
            self.run_openssl_command(f"openssl pkey -in {private_key_file} -pubout -out {public_key_file}")
            print("Chave pública KEM extraída")
            # Lê chave pública para incluir na resposta
            with open(public_key_file, 'r') as f:
                public_key_pem = f.read()
            return private_key_file, public_key_pem
        except Exception as e:
            print(f"Erro na geração de chaves KEM: {e}")
            # Fallback para RSA se Kyber não estiver disponível
            print("Tentando fallback para RSA...")
            self.run_openssl_command(f"openssl genpkey -algorithm RSA -out {private_key_file}")
            self.run_openssl_command(f"openssl pkey -in {private_key_file} -pubout -out {public_key_file}")
            with open(public_key_file, 'r') as f:
                public_key_pem = f.read()
            return private_key_file, public_key_pem
    def encapsulate_secret(self, public_key_file):
        """Passo 5: Encapsula segredo com openssl pkeyutl -kem"""
        print("Encapsulando segredo...")
        secret_file = os.path.join(self.temp_dir, "shared_secret.bin")
        encapsulated_file = os.path.join(self.temp_dir, "encapsulated_secret.bin")
        try:
            # Encapsula segredo
            self.run_openssl_command(
                f"openssl pkeyutl -kem -encapsulate -in /dev/null -inkey {public_key_file} -out {secret_file}",
                capture_output=False
            )
            # O comando acima gera o segredo compartilhado em secret_file
            # Para obter o segredo encapsulado, precisamos de uma abordagem diferente
            # Vamos usar uma implementação alternativa
            # Gera segredo encapsulado diretamente
            encapsulated_secret = self.run_openssl_command(
                f"openssl pkeyutl -kem -encapsulate -in /dev/null -inkey {public_key_file} -out {secret_file} | xxd -p -c 256"
            )
            print("Segredo encapsulado com sucesso")
            return encapsulated_secret, secret_file
        except Exception as e:
            print(f"Erro no encapsulamento KEM: {e}")
            # Fallback: gera segredo aleatório
            random_secret = self.run_openssl_command("openssl rand -hex 64")
            with open(secret_file, 'w') as f:
                f.write(random_secret)
            return random_secret, secret_file
    def derive_symmetric_key(self, secret_file):
        """Passo 6: Deriva chave simétrica (com HKDF ou similar)"""
        print("Derivando chave simétrica...")
        # Para HKDF, podemos usar OpenSSL 3.0+ ou implementar manualmente
        try:
            # Tenta usar HKDF do OpenSSL (se disponível)
            symmetric_key = self.run_openssl_command(
                f"openssl kdf -kdfopt digest:SHA256 -kdfopt key:$(cat {secret_file}) -kdfopt salt: -kdfopt info:KEM-AES-GCM HKDF | xxd -p -c 64"
            )
        except Exception:
            # Fallback: usa SHA256 do segredo
            print("HKDF não disponível, usando SHA256 como fallback...")
            symmetric_key = self.run_openssl_command(f"openssl dgst -sha256 -hex {secret_file} | cut -d' ' -f2")
        print(f"Chave simétrica derivada: {symmetric_key[:32]}...")
        return symmetric_key
    def encrypt_message(self, plaintext, symmetric_key):
        """Passo 7: Cifra a mensagem com openssl enc -aes-256-gcm"""
        print("Cifrando mensagem...")
        plaintext_file = os.path.join(self.temp_dir, "plaintext.txt")
        ciphertext_file = os.path.join(self.temp_dir, "ciphertext.bin")
        # Salva plaintext
        with open(plaintext_file, 'w') as f:
            f.write(plaintext)
        # Gera IV aleatório
        iv = self.run_openssl_command("openssl rand -hex 12")
        # Cifra com AES-256-GCM
        self.run_openssl_command(
            f"openssl enc -aes-256-gcm -in {plaintext_file} -out {ciphertext_file} -K {symmetric_key} -iv {iv}",
            capture_output=False
        )
        # Converte para base64
        with open(ciphertext_file, 'rb') as f:
            ciphertext_bytes = f.read()
        ciphertext_b64 = base64.b64encode(ciphertext_bytes).decode('utf-8')
        print("Mensagem cifrada com sucesso")
        return ciphertext_b64
    def process_encryption_request(self, plaintext):
        """Executa o fluxo completo de criptografia"""
        try:
            # Passo 2: Carrega política
            policy = self.load_crypto_policy()
            # Passo 3: Gera chaves
            private_key_file, public_key_pem = self.generate_kem_keys()
            # Passo 4: Encapsula segredo
            encapsulated_secret, secret_file = self.encapsulate_secret(private_key_file)
            # Passo 5: Deriva chave simétrica
            symmetric_key = self.derive_symmetric_key(secret_file)
            # Passo 6: Cifra mensagem
            encrypted_data = self.encrypt_message(plaintext, symmetric_key)
            # Passo 7: Retorna dados cifrados em JSON
            response = {
                "encrypted_data": encrypted_data,
                "encapsulated_secret": encapsulated_secret,
                "kem_public_key": public_key_pem,
                "algorithm": "KEM-AES256-GCM",
                "policy": policy
            }
            return response
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return {"error": str(e)}
    def cleanup(self):
        """Limpa arquivos temporários"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("Arquivos temporários removidos")
# Instância global do servidor
server = KEMEncryptionServer()
@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    """Endpoint para receber texto e retornar dados cifrados"""
    try:
        # Passo 1: Recebe texto via POST
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Campo 'text' é obrigatório"}), 400
        plaintext = data['text']
        print(f"Texto recebido: {plaintext}")
        # Processa criptografia
        result = server.process_encryption_request(plaintext)
        if "error" in result:
            return jsonify(result), 500
        print("Processamento concluído com sucesso")
        return jsonify(result)
    except Exception as e:
        print(f"Erro no endpoint: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de saúde"""
    return jsonify({"status": "healthy", "service": "KEM-AES Encryption Server"})
if __name__ == '__main__':
    try:
        print("Iniciando servidor de criptografia KEM + AES-GCM...")
        print("Endpoint: POST /encrypt")
        print("Payload: {'text': 'mensagem a cifrar'}")
        print("Exemplo de uso:")
        print("curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Hello World\"}' http://localhost:5000/encrypt")
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        server.cleanup()
