from tenable.io import TenableIO
import json
# --- ATENÇÃO: Início da seção não recomendada ---
# Inserir suas chaves diretamente no código é um risco de segurança.
# Use este método com extrema cautela e apenas em ambientes controlados.
TENABLE_ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
TENABLE_SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'
# --- Fim da seção não recomendada ---


# --- 1. Conexão com a API do Tenable.io ---
try:
    tio = TenableIO(
        access_key=TENABLE_ACCESS_KEY,
        secret_key=TENABLE_SECRET_KEY
    )
    print("Conexão com o Tenable.io bem-sucedida!\n")
except Exception as e:
    print(f"Erro ao conectar com o Tenable.io: {e}")
    exit()

# --- 2. Listar as Credenciais (Versão Segura) ---
try:
    print("--- Buscando credenciais existentes no Tenable.io ---")
    
    credentials_list = tio.credentials.list()
    count = 0

    for cred in credentials_list:
        count += 1
        # Para diagnóstico, você pode descomentar a linha abaixo para ver a estrutura completa de cada item:
        print(f"DEBUG: {cred}")
        xdebug=(f"{cred}") # estou criando esa variavel para armazenar o que vem supostamente em formato JSON.
        dados_j=json.loads(xdebug) # Nesta variavel iremos fazer o load do JSON
        print(dados_j) # para debug.
        # --- MUDANÇA PRINCIPAL: Usando .get() para evitar erros ---
        # Se a chave 'name' não existir, ele mostrará 'Nome não encontrado'.
        cred_name = cred.get('name', 'Nome não encontrado')
        
        # Se a chave 'id' não existir, ele mostrará 'ID não disponível'.
        cred_id = cred.get('id', 'ID não disponível')
        
        # Se a chave 'type' não existir, ele mostrará 'Tipo desconhecido'.
        cred_type = cred.get('type', 'Tipo desconhecido')
        
        # O mesmo para a descrição.
        cred_desc = cred.get('description', '') # Retorna uma string vazia se não houver descrição

        print(f"Nome:        {cred_name}")
        print(f"ID:          {cred_id}")
        print(f"Tipo:        {cred_type}")
        if cred_desc:
            print(f"Descrição:   {cred_desc}")
        print("-" * 30)

    if count == 0:
        print("\nNenhuma credencial gerenciada foi encontrada.")
    else:
        print(f"\nTotal de {count} item(ns) encontrado(s).")

except Exception as e:
    print(f"Ocorreu um erro inesperado ao listar as credenciais: {e}")
