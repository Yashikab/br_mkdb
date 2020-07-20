# python 3.7.5
# coding: utf-8

from module.const import PROJECT_ID
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
project_id = PROJECT_ID

# ただsecretをテストする
secret_name = "just_a_test"
resource_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
response = client.access_secret_version(resource_name)
just_a_test = response.payload.data.decode('UTF-8')

if just_a_test == 'test1':
    print('OK')
else:
    print('Check again')
