# python 3.7.5
# coding: utf-8

from module.const import PROJECT_ID
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
project_id = PROJECT_ID
# ただsecretをテストする
secret_id = "just_a_test"

# Build the resource name of the parent project.
parent = client.project_path(project_id)

# Create the secret.
response = client.create_secret(parent, secret_id, {
    'replication': {
        'automatic': {},
    },
})

# Print the new secret name.
print('Created secret: {}'.format(response.name))





# # Build the resource name of the secret.
# name = client.secret_path(project_id, secret_id)

# # Get the current IAM policy.
# policy = client.get_iam_policy(name)

# print(policy)




# resource_name = f"projects/{project_id}/secrets/{secret_name}/versions/1"
# response = client.access_secret_version(resource_name)
# just_a_test = response.payload.data.decode('UTF-8')

# if just_a_test == 'test1':
#     print('OK')
# else:
#     print('Check again')
