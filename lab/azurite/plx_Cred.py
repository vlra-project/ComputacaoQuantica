from tenable.io import TenableIO
import time
# --- ATENÇÃO: Início da seção não recomendada ---
# Inserir suas chaves diretamente no código é um risco de segurança.
# Use este método com extrema cautela e apenas em ambientes controlados.
TENABLE_ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
TENABLE_SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'


# --- 1. Conexão com a API ---
try:
    tio = TenableIO(access_key=TENABLE_ACCESS_KEY, secret_key=TENABLE_SECRET_KEY)
    print("Conexão com o Tenable.io bem-sucedida!")
    print("=" * 50)
except Exception as e:
    print(f"Erro ao conectar com o Tenable.io: {e}")
    exit()

# --- 2. Processo de varredura e detalhamento ---
try:
    print("Iniciando varredura de todas as credenciais...\n")
    
    all_credentials_summaries = tio.credentials.list()
    
    credential_count = 0
    for cred_summary in all_credentials_summaries:
        credential_count += 1
        
        cred_name = cred_summary.get('name', 'Nome Desconhecido')
        cred_uuid = cred_summary.get('uuid')
        
        print(f"--- {credential_count}: Processando '{cred_name}' ---")
        
        if not cred_uuid:
            print("   [AVISO] Este item não possui um UUID. Pulando.")
            print("-" * 50 + "\n")
            continue
            
        print(f"   [List] UUID encontrado: {cred_uuid}")
        
        try:
            print("   [Details] Buscando informações detalhadas...")
            details = tio.credentials.details(cred_uuid)
            
            # =================================================================
            # AQUI ESTÁ A LÓGICA PARA PEGAR E EXIBIR O NOME DE USUÁRIO
            # Usamos .get() para não dar erro se a credencial não tiver um usuário (ex: SNMP)
            
            username_encontrado = details.get('username', 'N/A (Não aplicável para este tipo de credencial)')
            print(f"\n      >> USUÁRIO DA CREDENCIAL: {username_encontrado}\n")
            
            # =================================================================

            # Também imprimimos todos os outros detalhes para conferência
            print("      -- Detalhes Completos Retornados pela API --")
            for key, value in details.items():
                print(f"         -> {key}: {value}")
                
        except Exception as e:
            print(f"   [ERRO] Falha ao obter detalhes para o UUID {cred_uuid}: {e}")
        
        print("-" * 50 + "\n")
        time.sleep(0.5)

    if credential_count == 0:
        print("Nenhuma credencial foi encontrada na sua instância.")
    else:
        print(f"Processo concluído. {credential_count} credenciais foram varridas e detalhadas.")

except Exception as e:
    print(f"Ocorreu um erro geral durante a varredura: {e}")
