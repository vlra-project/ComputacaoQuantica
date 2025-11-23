from tenable.io import TenableIO

tio = TenableIO(access_key='a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9', secret_key='c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213')

# Listar os scans disponíveis
#for scan in tio.scans.list():
#    print(f"{scan['id']} - {scan['name']} ({scan['status']})")

#temp_uid = tio.policies.templates()
#print (temp_uid)

#temp_crendentials = tio.credentials.types()
#print (temp_credentials)

#scan = tio.scans.create(
#    name='Scan_test',
#   scanner= 'IT_BRAZIL_NEW',
#    template='VALE_SCAN_TEMPLATE',
#    targets=['scans.csv']
#)
#tio.scans.launch(scan['id'])
def read_inc_file():
    try:
        with open("inc.txt", "r") as file:
            lines = file.readlines()

        ip_value = None
        security_zone = None

        for line in lines:
            if "IP:" in line:
                ip_value = line.split(":")[1].strip()
#            elif "Security Zone:" in line:
#                security_zone = line.split(":")[1].strip()

        return ip_value

# Call the function to read the file and get the values
#ip, security_zone = read_inc_file()

#if ip and security_zone:
#    print(f"IP: {ip}")
#    print(f"Security Zone: {security_zone}")
#else:
#    print("Unable to retrieve the required values.")
