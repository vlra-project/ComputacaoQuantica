import subprocess
import os
import tempfile
import base64
from flask import Flask, request, jsonify

# Importações da biblioteca de criptografia
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)

# --- Passo 2: Carregar a Política/Chave ---
# O servidor precisa da chave pública do destinatário.
RECIPIENT_PK_FILE = "recipient_pk.pem"
# A política é usar secp384r1 e AES-256-GCM.
EC_CURVE = "secp384r1"
KDF_INFO = b"aes-256-gcm-encryption"

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    try:
        # --- Passo 1: Cliente envia texto ---
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in JSON payload"}), 400
        
        plaintext = data['text'].encode('utf-8')

        # --- Passos 3-7 são executados em um diretório temporário ---
        with tempfile.TemporaryDirectory() as tmpdir:
            
            # --- Passo 4: Gerar chaves (efêmeras do remetente) ---
            ephemeral_sk_path = os.path.join(tmpdir, "ephemeral_sk.pem")
            ephemeral_pk_path = os.path.join(tmpdir, "ephemeral_pk.pem")

            # Gerar chave privada efêmera
            subprocess.run([
                "openssl", "genpkey",
                "-algorithm", "EC",
                "-pkeyopt", f"ec_paramgen_curve:{EC_CURVE}",
                "-out", ephemeral_sk_path
            ], check=True, capture_output=True)

            # Extrair chave pública efêmera
            subprocess.run([
                "openssl", "pkey",
                "-in", ephemeral_sk_path,
                "-pubout",
                "-out", ephemeral_pk_path
            ], check=True, capture_output=True)

            # --- Passo 5: "Encapsular" Segredo (Derivar Segredo Compartilhado) ---
            # Isso usa a chave privada efêmera do servidor e a chave pública
            # de longa duração do destinatário.
            shared_secret_path = os.path.join(tmpdir, "ss.bin")
            subprocess.run([
                "openssl", "pkeyutl",
                "-derive",
                "-inkey", ephemeral_sk_path,
                "-peerkey", RECIPIENT_PK_FILE,
                "-out", shared_secret_path
            ], check=True, capture_output=True)

            with open(shared_secret_path, 'rb') as f:
                shared_secret = f.read()

            # --- Passo 6: Derivar Chave Simétrica (com HKDF) ---
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,  # 32 bytes = 256 bits para AES-256
                salt=None,
                info=KDF_INFO,
                backend=default_backend()
            )
            derived_key = hkdf.derive(shared_secret)

            # --- Passo 7: Cifrar a Mensagem (com AES-256-GCM) ---
            # Usar a biblioteca de criptografia do Python é mais robusto
            # do que chamar 'openssl enc'.
            aesgcm = AESGCM(derived_key)
            iv = os.urandom(12)  # IV de 96 bits (12 bytes) é padrão para GCM
            
            # Criptografa e obtém o ciphertext + tag de autenticação
            ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)

            # Ler a chave pública efêmera para enviar ao destinatário
            with open(ephemeral_pk_path, 'r') as f:
                ephemeral_pk_str = f.read()

            # --- Passo 8: Retornar dados cifrados em JSON ---
            # Usamos Base64 para codificar dados binários para JSON
            response_data = {
                "ephemeral_public_key": ephemeral_pk_str,
                "iv": base64.b64encode(iv).decode('utf-8'),
                "ciphertext": base64.b64encode(ciphertext_with_tag).decode('utf-8')
            }
            
            return jsonify(response_data)

    except subprocess.CalledProcessError as e:
        print("Erro no OpenSSL:", e.stderr.decode())
        return jsonify({"error": "Cryptography operation failed"}), 500
    except Exception as e:
        print("Erro:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(RECIPIENT_PK_FILE):
        print(f"Erro: Arquivo da chave pública do destinatário não encontrado: {RECIPIENT_PK_FILE}")
        print("Execute os comandos 'openssl genpkey' e 'openssl pkey' primeiro.")
    else:
        app.run(debug=True, port=5000)
