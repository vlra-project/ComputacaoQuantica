import os, secrets, binascii, hashlib
import pyaes

# 1) Deriva a chave (PBKDF2-HMAC-SHA256, 200k iterações)
password = "s3cr3t*c0d3".encode()
salt = os.urandom(16)
key = hashlib.pbkdf2_hmac('sha256', password, salt, 200_000, dklen=32)
print("AES key:", binascii.hexlify(key).decode())

# 2) Gera contador inicial de 128 bits
iv_bytes = os.urandom(16)                               # 16 bytes
iv = int.from_bytes(iv_bytes, "big")

# 3) Criptografa (CTR)
plaintext = "Mensagem para criptografar".encode()
aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
ciphertext = aes.encrypt(plaintext)
print("Cifrado:", binascii.hexlify(ciphertext).decode())

# 4) Decifra (CTR)
aes2 = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
decrypted = aes2.decrypt(ciphertext)
print("Decifrado:", decrypted.decode())

# Você deve guardar: salt || iv_bytes || ciphertext
