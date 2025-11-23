from tenable.io import TenableIO

# Substitua pelas suas chaves de API
ACCESS_KEY = "3be4e181ee86df569084ebfd6c42fb10596ddbca97380a408a8ce99c172ba825"
SECRET_KEY = "2008996ac516e0d7483574dd11e4a6d0a620d7d1456d26445871dcd9397b6924"

# Inicializa o cliente Tenable.io
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Lista os templates de scan
#templates = tio.editor.template_list('scan')
for scanner in tio.scanners.allowed_scanners():
    print(scanner)

# Exibe os templates
#print("Templates de Scan disponíveis:")
#for template in templates:
#    print(f"- {template['title']} (UUID: {template['uuid']})")
