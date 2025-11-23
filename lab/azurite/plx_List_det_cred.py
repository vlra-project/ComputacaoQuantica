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

    # Usamos .list() para obter o iterador de todas as credenciais
    all_credentials_summaries = tio.credentials.list()

    credential_count = 0
    # Loop principal: para cada resumo de credencial encontrado pelo .list()
    for cred_summary in all_credentials_summaries:
        credential_count += 1

        # Pega o nome e o uuid do resumo inicial
        cred_name = cred_summary.get('name', 'Nome Desconhecido')
        cred_uuid = cred_summary.get('uuid')

        print(f"--- {credential_count}: Processando '{cred_name}' ---")

        # Verifica se o resumo continha um UUID antes de prosseguir
        if not cred_uuid:
            print("   [AVISO] Este item não possui um UUID. Pulando para o próximo.")
            print("-" * 50 + "\n")
            continue # Pula para a próxima iteração do loop

        print(f"   [List] UUID encontrado: {cred_uuid}")

        # Agora, usa o .details() para obter os dados completos
        try:
            print("   [Details] Buscando informações detalhadas...")
            # Chamada à API para obter os detalhes desta credencial específica
            details = tio.credentials.details(cred_uuid)

            # Imprime cada campo retornado pelo .details()
            for key, value in details.items():
                print(f"      -> {key}: {value}")

        except Exception as e:
            # Tratamento de erro caso a chamada .details() falhe para um UUID específico
            print(f"   [ERRO] Falha ao obter detalhes para o UUID {cred_uuid}: {e}")

        print("-" * 50 + "\n")
        time.sleep(0.5) # Pausa de meio segundo para não sobrecarregar a API com muitas chamadas rápidas

    if credential_count == 0:
        print("Nenhuma credencial foi encontrada na sua instância.")
    else:
        print(f"Processo concluído. {credential_count} credenciais foram varridas e detalhadas.")

except Exception as e:
    print(f"Ocorreu um erro geral durante a varredura: {e}")
