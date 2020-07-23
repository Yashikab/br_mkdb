#! bin/bash

KEY_NAME=${SA_NAME}_${PROJECT_ID}
# create
gcloud iam service-accounts keys create ${KEY_NAME}.json \
  --iam-account ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

# install cloud sql proxy if it's not exist
if ! type ./cloud_sql_proxy
then
  wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
  chmod +x cloud_sql_proxy
fi

# access to cloud sql with proxy
./cloud_sql_proxy -instances=${PROJECT_ID}:us-central1:${GSQL_DATABASE}=tcp:3206 \
                  -credential_file=${KEY_NAME}.json &
