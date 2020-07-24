#! bin/bash
KEY_NAME=${SA_NAME}_${PROJECT_ID}

# kill proxy process
ps | grep cloud_sql_proxy | awk '{print $1}' | xargs kill -9

#delete
private_key_id=$(
    cat ${KEY_NAME}.json | jq -r ".private_key_id"
)
echo yes | gcloud iam service-accounts keys delete ${private_key_id} \
  --iam-account ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

rm ${KEY_NAME}.json