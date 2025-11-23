import re
import json
from tenable.io import TenableIO

# Substitua pelas suas credenciais da API do Tenable.io
ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'


def buscar_credencial_por_nome(nome_alvo):
    nome_alvo = nome_alvo.lower()
    todas_credenciais = tio.credentials.list()

    for cred in todas_credenciais:
        nome_cred = cred['name'].lower()
        if nome_alvo in nome_cred:
            print(f"✅ Credencial encontrada: {cred['name']} (ID: {cred['id']})")
            return cred['id']

    print(f"❌ Nenhuma credencial encontrada com o nome: {nome_alvo}")
    return None

credencial_id = buscar_credencial_por_nome('Valenet')

