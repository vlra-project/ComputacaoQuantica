import rsa

# 1) Gerar par de chaves (512 bits para exemplo; use >= 2048 bits na prática)
public_key, private_key = rsa.newkeys(2048)

# 2) Mensagem a ser criptografada
mensagem = "Texto secreto para criptografia"
print("Mensagem original:", mensagem)

# 3) Criptografar usando a chave pública
mensagem_bytes = mensagem.encode('utf-8')
mensagem_criptografada = rsa.encrypt(mensagem_bytes, public_key)
print("\nMensagem criptografada (hex):", mensagem_criptografada.hex())

# 4) Descriptografar usando a chave privada
mensagem_decriptada = rsa.decrypt(mensagem_criptografada, private_key)
print("\nMensagem decriptada:", mensagem_decriptada.decode('utf-8'))

# 5) Opcional: salvar as chaves em arquivos
with open("public.pem", "wb") as pub_file:
    pub_file.write(public_key.save_pkcs1())

with open("private.pem", "wb") as priv_file:
    priv_file.write(private_key.save_pkcs1())

print("\nChaves salvas em 'public.pem' e 'private.pem'")
